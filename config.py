# MYSQL Connection
MYSQL_USER = 'markuser'
MYSQL_PASSWORD = '12345678'
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'mark'

INVALID_TOKEN_MESSAGE = 'Invalid token passed'
UNAUTHORIZED_ACCESS_MESSAGE = 'Unauthorized access'
LINK_NOT_FOUND_MESSAGE = 'Link is not found'
AUTHORIZATION_TOKEN = 'd4SjCgRP35p55IsGHVWpTSBAIHusQmcS'

ERROR_LOG_FILENAME = "pictures-errors.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:%(name)s:%(process)d:%(lineno)d " "%(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": ERROR_LOG_FILENAME,
            "formatter": "default",
            "backupCount": 2,
        },
        "verbose_output": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "tryceratops": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
        },
    },
    "root": {"level": "INFO", "handlers": ["logfile"]},
}
