class CrawlerError(Exception):
    """
    Base exception class for all crawler-related exceptions.
    """


class CrawlerNetworkError(CrawlerError):
    def __init__(self, msg, original_exc):
        super(CrawlerNetworkError, self).__init__(msg, original_exc)
        self.original_exc = original_exc


class CrawlerBadStatusCode(CrawlerError):
    pass


class CrawlerFatalError(CrawlerError):
    """Raised in case of unrecovery internal error."""
