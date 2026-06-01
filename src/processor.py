import os
import shutil
import logging
from json import load

from mail import Mail
from classifier import MailClassifier


class MailProcessor:
    def __init__(self, inbox_dir="inbox", processed_dir="processed", log_dir="logs", config_path="categories.json"):
        self.inbox_dir = inbox_dir
        self.processed_dir = processed_dir
        self.log_dir = log_dir
        self.classifier = MailClassifier(config_path)
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = load(file)
        self.statistics = {}

    def prepare_folders(self):
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

        for category in self.config["categories"]:
            folder = category["folder"]
            os.makedirs(os.path.join(self.processed_dir, folder), exist_ok=True)
            self.statistics[folder] = 0

        unknown_folder = self.config["unknown"]["folder"]
        os.makedirs(os.path.join(self.processed_dir, unknown_folder), exist_ok=True)
        self.statistics[unknown_folder] = 0

        for quarantine in self.config["quarantine"].values():
            folder = quarantine["folder"]
            os.makedirs(os.path.join(self.processed_dir, folder), exist_ok=True)
            self.statistics[folder] = 0

        logging.basicConfig(
            filename=os.path.join(self.log_dir, "processing.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
            force=True
        )

    def read_mail(self, path):
        filename = os.path.basename(path)
        if not filename.endswith(".txt"):
            raise ValueError("Unsupported file format")
        with open(path, "r", encoding="utf-8", errors="strict") as file:
            text = file.read()
        return Mail(filename, text)

    def process_file(self, filename):
        source_path = os.path.join(self.inbox_dir, filename)
        try:
            mail = self.read_mail(source_path)
            category = self.classifier.classify(mail.text)
        except UnicodeDecodeError:
            category = self.config["quarantine"]["decode_error"]["folder"]
        except ValueError:
            category = self.config["quarantine"]["unsupported_format"]["folder"]
        except Exception as error:
            category = self.config["quarantine"]["corrupted"]["folder"]
            logging.error(f"{filename}: processing error: {error}")

        destination_path = os.path.join(self.processed_dir, category, filename)
        shutil.move(source_path, destination_path)
        self.statistics[category] += 1
        logging.info(f"{filename}: {category}")

    def save_statistics(self):
        statistics_path = os.path.join(self.processed_dir, "statistics.txt")

        with open(statistics_path, "w", encoding="utf-8") as file:
            total = sum(self.statistics.values())
            file.write(f"Total: {total}\n\n")
            for category, count in sorted(self.statistics.items()):
                file.write(f"{category}: {count}\n")

    def process_all(self):
        self.prepare_folders()
        if not os.path.exists(self.inbox_dir):
            raise FileNotFoundError("Inbox folder not found")

        for filename in os.listdir(self.inbox_dir):
            path = os.path.join(self.inbox_dir, filename)
            if os.path.isfile(path):
                self.process_file(filename)

        self.save_statistics()
        return self.statistics
