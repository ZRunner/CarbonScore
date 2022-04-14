import re
from typing import Optional
import spacy
from spacy.tokens import Doc

nlp = spacy.load("fr_core_news_lg")
ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
ruler.add_patterns([
    {"label": "ORG", "pattern": "CarbonScore"},
])

def parse_msg(msg: str) -> Doc:
    return nlp(msg)

def get_heater_carbon(sources: set[str], surface: int) -> Optional[int]:
    if len(sources) == 0:
        return None
    values = {
        "fioul": 264,
        "gaz": 208,
        "électricité": 79,
        "radiateur": 79,
        "biométhane": 14,
        "bois": 0
    }
    surface = surface/len(sources)
    return round(sum(surface*100*values[source] for source in sources))

def get_heater_surface(sentence: str) -> int:
    if sentence.isnumeric():
        return int(sentence)
    result = 0
    for match in re.findall(r'(\d[\d\s]*)(?:[,.]\d+\s*)?(?:m|mètre|metre)', sentence.lower()):
        match: str
        result += int(match.replace(' ', ''))
    return result or None

def get_heater_sources(sentence: str) -> Optional[set[str]]:
    sources = ["fioul", "gaz", "électricité", "radiateur", "biométhane", "bois"]
    result = set()
    doc = parse_msg(sentence)

    # on lit tous les mots de la phrase
    for word in doc:
        if word.is_stop or word.text in {"chauffe"}:
            continue
        max_value: float = 0.55 # plus grande similarité de source pour ce mot
        max_src: str = None # source la plus proche de ce mot (None si aucune)
        # on regarde chaque source
        for source in sources:
            # si on a une correspondance parfaite
            if source == word.lower_:
                max_src = source
                break
            score = word.similarity(nlp(source))
            # si ce mot est plus proche que le mot actuel
            if score > max_value:
                max_src = source
                max_value = score
        # si on a trouvé un mot similaire
        if max_src:
            result.add(max_src)
    return result or None

def get_distance_km(sentence: str) -> Optional[int]:
    if sentence.isnumeric():
        return int(sentence)
    if nlp(sentence).similarity(nlp("je ne prend pas la voiture")) > 0.8:
        return 0
    result = None
    # distance
    if match := re.search(r'(\d[\d\s]*)(?:[,.]\d+\s*)?(?:km|kilomètres?)', sentence.lower()):
        result = int(match.group(1).replace(' ', ''))
        # number of people
        if match2 := re.search(r'(\d+) (?:passagers?|personnes)', sentence.lower()):
            result *= int(match2.group(1).replace(' ', ''))
        # number of *other* people
        elif match2 := re.search(r'(\d+) autres? (?:passagers?|personnes)?', sentence.lower()):
            result *= int(match2.group(1).replace(' ', '')) + 1
    return result

def get_time_hours(sentence: str) -> Optional[int]:
    result = None
    if sentence.isnumeric():
        result = int(sentence)
    elif match := re.search(r'(\d+) ?(?:h)', sentence.lower()):
        result = int(match.group(1))
    # check for aberations
    if result is not None and result > 24*7:
        result = None
    return result

def get_diet(sentence: str):
    sources = [
        "végétarien",
        "végan",
        "normal",
        "tout"
    ]
    
    result = []
    doc = parse_msg(sentence)
    # on lit tous les mots de la phrase
    for word in doc:
        max_value: float = 0.55 # plus grande similarité de source pour ce mot
        max_src: str = None # source la plus proche de ce mot (None si aucune)
        if (word.text in {"vege","végé","vége","vegé"}):
            result.append("végétarien")
        # on regarde chaque source
        for source in sources:
            score = word.similarity(nlp(source))
            if score > max_value:
                max_src = source
                max_value = score
        # si on a trouvé un mot similaire
        if max_src:
            result.append(max_src)
            
    if ("normal" in result #N'est pas vegan ni vegetarien
        or "tout" in result 
        or (not "végan" in result
            and not "végétarien" in result)):
        return "normal"
    elif ("végétarien" in result): #Est vegetarien
        return "vegetarien"
    else: #Est vegan
        return "vegan"
    
def get_clothes_number(sentence: str) -> int:
    if sentence.isnumeric():
        return int(sentence)
    result = 0
    count = 0
    for match in re.findall(r'(\d+) ?(?:vêtements?|vetements)?', sentence.lower()):
        match: str
        count += 1
        result += int(match.replace(' ', ''))
    return int(result/count) if count != 0 else None

if __name__ == '__main__':
    # src = get_heater_sources("Je me réchauffe principalement au fioul")
    # print(get_heater_sources("Bois"))
    # surface = get_heater_surface("J'ai 1 151,7 m²")
    # print(src, surface)
    # print(get_heater_carbon(src, surface))
    # print(get_distance_km("J'utilise la voiture 12km par semaine, on est avec 3 personnes"))
    # print(get_distance_km("5km par semaine en moyenne, avec 4 autres collègues"))
    # print(get_distance_km("je ne prend jamais ma voiture"))
    # print(get_diet("Je mange de tout et de temps en temps je suis vegan"))
    # print(get_clothes_number("Environ entre 15 et 8 vêtements"))
    # print(get_clothes_number("Je suis pauvre"))
    pass
