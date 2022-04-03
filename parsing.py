import spacy
from spacy.tokens import Doc
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop

nlp = spacy.load("fr_core_news_lg")
tokenizer = nlp.tokenizer

def parse_msg(msg: str) -> Doc:
    return nlp(msg)
