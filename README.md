# rabbitmq2psql-as-json

rabbitmq2psql-as-json is ready to use, basic asynchronous RabbitMQ consumer job library for PostgreSQL. It stops when queue is empty, so it can be useful for cron jobs, unit tests, CI/CD environments and production environments has slow datastream.

## Installation

You can install this library easily with pip.
`pip install rabbitmq2psql-as-json` 

## Usage
### As a library
```py
import os
import asyncio
import logging
from rabbitmq2psql_as_json import consume

if __name__ == '__main__':
    logger = logging.getLogger("rabbitmq2psql-as-json")
    logger.setLevel(os.environ.get('LOG_LEVEL', "DEBUG"))
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            os.environ.get('LOG_FORMAT', "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
    )
    logger.addHandler(handler)

    config = {
      "mq_host": os.environ.get('MQ_HOST'),
	  "mq_port": int(os.environ.get('MQ_PORT')), 
	  "mq_vhost": os.environ.get('MQ_VHOST'),
	  "mq_user": os.environ.get('MQ_USER'),
	  "mq_pass": os.environ.get('MQ_PASS'),
	  "mq_queue": os.environ.get('MQ_QUEUE'),
      "mq_exchange": os.environ.get('MQ_EXCHANGE'),
      "mq_routing_key": os.environ.get('MQ_ROUTING_KEY'),
	  "db_host": os.environ.get('DB_HOST'),
	  "db_port": int(os.environ.get('DB_PORT')),
	  "db_user": os.environ.get('DB_USER'),
	  "db_pass": os.environ.get('DB_PASS'),
	  "db_database": os.environ.get('DB_DATABASE') 
    }
  
    sql_template = """insert into logs (body) values (%s);""" 
  
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        consume(
          loop=loop,
          consumer_pool_size=10,
          sql_template=sql_template,
          config=config
        )
    )

loop.close()
```

This library uses [aio_pika](https://aio-pika.readthedocs.io/en/latest/) and [aiopg](https://aiopg.readthedocs.io/en/stable/) packages.

### Standalone
You can also call this library as standalone consumer job command.  Just set required environment variables and run `rabbitmq2psql-as-json`. This usecase perfectly fits when you need run it on cronjobs or kubernetes jobs. 

**Required environment variables:**
- MQ_HOST
- MQ_PORT (optional)
- MQ_VHOST
- MQ_USER
- MQ_PASS
- MQ_QUEUE
- MQ_QUEUE_DURABLE (optional, default value: True)
- MQ_EXCHANGE (Exchange for dead letter queue, aka records with error queue)
- MQ_ROUTING_KEY (Routing key for dead letter queue)
- DB_HOST
- DB_PORT (optional)
- DB_USER
- DB_PASS
- DB_DATABASE
- SQL_TEMPLATE (DB Insert query template. Ex: `insert into logs (body) values (%s);`)
- CONSUMER_POOL_SIZE (optional, default value: 10)
- LOG_LEVEL (Logging level. See: [Python logging module docs](https://docs.python.org/3/library/logging.html#logging-levels))

**Example Kubernetes job:** 
 You can see it to [kube.yaml](kube.yaml)


