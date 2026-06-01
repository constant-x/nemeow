import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from main import build_parser, main, print_statistics


def write_config(tmp_path):
    config = {
        "min_score": 2,
        "unknown": {"folder": "10_unknown_unclassified"},
        "quarantine": {
            "empty": {"folder": "90_quarantine_empty"},
            "unsupported_format": {"folder": "91_quarantine_unsupported"},
            "corrupted": {"folder": "92_quarantine_corrupted"},
            "decode_error": {"folder": "93_quarantine_decode_error"},
        },
        "categories": [
            {
                "folder": "03_access_requests",
                "priority": 80,
                "strong_keywords": ["выдать доступ"],
                "keywords": ["vpn"],
            }
        ],
    }
    config_path = tmp_path / "categories.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    return config_path


def test_build_parser_uses_project_root_defaults(tmp_path):
    parser = build_parser(tmp_path)
    args = parser.parse_args([])

    assert args.inbox == str(tmp_path / "inbox")
    assert args.processed == str(tmp_path / "processed")
    assert args.logs == str(tmp_path / "logs")
    assert args.config == str(tmp_path / "categories.json")


def test_print_statistics_outputs_total_and_sorted_categories(capsys):
    print_statistics(
        {
            "11_info_news": 1,
            "03_access_requests": 2,
            "10_unknown_unclassified": 1,
        }
    )

    output = capsys.readouterr().out
    assert "Processing completed successfully" in output
    assert "Total processed: 4" in output

    lines = output.splitlines()
    assert lines[2:] == [
        "03_access_requests: 2",
        "10_unknown_unclassified: 1",
        "11_info_news: 1",
    ]


def test_main_processes_custom_directories(tmp_path, capsys):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    logs = tmp_path / "logs"
    inbox.mkdir()
    (inbox / "access.txt").write_text(
        "Прошу выдать доступ к VPN",
        encoding="utf-8",
    )
    config_path = write_config(tmp_path)

    exit_code = main(
        [
            "--inbox",
            str(inbox),
            "--processed",
            str(processed),
            "--logs",
            str(logs),
            "--config",
            str(config_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Total processed: 1" in output
    assert (processed / "03_access_requests" / "access.txt").exists()


def test_main_returns_error_when_processing_fails(tmp_path, capsys):
    config_path = write_config(tmp_path)

    exit_code = main(
        [
            "--inbox",
            str(tmp_path / "missing-inbox"),
            "--processed",
            str(tmp_path / "processed"),
            "--logs",
            str(tmp_path / "logs"),
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Processing failed: Inbox folder not found" in captured.err
