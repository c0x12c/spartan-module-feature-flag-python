# core/exceptions.py

class FeatureFlagError(Exception):
    """Base exception for feature flag errors."""


class FeatureFlagNotFoundError(FeatureFlagError):
    """Raised when a feature flag is not found."""


class FeatureFlagValidationError(FeatureFlagError):
    """Raised when feature flag data fails validation."""


class FeatureFlagCacheError(FeatureFlagError):
    """Raised when there's an error with the feature flag cache."""


class FeatureFlagDatabaseError(FeatureFlagError):
    """Raised when there's a database error related to feature flags."""


class CacheError(Exception):
    """Custom exception for cache-related errors."""
    pass
