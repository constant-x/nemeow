import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from processor import MailProcessor


def create_processor(tmp_path):
    return MailProcessor(
        inbox_dir=str(tmp_path / "inbox"),
        processed_dir=str(tmp_path / "processed"),
        log_dir=str(tmp_path / "logs"),
    )


def test_read_mail_reads_text_file(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    file_path = inbox / "mail.txt"
    file_path.write_text("Ошибка при входе в VPN", encoding="utf-8")
    processor = create_processor(tmp_path)

    mail = processor.read_mail(str(file_path))

    assert mail.filename == "mail.txt"
    assert mail.text == "Ошибка при входе в VPN"


def test_read_mail_rejects_unsupported_file_format(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    file_path = inbox / "mail.json"
    file_path.write_text("{}", encoding="utf-8")
    processor = create_processor(tmp_path)

    with pytest.raises(ValueError):
        processor.read_mail(str(file_path))


def test_process_all_moves_text_mail_to_classified_folder(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "incident.txt").write_text(
        "[CRITICAL] Сервис недоступен, возвращает ошибка 500",
        encoding="utf-8",
    )
    processor = create_processor(tmp_path)

    statistics = processor.process_all()

    assert statistics["02_critical_incidents"] == 1
    assert not (inbox / "incident.txt").exists()
    assert (tmp_path / "processed" / "02_critical_incidents" / "incident.txt").exists()


def test_empty_file_goes_to_empty_quarantine(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "empty.txt").write_text("", encoding="utf-8")
    processor = create_processor(tmp_path)

    statistics = processor.process_all()

    assert statistics["90_quarantine_empty"] == 1
    assert (tmp_path / "processed" / "90_quarantine_empty" / "empty.txt").exists()


def test_unsupported_format_goes_to_unsupported_quarantine(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "image.jpeg").write_bytes(b"not a text mail")
    processor = create_processor(tmp_path)

    statistics = processor.process_all()

    assert statistics["91_quarantine_unsupported"] == 1
    assert (tmp_path / "processed" / "91_quarantine_unsupported" / "image.jpeg").exists()


def test_decode_error_goes_to_decode_error_quarantine(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "broken.txt").write_bytes(b"\xff\xfe\xfa")
    processor = create_processor(tmp_path)

    statistics = processor.process_all()

    assert statistics["93_quarantine_decode_error"] == 1
    assert (tmp_path / "processed" / "93_quarantine_decode_error" / "broken.txt").exists()


def test_processing_error_goes_to_corrupted_quarantine(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "broken.txt").write_text("text", encoding="utf-8")
    processor = create_processor(tmp_path)

    def fail_read(_path):
        raise OSError("disk read failed")

    monkeypatch.setattr(processor, "read_mail", fail_read)

    processor.prepare_folders()
    processor.process_file("broken.txt")

    assert processor.statistics["92_quarantine_corrupted"] == 1
    assert (tmp_path / "processed" / "92_quarantine_corrupted" / "broken.txt").exists()


def test_process_all_writes_statistics_file(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "access.txt").write_text(
        "Прошу выдать доступ к VPN для нового сотрудника",
        encoding="utf-8",
    )
    processor = create_processor(tmp_path)

    processor.process_all()

    statistics_text = (tmp_path / "processed" / "statistics.txt").read_text(
        encoding="utf-8"
    )
    assert "Total: 1" in statistics_text
    assert "03_access_requests: 1" in statistics_text


def test_process_all_writes_visual_report(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "access.txt").write_text(
        "Прошу выдать доступ к VPN для нового сотрудника",
        encoding="utf-8",
    )
    processor = create_processor(tmp_path)

    processor.process_all()

    chart_path = tmp_path / "processed" / "statistics.png"
    report_path = tmp_path / "processed" / "report.html"

    assert chart_path.exists()
    assert chart_path.stat().st_size > 0
    assert report_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    assert "Mail Processing Report" in report_text
    assert "Total processed" in report_text
    assert "03_access_requests" in report_text


def test_process_all_raises_when_inbox_is_missing(tmp_path):
    processor = create_processor(tmp_path)

    with pytest.raises(FileNotFoundError):
        processor.process_all()
