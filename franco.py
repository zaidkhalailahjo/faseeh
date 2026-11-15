# -*- coding: utf-8 -*-
"""
Franco / Arabizi to Arabic Conversion Engine
Translates Franco-Arabic text (e.g. 'mar7aba keefak 7abibi 3ala fekra') into proper Arabic.
"""

import re

# Comprehensive dictionary for common Franco words and phrases
FRANCO_DICTIONARY = {
    # Greetings & Common Expressions
    "mar7aba": "مرحبا",
    "marhaba": "مرحبا",
    "ahlan": "أهلاً",
    "ahlen": "أهلاً",
    "salam": "سلام",
    "salaam": "سلام",
    "alsalam": "السلام",
    "keefak": "كيفك",
    "kefak": "كيفك",
    "keifak": "كيفك",
    "keefek": "كيفِك",
    "kifek": "كيفِك",
    "keefkum": "كيفكم",
    "keefkon": "كيفكم",
    "shlonak": "شلونك",
    "shlonik": "شلونِك",
    "shlonkum": "شلونكم",
    "ezayak": "إزيك",
    "ezayek": "إزيِك",
    "ezayoko": "إزيكوا",
    "7abibi": "حبيبي",
    "habibi": "حبيبي",
    "7abibti": "حبيبتي",
    "habibti": "حبيبتي",
    "7obi": "حبي",
    "ya": "يا",
    "rab": "رب",
    "yarab": "يا رب",
    "wallah": "والله",
    "wallahi": "والله",
    "shokran": "شكراً",
    "shukran": "شكراً",
    "mashkoor": "مشكور",
    "mashkour": "مشكور",
    "3afwan": "عفواً",
    "afwan": "عفواً",
    "inshallah": "إن شاء الله",
    "inshaallah": "إن شاء الله",
    "alhamdulillah": "الحمد لله",
    "elhamdulillah": "الحمد لله",
    "elhamdellah": "الحمد لله",
    "tamam": "تمام",
    "mashi": "ماشي",
    "tayeb": "طيب",
    "6ayeb": "طيب",
    "akhi": "أخي",
    "a5i": "أخي",
    "a5oy": "أخوي",
    "okhti": "أختي",
    "o5ti": "أختي",
    "bhebak": "بحبك",
    "ba7ebak": "بحبك",
    "ba7ebik": "بحبِك",
    "teslam": "تسلم",
    "tislam": "تسلم",
    "mabrook": "مبروك",
    "mabrouk": "مبروك",
    "alf": "ألف",
    "koll": "كل",
    "kol": "كل",
    "sana": "سنة",
    "wein": "وين",
    "wayn": "وين",
    "fein": "فين",
    "fain": "فين",
    "leish": "ليش",
    "lesh": "ليش",
    "leh": "ليه",
    "sho": "شو",
    "shu": "شو",
    "eh": "إيه",
    "eeh": "إيه",
    "meen": "مين",
    "min": "من",
    "kam": "كم",
    "yalla": "يلا",
    "tab3an": "طبعاً",
    "6ab3an": "طبعاً",
    "aslan": "أصلاً",
    "a9lan": "أصلاً",
    "akeed": "أكيد",
    "momken": "ممكن",
    "lazem": "لازم",
    "sa7": "صح",
    "9a7": "صح",
    "ghalat": "غلط",
    "3'alat": "غلط",
    "5alas": "خلاص",
    "khalas": "خلاص",
    "5eir": "خير",
    "kheir": "خير",
    "kheer": "خير",
    "sabah": "صباح",
    "9aba7": "صباح",
    "masaa": "مساء",
    "masa": "مساء",
    "el": "ال",
    "al": "ال",
    "faseeh": "فصيح",
    "fasi7": "فصيح",
    "fasee7": "فصيح",
    "3ala": "على",
    "fekra": "فكرة",
    "3alafekra": "على فكرة",
    "3ashan": "عشان",
    "3ashen": "عشان",
    "kman": "كمان",
    "bardoo": "برضه",
    "bardo": "برضه",
    "hassa": "هسه",
    "hala2": "هلق",
    "dilwa2ti": "دلوقتي",
    "delwa2ty": "دلوقتي",
    "kteer": "كتير",
    "ktir": "كتير",
    "shway": "شوي",
    "shwaya": "شوية",
    "zghir": "صغير",
    "kbeer": "كبير",
    "helw": "حلو",
    "7elw": "حلو",
    "hilw": "حلو",
    "gamid": "جامد",
    "biddi": "بدي",
    "bade": "بدي",
    "3ayez": "عايز",
    "3ayza": "عايزة",
    "la": "لا",
    "la2": "لا",
    "na3am": "نعم",
    "aywa": "أيوه",
    "aiwa": "أيوه",
    "ah": "آه",
    "bas": "بس",
    "ma": "ما",
    "msh": "مش",
    "mesh": "مش",
    "mo": "مو",
    "mafi": "ما في",
    "fi": "في",
    "fee": "في",
    "fe": "في",
    "ana": "أنا",
    "enta": "إنت",
    "ente": "إنتِ",
    "enti": "إنتِ",
    "ento": "إنتو",
    "e7na": "إحنا",
    "ne7na": "نحنا",
    "howa": "هو",
    "heya": "هي",
    "homa": "هم",
}

