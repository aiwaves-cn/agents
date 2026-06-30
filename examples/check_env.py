import os


REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "OPENAI_API_BASE",
    "OPENAI_MODEL_NAME",
]


def main() -> int:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]

    if missing:
        print("Missing required environment variables:")
        for name in missing:
            print(f"- {name}")
        print("\nPlease configure them before running agent examples.")
        print("Do not commit real API keys or .env files to Git.")
        return 1

    print("Environment check passed.")
    print("Required model configuration variables are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
