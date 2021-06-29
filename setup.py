import setuptools

setuptools.setup(
    name="rabbitmq2psql-as-json",
    version="0.0.0",
    author="Furkan Kalkan",
    author_email="furkankalkan@mantis.com.tr",
    description="Asynchronous RabbitMQ consumer job library for PostgreSQL",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="all",
    url="https://github.com/mantis-software-company/rabbitmq2psql-as-json",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
	"Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    install_requires=['aiopg', 'aio_pika'],
    python_requires=">3.6.*, <4",
    packages=['rabbitmq2psql_as_json'],
    scripts=['bin/rabbitmq2psql-as-json']
)
