import logging

"""
These variables are checked by various parts of the application to make sure that areas that are capable of producing
a great number of log messages only produce a certain amount.
"""
imgur_client_error_log_count = 0
modified_date_log_count = 0


def log_proxy(class_name, level, message=None, exc_info=False, **kwargs):
    """
    This method is used to log from classes that cannot have a log instance.

    Some classes in this application need to be pickled.  The logger instance when created is not able to be pickled.
    This method is used to log from classes that are not allowed to have a logger instance of their own due to the
    pickling requirement.  The arguments supplied to this method will be the same as the arguments supplied to a logger
    instance, this class is used only as a proxy.

    :param class_name: The name of the class that the log message is being sent from.
    :param level: The severity level of the log message.
    :param message: The message that is to be logged.
    :param exc_info: True if the current exception being handled is to be logged, False if not.
    :param kwargs: Any parameters to be entered into the log message as extra.
    :type class_name: str
    :type level: str
    :type message: str
    :type exc_info: bool
    """
    logger = logging.getLogger('DownloaderForReddit.%s' % class_name)
    log_dict = {'DEBUG': logger.debug, 'INFO': logger.info, 'WARNING': logger.warning, 'ERROR': logger.error}
    log_dict[level](message, extra=kwargs, exc_info=exc_info)
