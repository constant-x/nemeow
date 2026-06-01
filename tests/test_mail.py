import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from mail import Mail


def test_mail_stores_filename_and_text():
    mail = Mail("mail_0001.txt", "System is unavailable")

    assert mail.filename == "mail_0001.txt"
    assert mail.text == "System is unavailable"
