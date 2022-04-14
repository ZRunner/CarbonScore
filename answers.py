import csv
from typing import Optional

import spacy
from spacy.tokens import Doc


class AnswersManager:
    "Class used to answer custom questions (about carbonscore, ecology and other things)"

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.questions: list[tuple[Doc, str]] = []
        # read questions and related answers from the csv
        with open('answers.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                self.questions.append((self.nlp(line[0]), line[1]))
    
    def get_answer(self, question: str) -> Optional[str]:
        "Get the best corresponding answer from a question, or None if not applicable"
        sentence, max_score = None, 0.7
        question = self.nlp(question)
        for doc, answer in self.questions:
            score = doc.similarity(question)
            if score > max_score:
                sentence = answer
                max_score = score
        return sentence
    
    def __len__(self):
        return len(self.questions)


if __name__ == '__main__':
    manager = AnswersManager(spacy.load("fr_core_news_lg"))
    for question in {"Quelle est la circonférence du Soleil ?", "C'est quoi un bilan carbon?", "quelle est l'empreinte carbon de la nouriture en françe ?"}:
        print(question, "\n>", manager.get_answer(question))

