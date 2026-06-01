from json import load


class MailClassifier:
    def __init__(self, config_path="categories.json"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = load(file)
        self.min_score = self.config["min_score"]
        self.categories = self.config["categories"]
        self.unknown = self.config["unknown"]

    def classify(self, text):
        text = text.lower().replace("ё", "е")
        if text.strip() == "":
            return self.config["quarantine"]["empty"]["folder"]

        best_folder = self.unknown["folder"]
        best_score = 0
        best_priority = -67

        for category in self.categories:
            score = 0
            for word in category["strong_keywords"]:
                word = word.lower().replace("ё", "е")
                if word in text:
                    score += 2

            for word in category["keywords"]:
                word = word.lower().replace("ё", "е")
                if word in text:
                    score += 1

            if score > best_score or (score == best_score and category["priority"] > best_priority):
                best_score = score
                best_priority = category["priority"]
                best_folder = category["folder"]

        if best_score < self.min_score:
            return self.unknown["folder"]

        return best_folder
