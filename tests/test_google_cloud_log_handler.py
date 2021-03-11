import unittest
import logging
import logging.config
from datetime import datetime


class TestTheProjectMethods(unittest.TestCase):
    def test_get_hello_world_methods(self):
        logging.config.dictConfig(default_with_google_cloud_logging_format_1())
        # build the logger
        logger = logging.getLogger("my-log")
        logger.setLevel(logging.INFO)
        data = {"data": "{'field1': 'test1', 'field2': 'test2'}"}
        logger.info(f"Hello, world! {datetime.now()}", extra=data)


def default_with_google_cloud_logging_format_1():
    return {
            "version": 1,
            "disable_existing_loggers": "false",
            "formatters": {
                "default-single-line": {
                    "style": "{",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "{{\"message\":\"{message:s}\",\"data\":\"{data:s}\"}}"
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "default-single-line",
                    "stream": "ext://sys.stdout"
                },
                "googlecloud": {
                    "level": "DEBUG",
                    "class": "zeppos_log_handler_google_cloud.GoogleCloudLogHandler",
                    "formatter": "default-single-line",
                    "project": "sandbox"
                }
            },
            "loggers": {},
            "root": {
                "handlers": ["console", "googlecloud"],
            }
        }


if __name__ == '__main__':
    unittest.main()
