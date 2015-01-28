class IobError(Exception):
    """
    Base exception class for all iob-related exceptions.
    """


class UnknownTaskType(IobError):
    """
    Raised when Iob does not know what to do
    with some objects received from generator.
    """


class RequestConfigurationError(IobError):
    """
    Raised when Request object is instantiating with
    invalid parameters.
    """
