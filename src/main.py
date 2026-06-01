import argparse
import logging
import sys
from pathlib import Path

from processor import MailProcessor


def build_parser(project_root):
    parser = argparse.ArgumentParser(
        description="Process and classify corporate mail files.",
    )
    parser.add_argument(
        "--inbox",
        default=str(project_root / "inbox"),
        help="Folder with incoming mail files.",
    )
    parser.add_argument(
        "--processed",
        default=str(project_root / "processed"),
        help="Folder where classified mail files will be moved.",
    )
    parser.add_argument(
        "--logs",
        default=str(project_root / "logs"),
        help="Folder for processing logs.",
    )
    parser.add_argument(
        "--config",
        default=str(project_root / "categories.json"),
        help="Path to categories configuration.",
    )
    return parser


def print_statistics(statistics):
    total = sum(statistics.values())
    print("Processing completed successfully")
    print(f"Total processed: {total}")

    for category, count in statistics.items():
        print(f"{category}: {count}")


def main(argv=None):
    project_root = Path(__file__).resolve().parents[1]
    parser = build_parser(project_root)
    args = parser.parse_args(argv)

    processor = MailProcessor(
        inbox_dir=args.inbox,
        processed_dir=args.processed,
        log_dir=args.logs,
        config_path=args.config,
    )

    try:
        statistics = processor.process_all()
    except Exception as error:
        print(f"Processing failed: {error}", file=sys.stderr)
        return 1
    finally:
        logging.shutdown()

    print_statistics(statistics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
