import logging
import ast
from google.cloud.logging_v2.handlers.transports import BackgroundThreadTransport
from google.cloud.logging_v2.logger import _GLOBAL_RESOURCE
from google.cloud.logging import Client
# This class (GoogleCloudLogHandler) has to be in the __init__. Otherwise it will not work with the json logging
# config as specified in the README.md


class GoogleCloudLogHandler(logging.StreamHandler):
    """Handler that directly makes Cloud Logging API calls.
    This is a Python standard ``logging`` handler using that can be used to
    route Python standard logging messages directly to the Stackdriver Logging API.
    This handler is used when not in GAE or GKE environment.
    This handler supports both an asynchronous and synchronous transport.
    """

    def __init__(
            self,
            project,
            *,
            log_name="python",
            transport=BackgroundThreadTransport,
            resource=_GLOBAL_RESOURCE,
            labels=None,
            stream=None,
    ):
        """
        Args:
            project (str):
                The name of the project the information will be logged to.
            log_name (str): the name of the custom log in Cloud Logging.
                Defaults to 'python'. The name of the Python logger will be represented
                in the ``python_logger`` field.
            transport (~logging_v2.transports.Transport):
                Class for creating new transport objects. It should
                extend from the base :class:`.Transport` type and
                implement :meth`.Transport.send`. Defaults to
                :class:`.BackgroundThreadTransport`. The other
                option is :class:`.SyncTransport`.
            resource (~logging_v2.resource.Resource):
                Resource for this Handler. Defaults to ``GLOBAL_RESOURCE``.
            labels (Optional[dict]): Monitored resource of the entry, defaults
                to the global resource type.
            stream (Optional[IO]): Stream to be used by the handler.
        """
        super(GoogleCloudLogHandler, self).__init__(stream)
        _client = Client(project=project)

        self.log_name = log_name
        self.transport = transport(_client, log_name)
        self.project_id = _client.project
        self.resource = resource
        self.labels = labels

    def emit(self, record):
        """Actually log the specified logging record.
        Overrides the default emit behavior of ``StreamHandler``.
        See https://docs.python.org/2/library/logging.html#handler-objects
        Args:
            record (logging.LogRecord): The record to be logged.
        """

        self.transport.send(
            record,
            record.getMessage(),
            info=self._get_info_dict(record=record),
            resource=GoogleCloudLogHandler._get_resource(record=record, resource=self.resource),
            labels=GoogleCloudLogHandler._get_labels(record=record, labels=self.labels),
            trace=GoogleCloudLogHandler._get_trace(record=record),
            span_id=GoogleCloudLogHandler._get_span_id(record=record),
            http_request=GoogleCloudLogHandler._get_http_request(record=record),
        )

    def _get_info_dict(self, record):
        try:
            info_dict = ast.literal_eval(super(GoogleCloudLogHandler, self).format(record))
            info_dict = {**info_dict, **self._get_info_dict_log_record_data(record=record)}
            if "data" in info_dict:
                data_dict = ast.literal_eval(info_dict["data"])
                info_dict.pop("data", None)
                info_dict = {**info_dict, **data_dict}
            return info_dict
        except Exception as error:
            print(f"error in _get_info_dict: {error}")
            return {}

    def _get_info_dict_log_record_data(self, record):
        return {
            "filename": getattr(record, "filename", None),
            "funcName": getattr(record, "funcName", None),
            "level_name": getattr(record, "levelname", None),
            "level_no": getattr(record, "levelno", None),
            "line_no": getattr(record, "lineno", None),
            "module": getattr(record, "module", None),
            "logger_name": getattr(record, "name", None),
            "pathname": getattr(record, "pathname", None),
            "client_ip": getattr(record, "client_ip", None),
            "host_name": getattr(record, "host_name", None),
        }

    @staticmethod
    def _get_resource(record, resource):
        return getattr(record, "resource", resource)

    @staticmethod
    def _get_labels(record, labels):
        user_labels = getattr(record, "labels", {})

        total_labels = labels if labels is not None else {}
        total_labels.update(user_labels)
        if len(total_labels) == 0:
            total_labels = None
        return total_labels if total_labels else None

    @staticmethod
    def _get_trace(record):
        return getattr(record, "trace", None)

    @staticmethod
    def _get_span_id(record):
        return getattr(record, "span_id", None)

    @staticmethod
    def _get_http_request(record):
        return getattr(record, "http_request", None)

