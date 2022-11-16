error_hierarchy = {
    "BaseError": {
        "ConfigError": {
            "MissingKey": {},
        },
        "AnnouncementError": {
            "DataNotAvailable": {},
            "DataIntegrity": {},
            "CachedData": {},
            "OperationCanceled": {},
        },
        "ExchangeError": {
            "AuthenticationError": {
                "PermissionDenied": {},
                "AccountSuspended": {},
            },
            "ArgumentsRequired": {},
            "BadRequest": {
                "BadSymbol": {},
            },
            "BadResponse": {
                "NullResponse": {},
            },
            "InsufficientFunds": {},
            "InvalidAddress": {
                "AddressPending": {},
            },
            "InvalidOrder": {
                "OrderNotFound": {},
                "OrderNotCached": {},
                "CancelPending": {},
                "OrderImmediatelyFillable": {},
                "OrderNotFillable": {},
                "DuplicateOrderId": {},
            },
            "NotSupported": {},
        },
        "NetworkError": {
            "DDoSProtection": {
                "RateLimitExceeded": {},
            },
            "ExchangeNotAvailable": {
                "OnMaintenance": {},
            },
            "InvalidNonce": {},
            "RequestTimeout": {},
        },
    },
}


class BaseError(Exception):
    pass


class ConfigError(BaseError):
    pass


class MissingKey(ConfigError):
    pass


class AnnouncementError(BaseError):
    pass


class DataNotAvailable(AnnouncementError):
    pass


class CachedData(AnnouncementError):
    pass


class DataIntegrity(AnnouncementError):
    pass


class OperationCanceled(AnnouncementError):
    pass


class ExchangeError(BaseError):
    pass


class AuthenticationError(ExchangeError):
    pass


class PermissionDenied(AuthenticationError):
    pass


class AccountSuspended(AuthenticationError):
    pass


class ArgumentsRequired(ExchangeError):
    pass


class BadRequest(ExchangeError):
    pass


class BadSymbol(BadRequest):
    pass


class BadResponse(ExchangeError):
    pass


class NullResponse(BadResponse):
    pass


class InsufficientFunds(ExchangeError):
    pass


class InvalidAddress(ExchangeError):
    pass


class AddressPending(InvalidAddress):
    pass


class InvalidOrder(ExchangeError):
    pass


class OrderNotFound(InvalidOrder):
    pass


class OrderNotCached(InvalidOrder):
    pass


class CancelPending(InvalidOrder):
    pass


class OrderImmediatelyFillable(InvalidOrder):
    pass


class OrderNotFillable(InvalidOrder):
    pass


class DuplicateOrderId(InvalidOrder):
    pass


class NotSupported(ExchangeError):
    pass


class NetworkError(BaseError):
    pass


class DDoSProtection(NetworkError):
    pass


class RateLimitExceeded(DDoSProtection):
    pass


class ExchangeNotAvailable(NetworkError):
    pass


class OnMaintenance(ExchangeNotAvailable):
    pass


class InvalidNonce(NetworkError):
    pass


class RequestTimeout(NetworkError):
    pass


__all__ = [
    "error_hierarchy",
    "BaseError",
    "ConfigError",
    "MissingKey",
    "AnnouncementError",
    "DataIntegrity",
    "CachedData",
    "OperationCanceled",
    "ExchangeError",
    "AuthenticationError",
    "PermissionDenied",
    "AccountSuspended",
    "ArgumentsRequired",
    "BadRequest",
    "BadSymbol",
    "BadResponse",
    "NullResponse",
    "InsufficientFunds",
    "InvalidAddress",
    "AddressPending",
    "InvalidOrder",
    "OrderNotFound",
    "OrderNotCached",
    "CancelPending",
    "OrderImmediatelyFillable",
    "OrderNotFillable",
    "DuplicateOrderId",
    "NotSupported",
    "NetworkError",
    "DDoSProtection",
    "RateLimitExceeded",
    "ExchangeNotAvailable",
    "OnMaintenance",
    "InvalidNonce",
    "RequestTimeout",
]
