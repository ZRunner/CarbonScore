import csv
from typing import Optional
import numpy as np

import spacy
from spacy.tokens import Doc


def compute_similarity(doc1: Doc, doc2: Doc) -> float:
    "Compute similarities between 2 docs but ignores stopwords and punctuation"
    vector1 = np.zeros(300)
    vector2 = np.zeros(300)
    for token in doc1:
        if not token.is_stop and token.pos_ != 'PUNCT':
            vector1 = vector1 + token.vector
    vector1: np.ndarray = np.divide(vector1, len(doc1))
    for token in doc2:
        if not token.is_stop and token.pos_ != 'PUNCT':
            vector2 = vector2 + token.vector
    vector2: np.ndarray = np.divide(vector2, len(doc2))
    if (vector1.min() == vector1.max() == 0) or (vector2.min() == vector2.max() == 0):
        # fallback to traditional computation
        return doc1.similarity(doc2)
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


class AnswersManager:
    "Class used to answer custom questions (about carbonscore, ecology and other things)"

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.questions: list[tuple[Doc, str]] = []
        # read questions and related answers from the csv
        with open('answers.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                self.questions.append((self.nlp(line[0]), line[1].replace("\\n", "\n")))
    
    def get_answer(self, question: str) -> Optional[str]:
        "Get the best corresponding answer from a question, or None if not applicable"
        sentence, max_score = None, 0.7
        question: Doc = self.nlp(question)
        for doc, answer in self.questions:
            # score = doc.similarity(question)
            score = compute_similarity(doc, question)
            if score > max_score:
                sentence = answer
                max_score = score
        return sentence
    
    def __len__(self):
        return len(self.questions)


if __name__ == '__main__':
    from carbonscore import nlp
    manager = AnswersManager(nlp)
    for question in ("Quelle est la circonférence du Soleil ?", "C'est quoi un bilan carbone?", "quelle est l'empreinte carbon de la nouriture en françe ?", "C'est quoi carbonscore ?"):
        print(question, "\n>", manager.get_answer(question))
    
    a = nlp("Qu'est-ce que le patinage ?")
    b = nlp("Qu'est-ce que CarbonScore ?")
    r1, r2 = a.similarity(b), compute_similarity(a, b)
    print(r1, r2)

