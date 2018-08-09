class CrawlerError(Exception):
    """
    Base exception class for all crawler-related exceptions.
    """


class RequestConfigurationError(CrawlerError):
    """
    Raised when Request object is instantiating with
    invalid parameters.
    """


class NetworkError(CrawlerError):
    def __init__(self, msg, original_exc):
        super(NetworkError, self).__init__(msg, original_exc)
        self.original_exc = original_exc


class BadStatusCode(CrawlerError):
    pass
