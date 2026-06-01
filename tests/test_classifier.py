import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from classifier import MailClassifier


ROOT = Path(__file__).resolve().parents[1]


def write_config(tmp_path, *, min_score=2, categories=None):
    config = {
        "min_score": min_score,
        "unknown": {"folder": "unknown"},
        "quarantine": {"empty": {"folder": "empty"}},
        "categories": categories
        or [
            {
                "folder": "finance",
                "priority": 10,
                "strong_keywords": ["счет"],
                "keywords": ["payment"],
            },
            {
                "folder": "access",
                "priority": 20,
                "strong_keywords": ["vpn access"],
                "keywords": ["account"],
            },
        ],
    }
    config_path = tmp_path / "categories.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    return config_path


def test_classify_uses_strong_keyword_and_normalizes_text(tmp_path):
    config_path = write_config(tmp_path)
    classifier = MailClassifier(config_path)

    assert classifier.classify("Нужен СЧЁТ на оплату") == "finance"


def test_classify_returns_unknown_when_score_is_below_minimum(tmp_path):
    config_path = write_config(tmp_path)
    classifier = MailClassifier(config_path)

    assert classifier.classify("Please check this account") == "unknown"


def test_classify_uses_priority_to_break_score_ties(tmp_path):
    config_path = write_config(
        tmp_path,
        min_score=1,
        categories=[
            {
                "folder": "low_priority",
                "priority": 10,
                "strong_keywords": [],
                "keywords": ["urgent"],
            },
            {
                "folder": "high_priority",
                "priority": 50,
                "strong_keywords": [],
                "keywords": ["urgent"],
            },
        ],
    )
    classifier = MailClassifier(config_path)

    assert classifier.classify("urgent request") == "high_priority"


def test_classify_empty_text_as_empty_quarantine(tmp_path):
    config_path = write_config(tmp_path)
    classifier = MailClassifier(config_path)

    assert classifier.classify("   \n\t") == "empty"


@pytest.mark.parametrize(
    "text, expected_folder",
    [
        (
            "Немедленно подтвердите личность и перейдите по ссылке secure-login",
            "01_spam_phishing",
        ),
        (
            "[CRITICAL] Сервис недоступен, возвращает ошибка 500",
            "02_critical_incidents",
        ),
        (
            "Прошу выдать доступ к VPN для нового сотрудника",
            "03_access_requests",
        ),
        (
            "Обычное письмо без понятных признаков категории",
            "10_unknown_unclassified",
        ),
    ],
)
def test_project_config_classifies_representative_messages(text, expected_folder):
    classifier = MailClassifier(ROOT / "categories.json")

    assert classifier.classify(text) == expected_folder
