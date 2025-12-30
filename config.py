import os
import sys


class Config:
    # Bluesky account to track
    # Note: handle should NOT include @ symbol
    # REQUIRED: Set this in your .env file
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE", "")

    # REQUIRED: App Password for authenticated access
    # Generate at: https://bsky.app/settings/app-passwords
    # More secure than main password, can be revoked anytime
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD", "").strip()

    # Validate required configuration
    @classmethod
    def validate(cls):
        """Validate required configuration on startup"""
        errors = []

        if not cls.BLUESKY_HANDLE or cls.BLUESKY_HANDLE == "your-handle.bsky.social":
            errors.append("BLUESKY_HANDLE is required. Set it in your .env file.")

        if not cls.BLUESKY_APP_PASSWORD:
            errors.append(
                "BLUESKY_APP_PASSWORD is required. Generate one at https://bsky.app/settings/app-passwords"
            )

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

    # API settings
    BLUESKY_API_URL = "https://bsky.social"  # Always use authenticated API
    REQUEST_DELAY = 0.7  # Seconds between API calls
    MAX_RETRIES = 3

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/bluesky.db")

    # Scheduler
    COLLECTION_TIME = "06:00"  # 6 AM Europe/Brussels
    TIMEZONE = "Europe/Brussels"

    # Flask
    PORT = int(os.getenv("PORT", 8095))

    # Display settings
    WIDGET_DAYS = 30  # Show last 30 days in widget
