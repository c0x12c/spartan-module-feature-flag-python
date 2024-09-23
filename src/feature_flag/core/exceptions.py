# core/exceptions.py


class FeatureFlagError(Exception):
    """Base exception for feature flag errors."""


class FeatureFlagNotFoundError(FeatureFlagError):
    """Raised when a feature flag is not found."""


class NotifierError(Exception):
    """Base exception for notifier errors."""
