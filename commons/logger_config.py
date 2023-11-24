import logging

# Create a logger

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

DICTIONARY_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "%(message)s",
        },
        "standard": {
            # "format": '{"user_id": "AnonymousUser","request_id":"%(request_id)s","level":"%(levelname)s","datetime":"%(asctime)s","service":"%(name)s","message":"%(message)s","filename":"%(filename)s","module":"%(module)s","func_name":"%(funcName)s","line_no":"%(lineno)d","path_name":"%(pathname)s"}'
            "format": '{"user_id": "AnonymousUser","level":"%(levelname)s","datetime":"%(asctime)s","service":"%(name)s","message":"%(message)s","filename":"%(filename)s","module":"%(module)s","func_name":"%(funcName)s","line_no":"%(lineno)d","path_name":"%(pathname)s"}'
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "standard",
        },
    },
    "root": {
        "level": "INFO",
        # 'handlers': ['wsgi','file.handler']
        "handlers": ["wsgi"],
    },
}