# Multi-word Franco phrases
PHRASE_MAPPINGS = [
    (r"\b3ala\s+fekra\b", "على فكرة"),
    (r"\bin\s+sha\s+allah\b", "إن شاء الله"),
    (r"\bin\s+sha2\s+allah\b", "إن شاء الله"),
    (r"\bin\s+allah\b", "إن شاء الله"),
    (r"\bsaba7\s+el\s+5eir\b", "صباح الخير"),
    (r"\b9aba7\s+el\s+5eir\b", "صباح الخير"),
    (r"\bsabah\s+el\s+kheir\b", "صباح الخير"),
    (r"\bmasaa?\s+el\s+5eir\b", "مساء الخير"),
    (r"\bmasaa?\s+el\s+kheir\b", "مساء الخير"),
    (r"\bahlan\s+wa\s+sahlan\b", "أهلاً وسهلاً"),
    (r"\bkol\s+sana\s+w\s*enta\s+tayeb\b", "كل سنة وانت طيب"),
    (r"\bkol\s+3am\s+w\s*ento\s+b5eir\b", "كل عام وانتو بخير"),
    (r"\bkol\s+3am\s+w\s*ento\s+bkheir\b", "كل عام وانتو بخير"),
    (r"\b3amel\s+eh\b", "عامل إيه"),
    (r"\b3amla\s+eh\b", "عاملة إيه"),
]

# Character & Digraph mapping for general Arabizi transliteration
PHONETIC_RULES = [
    # 2-character / digraph patterns first
    (r"3'", "غ"),
    (r"th", "ث"),
    (r"sh", "ش"),
    (r"ch", "تش"),
    (r"kh", "خ"),
    (r"gh", "غ"),
    (r"dh", "ض"),
    (r"ee", "ي"),
    (r"ei", "ي"),
    (r"oo", "و"),
    (r"ou", "و"),
    (r"aa", "ا"),
    (r"2a", "أ"),
    (r"2o", "أ"),
    (r"2e", "إ"),
    (r"2i", "إ"),

    # Single numbers
    (r"2", "ء"),
    (r"3", "ع"),
    (r"4", "ذ"),
    (r"5", "خ"),
    (r"6", "ط"),
    (r"7", "ح"),
    (r"8", "ق"),
    (r"9", "ص"),

    # Single letters
    (r"b", "ب"),
    (r"p", "ب"),
    (r"t", "ت"),
    (r"j", "ج"),
    (r"g", "ج"),
    (r"d", "د"),
    (r"r", "ر"),
    (r"z", "ز"),
    (r"s", "س"),
    (r"f", "ف"),
    (r"v", "ف"),
    (r"q", "ق"),
    (r"k", "ك"),
    (r"l", "ل"),
    (r"m", "م"),
    (r"n", "ن"),
    (r"h", "ه"),
    (r"w", "و"),
    (r"y", "ي"),
    (r"a", "ا"),
    (r"e", "ي"),
    (r"i", "ي"),
    (r"o", "و"),
    (r"u", "و"),
]


def is_franco_text(text: str) -> bool:
    """Detect if text contains Arabizi / Franco-Arabic characteristics."""
    if not text:
        return False

    # Check for Arabizi digits inside words (e.g. 3, 7, 5, 2, 6, 8, 9 with latin letters)
    has_franco_digits = bool(re.search(r'[a-zA-Z]+[2356789]|[2356789][a-zA-Z]+', text))
    if has_franco_digits:
        return True

    # Check for presence of distinct Franco vocabulary
    words = re.findall(r'[a-zA-Z0-9\']+', text.lower())
    if not words:
        return False

    franco_match_count = sum(1 for w in words if w in FRANCO_DICTIONARY)
    if franco_match_count >= 1 and (franco_match_count / len(words)) >= 0.25:
        return True

    return False


def convert_franco_word(word: str) -> str:
    """Convert an individual Franco word to Arabic."""
    clean = word.lower().strip()
    if clean in FRANCO_DICTIONARY:
        return FRANCO_DICTIONARY[clean]

    # Handle prefixed 'el' or 'al' (e.g. 'elbeit' -> 'البيت')
    if (clean.startswith("el") or clean.startswith("al")) and len(clean) > 3:
        sub = clean[2:]
        if sub in FRANCO_DICTIONARY:
            return "ال" + FRANCO_DICTIONARY[sub]

    # Handle prefixed 'w' or 'wa' (and)
    if clean.startswith("w") and len(clean) > 2 and clean[1:] in FRANCO_DICTIONARY:
        return "و" + FRANCO_DICTIONARY[clean[1:]]

    # Handle prefixed 'b' (in/with)
    if clean.startswith("b") and len(clean) > 2 and clean[1:] in FRANCO_DICTIONARY:
        return "ب" + FRANCO_DICTIONARY[clean[1:]]

    # Fallback: Phonetic transliteration
    res = clean
    for pattern, replacement in PHONETIC_RULES:
        res = re.sub(pattern, replacement, res)

    return res


def convert_franco_to_arabic(text: str) -> str:
    """Translate full Franco text into Arabic."""
    if not text:
        return text

    result = text
    # 1. Apply multi-word phrases first
    for pattern, repl in PHRASE_MAPPINGS:
        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)

    # 2. Tokenize words and punctuation
    tokens = re.split(r'(\s+|[.,!?:;"\'-]+)', result)
    converted = []

    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,!?:;"\'-]+$', t):
            converted.append(t)
        elif any('\u0600' <= c <= '\u06FF' for c in t):
            # Already Arabic (from phrase replacement)
            converted.append(t)
        else:
            converted.append(convert_franco_word(t))

    return ''.join(converted)


if __name__ == "__main__":
    test_cases = [
        "mar7aba keefak 7abibi 3ala fekra",
        "shlonak ya ghali",
        "inshallah 5alas bshofak bokra",
        "alhamdulillah 3ala kol 7al",
        "sabah el kheir ya 7elw",
    ]
    for tc in test_cases:
        print(f"'{tc}' -> '{convert_franco_to_arabic(tc)}'")
