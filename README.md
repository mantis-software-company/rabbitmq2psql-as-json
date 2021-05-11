# rabbitmq2psql-as-json

rabbitmq2psql-as-json is ready to use, basic asynchronous RabbitMQ consumer job library for PostgreSQL. It stops when queue is empty, so it can be useful for cron jobs, unit tests, CI/CD environments and production environments has slow datastream.

## Usage
```py
import os
import asyncio
from rabbitmq2psql-as-json import consume

if __name__ == '__main__':  
    config = {  
      "mq_host": os.environ.get('MQ_HOST'),  
	  "mq_port": int(os.environ.get('MQ_PORT')),  
	  "mq_vhost": os.environ.get('MQ_VHOST'),  
	  "mq_user": os.environ.get('MQ_USER'),  
	  "mq_pass": os.environ.get('MQ_PASS'),  
	  "mq_queue": os.environ.get('MQ_QUEUE'),  
	  "db_host": os.environ.get('DB_HOST'),  
	  "db_port": int(os.environ.get('DB_PORT')),  
	  "db_user": os.environ.get('DB_USER'),  
	  "db_pass": os.environ.get('DB_PASS'),  
	  "db_database": os.environ.get('DB_DATABASE')  
    }  
  
sql_template = """insert into logs (body) values (%s);"""  
  
loop = asyncio.get_event_loop()  
loop.run_until_complete(
	consume(loop=loop, consumer_pool_size=10, sql_template=sql_template, config=config)
)  
loop.close()
```
