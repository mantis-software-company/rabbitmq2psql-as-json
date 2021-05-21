import aio_pika
import aiopg
import asyncio
import json
import os
from aio_pika.pool import Pool
from distutils.util import strtobool


async def consume(loop, sql_template=None, logger=None, config=None, consumer_pool_size=10):
    if config is None:
        config = {
            "mq_host": os.environ.get('MQ_HOST'),
            "mq_port": int(os.environ.get('MQ_PORT', '5672')),
            "mq_vhost": os.environ.get('MQ_VHOST'),
            "mq_user": os.environ.get('MQ_USER'),
            "mq_pass": os.environ.get('MQ_PASS'),
            "mq_queue": os.environ.get('MQ_QUEUE'),
            "mq_queue_durable": bool(strtobool(os.environ.get('MQ_QUEUE_DURABLE', 'True'))),
            "db_host": os.environ.get('DB_HOST'),
            "db_port": int(os.environ.get('DB_PORT', '5432')),
            "db_user": os.environ.get('DB_USER'),
            "db_pass": os.environ.get('DB_PASS'),
            "db_database": os.environ.get('DB_DATABASE'),
            "consumer_pool_size": os.environ.get("CONSUMER_POOL_SIZE"),
            "sql_template": os.environ.get('SQL_TEMPLATE')
        }

    if sql_template is None:
        sql_template = config.get("sql_template")

    if "consumer_pool_size" in config:
        if config.get("consumer_pool_size"):
            try:
                consumer_pool_size = int(config.get("consumer_pool_size"))
            except TypeError as e:
                if logger:
                    logger.error("Invalid pool size: %s" % (consumer_pool_size,))
                raise e

    db_pool = await aiopg.create_pool(
        host=config.get("db_host"),
        user=config.get("db_user"),
        password=config.get("db_pass"),
        database=config.get("db_database"),
        port=config.get("db_port"),
        minsize=consumer_pool_size,
        maxsize=consumer_pool_size * 2
    )

    async def get_connection():
        return await aio_pika.connect(
            host=config.get("mq_host"),
            port=config.get("mq_port"),
            login=config.get("mq_user"),
            password=config.get("mq_pass"),
            virtualhost=config.get("mq_vhost"),
            loop=loop
        )

    connection_pool = Pool(get_connection, max_size=consumer_pool_size, loop=loop)

    async def get_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool = Pool(get_channel, max_size=consumer_pool_size, loop=loop)

    async def _consume():
        async with channel_pool.acquire() as channel:
            queue = await channel.declare_queue(
                config.get("mq_queue"), durable=config.get("mq_queue_durable"), auto_delete=False
            )

            db_conn = await db_pool.acquire()
            cursor = await db_conn.cursor()

            while True:
                try:
                    m = await queue.get(timeout=5 * consumer_pool_size)
                    message = m.body.decode('utf-8')
                    if logger:
                        logger.debug("Message %s inserting to db" % (json.loads(message),))
                    try:
                        await cursor.execute(sql_template, (message,))
                    except Exception as e:
                        if logger:
                            logger.error("DB Error: %s" % (e,))
                        await db_conn.close()
                        raise e
                    else:
                        m.ack()
                except aio_pika.exceptions.QueueEmpty:
                    db_conn.close()
                    if logger:
                        logger.info("Queue empty. Stopping.")
                    break

    async with connection_pool, channel_pool:
        consumer_pool = []
        if logger:
            logger.info("Consumers started")
        for _ in range(consumer_pool_size):
            consumer_pool.append(_consume())

        await asyncio.gather(*consumer_pool)

