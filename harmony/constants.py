"""
Constants used throughout the Harmony application.

This module centralizes all magic numbers and configuration values
to improve maintainability and avoid hardcoded values scattered
throughout the codebase.
"""

# Server Configuration
LOCALHOST_PORT = 8888
LOCALHOST_HOST = "localhost"
REDIRECT_URI = f"http://{LOCALHOST_HOST}:{LOCALHOST_PORT}/callback"

# API Limits - Default values for API requests
DEFAULT_SEARCH_LIMIT = 10
DEFAULT_PLAYLIST_LIMIT_SPOTIFY = 50
DEFAULT_PLAYLIST_LIMIT_APPLE_MUSIC = 100
DEFAULT_TRACK_LIMIT = 100
EXPANDED_SEARCH_LIMIT = 5  # For fallback searches

# Authentication
JWT_EXPIRY_HOURS = 12

# Logging Configuration
MAX_LOG_FILES = 5
KEEP_LOG_FILES = 4
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Similarity Matching Thresholds
PLAYLIST_NAME_SIMILARITY_THRESHOLD = 0.8
TRACK_NAME_SIMILARITY_THRESHOLD = 0.75
ARTIST_SIMILARITY_THRESHOLD = 0.5
COMBINED_SIMILARITY_THRESHOLD = 0.7

# Similarity Weights
TRACK_NAME_WEIGHT = 0.6
ARTIST_NAME_WEIGHT = 0.4

# Text Processing
THE_PREFIX_LENGTH = 4  # Length of "the " prefix to remove from artist names
