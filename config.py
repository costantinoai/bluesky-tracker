import os

class Config:
    # Bluesky account to track (public profile)
    # Note: handle should NOT include @ symbol
    # REQUIRED: Set this in your .env file
    BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE', 'your-handle.bsky.social')
    
    # Optional: App Password for authenticated access (recommended)
    # Generate at: https://bsky.app/settings/app-passwords
    # More secure than main password, can be revoked anytime
    BLUESKY_APP_PASSWORD = os.getenv('BLUESKY_APP_PASSWORD', '').strip()
    
    # Determine if we have authentication
    HAS_AUTH = bool(BLUESKY_APP_PASSWORD)

    # API settings
    BLUESKY_API_URL = 'https://public.api.bsky.app'  # Public API with caching
    BLUESKY_AUTH_API_URL = 'https://bsky.social'      # Authenticated API
    REQUEST_DELAY = 0.7  # Seconds between API calls
    MAX_RETRIES = 3

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/bluesky.db')

    # Scheduler
    COLLECTION_TIME = '06:00'  # 6 AM Europe/Brussels
    TIMEZONE = 'Europe/Brussels'

    # Flask
    PORT = int(os.getenv('PORT', 8095))

    # Display settings
    WIDGET_DAYS = 30  # Show last 30 days in widget
    
    @classmethod
    def is_authenticated(cls):
        """Check if authentication is configured"""
        return cls.HAS_AUTH
    
    @classmethod
    def get_api_url(cls):
        """Get appropriate API URL based on auth status"""
        return cls.BLUESKY_AUTH_API_URL if cls.HAS_AUTH else cls.BLUESKY_API_URL
