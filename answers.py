import csv
from typing import Optional
import spacy
from spacy.tokens import Doc

class AnswersManager:

    def __init__(self):
        self.nlp = spacy.load("fr_core_news_lg")
        self.questions: list[tuple[Doc, str]] = []
        with open('answers.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                self.questions.append((self.nlp(line[0]), line[1]))
    
    def get_answer(self, question: str) -> Optional[str]:
        sentence, max_score = None, 0.5
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
    manager = AnswersManager()
    question = "c'est quoi le bilan carbonscore?"
    print(question, manager.get_answer(question))
