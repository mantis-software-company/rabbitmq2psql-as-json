import aio_pika
import asyncio
import psycopg2
from aio_pika.pool import Pool


async def consume(loop, sql_template, config, consumer_pool_size=10):
    db_conn = psycopg2.connect(
        host=config.get("db_host"),
        user=config.get("db_user"),
        password=config.get("db_pass"),
        database=config.get("db_database"),
        port=config.get("db_port")
    )

    db_conn.autocommit = True

    cursor = db_conn.cursor()

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
                config.get("mq_queue"), durable=False, auto_delete=False
            )

            while True:
                try:
                    m = await queue.get(timeout=5 * consumer_pool_size)
                    message = m.body.decode('utf-8')
                    try:
                        cursor.execute(sql_template, (message,))
                    except Exception as e:
                        raise e
                    else:
                        m.ack()
                except aio_pika.exceptions.QueueEmpty:
                    break

    async with connection_pool, channel_pool:
        consumer_pool = []
        for i in range(consumer_pool_size):
            consumer_pool.append(_consume())

        await asyncio.gather(*consumer_pool)
