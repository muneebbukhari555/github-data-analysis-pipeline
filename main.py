import argparse
import sys
from config.settings import Settings


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Pipeline Analysis - MSc Project"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "collect", "analyze"],
        default="full",
        help="Pipeline execution mode (default: full)"
    )
    parser.add_argument(
        "--repos",
        nargs="*",
        help="Optional: specific repos to analyze (e.g., pytorch/pytorch)"
    )
    args = parser.parse_args()

    settings = Settings()
    logger = settings.get_logger("main")
    logger.info("GitHub Pipeline Analysis starting in '%s' mode", args.mode)

if __name__ == "__main__":
    main()