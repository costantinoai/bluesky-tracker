import os
import sys


class Config:
    # Bluesky account to track
    # Note: handle should NOT include @ symbol
    # REQUIRED: Set this in your .env file
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE", "")

    # OPTIONAL: App Password for authenticated access
    # Only needed for: interactions (who liked/replied to you)
    # Generate at: https://bsky.app/settings/app-passwords
    # Most features work WITHOUT this!
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD", "").strip()

    # Computed: Is authentication enabled?
    # True if app password is provided, False otherwise
    AUTH_ENABLED = bool(BLUESKY_APP_PASSWORD)

    # Features that require authentication
    AUTH_REQUIRED_FEATURES = ["interactions"]  # Only interactions needs auth now

    # Validate required configuration
    @classmethod
    def validate(cls):
        """Validate required configuration on startup"""
        errors = []

        if not cls.BLUESKY_HANDLE or cls.BLUESKY_HANDLE == "your-handle.bsky.social":
            errors.append("BLUESKY_HANDLE is required. Set it in your .env file.")

        if errors:
            print("\n" + "=" * 70, file=sys.stderr)
            print("CONFIGURATION ERROR", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            for error in errors:
                print(f"  ✗ {error}", file=sys.stderr)
            print(
                "\nPlease update your .env file with the required values.",
                file=sys.stderr,
            )
            print("=" * 70 + "\n", file=sys.stderr)
            sys.exit(1)

        # Show auth status (not an error, just info)
        if cls.AUTH_ENABLED:
            print("Authentication: ENABLED (all features available)")
        else:
            print("Authentication: DISABLED (interactions feature unavailable)")
            print("  To enable: Set BLUESKY_APP_PASSWORD in your .env file")

    # API settings
    BLUESKY_API_URL = "https://bsky.social"  # For authenticated requests
    PUBLIC_API_URL = "https://public.api.bsky.app"  # For public requests (no auth)
    PLC_DIRECTORY_URL = "https://plc.directory"  # For DID resolution
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.7"))  # Seconds between API calls
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "0.5"))
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "30"))
    CAR_DOWNLOAD_TIMEOUT = int(os.getenv("CAR_DOWNLOAD_TIMEOUT", "120"))

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/bluesky.db")

    # Scheduler
    COLLECTION_TIME = os.getenv("COLLECTION_TIME", "06:00")  # Default: 6 AM
    TIMEZONE = os.getenv("TZ", os.getenv("TIMEZONE", "Europe/Brussels"))

    # Flask
    PORT = int(os.getenv("PORT", 8095))

    # Display settings
    WIDGET_DAYS = 30  # Show last 30 days in widget
