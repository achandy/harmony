"""
Custom exception classes for the Harmony application.

This module defines specific exception types for better error handling
and debugging throughout the application.
"""


class HarmonyError(Exception):
    """Base exception class for all Harmony-related errors."""
    pass


class AuthenticationError(HarmonyError):
    """Raised when authentication with a music service fails."""
    pass


class APIError(HarmonyError):
    """Raised when API requests to music services fail."""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class ConfigurationError(HarmonyError):
    """Raised when there are issues with application configuration."""
    pass


class PlaylistSyncError(HarmonyError):
    """Raised when playlist synchronization fails."""
    pass


class TrackSearchError(HarmonyError):
    """Raised when track search operations fail."""
    pass