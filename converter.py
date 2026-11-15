# -*- coding: utf-8 -*-
"""
Keyboard Mapping and Converter Engine
Converts text typed with incorrect keyboard layout (English QWERTY <-> Arabic 101).
"""

# Windows Arabic 101 keyboard layout mapping
EN_TO_AR = {
    # Lowercase / normal keys
    '`': 'ذ',
    'q': 'ض',
    'w': 'ص',
    'e': 'ث',
    'r': 'ق',
    't': 'ف',
    'y': 'غ',
    'u': 'ع',
    'i': 'ه',
    'o': 'خ',
    'p': 'ح',
    '[': 'ج',
    ']': 'د',
    'a': 'ش',
    's': 'س',
    'd': 'ي',
    'f': 'ب',
    'g': 'ل',
    'h': 'ا',
    'j': 'ت',
    'k': 'ن',
    'l': 'م',
    ';': 'ك',
    "'": 'ط',
    'z': 'ئ',
    'x': 'ء',
    'c': 'ؤ',
    'v': 'ر',
    'b': 'لا',
    'n': 'ى',
    'm': 'ة',
    ',': 'و',
    '.': 'ز',
    '/': 'ظ',

    # Uppercase / Shift keys
    '~': 'ّ',
    'Q': 'َ',
    'W': 'ً',
    'E': 'ُ',
    'R': 'ٌ',
    'T': 'لإ',
    'Y': 'إ',
    'U': '‘',
    'I': '÷',
    'O': '×',
    'P': '؛',
    '{': '<',
    '}': '>',
    'A': 'ِ',
    'S': 'ٍ',
    'D': ']',
    'F': '[',
    'G': 'لأ',
    'H': 'أ',
    'J': 'ـ',
    'K': '،',
    'L': '/',
    ':': ':',
    '"': '"',
    'Z': '~',
    'X': 'ْ',
    'C': '}',
    'V': '{',
    'B': 'لآ',
    'N': 'آ',
    'M': '’',
    '<': ',',
    '>': '.',
    '?': '؟',
}

# Reverse mapping: Arabic to English
AR_TO_EN = {}

# Special ligature reverse mappings
AR_TO_EN['لا'] = 'b'
AR_TO_EN['لإ'] = 'T'
AR_TO_EN['لأ'] = 'G'
AR_TO_EN['لآ'] = 'B'

for en_char, ar_char in EN_TO_AR.items():
    if ar_char not in AR_TO_EN:
        AR_TO_EN[ar_char] = en_char

# Additional common arabic symbols to English mappings
AR_TO_EN['،'] = 'K'
AR_TO_EN['؛'] = 'P'
AR_TO_EN['؟'] = '?'
AR_TO_EN['ء'] = 'x'
AR_TO_EN['ئ'] = 'z'
AR_TO_EN['ؤ'] = 'c'
AR_TO_EN['إ'] = 'Y'
AR_TO_EN['أ'] = 'H'
AR_TO_EN['آ'] = 'N'
AR_TO_EN['ة'] = 'm'
AR_TO_EN['ى'] = 'n'


def is_mostly_arabic(text: str) -> bool:
    """Check if the text has more Arabic characters than English characters."""
    ar_count = 0
    en_count = 0
    for ch in text:
        if '\u0600' <= ch <= '\u06FF' or ch in '،؛؟':
            ar_count += 1
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
            en_count += 1
    return ar_count > en_count


import re

def convert_token_ar_to_en(token: str) -> str:
    """Convert an Arabic token or character to English keyboard layout."""
    res = []
    i = 0
    n = len(token)
    while i < n:
        if i + 1 < n and token[i:i+2] in AR_TO_EN:
            res.append(AR_TO_EN[token[i:i+2]])
            i += 2
        else:
            ch = token[i]
            if ch in '.,!?:;"\'-()[]{}':
                res.append(ch)
            else:
                res.append(AR_TO_EN.get(ch, ch))
            i += 1
    return ''.join(res)


def convert_en_to_ar(text: str) -> str:
    """Convert text typed with English layout to Arabic layout."""
    result = []
    for ch in text:
        result.append(EN_TO_AR.get(ch, ch))
    return ''.join(result)


def convert_ar_to_en(text: str) -> str:
    """Convert text typed with Arabic layout to English layout."""
    return convert_token_ar_to_en(text)


from franco import is_franco_text, convert_franco_to_arabic


def fix_text(text: str) -> str:
    """
    Intelligently converts text typed with incorrect keyboard layout,
    or Franco-Arabic (Arabizi) text into proper Arabic.
    Supports mixed sentences (e.g. English gibberish with accidental Arabic keys
    such as ';dt phg; s,t kj;gl uk pvt ي i,i pvt' -> 'كيف حالك سوف نتكلم عن حرف D هوه حرف').
    """
    if not text:
        return text

    # 1. Check if the text is Arabizi / Franco-Arabic
    if is_franco_text(text):
        return convert_franco_to_arabic(text)

    # 2. Keyboard layout correction (QWERTY <-> Arabic 101)
    mostly_ar = is_mostly_arabic(text)
    tokens = re.split(r'(\s+)', text)
    converted_tokens = []

    for token in tokens:
        if not token or token.isspace():
            converted_tokens.append(token)
            continue

        if mostly_ar:
            token_is_ar = any('\u0600' <= c <= '\u06FF' or c in '،؛؟' for c in token)
            if token_is_ar:
                converted_tokens.append(convert_token_ar_to_en(token))
            else:
                converted_tokens.append(''.join(EN_TO_AR.get(c, c) for c in token))
        else:
            token_is_ar = any('\u0600' <= c <= '\u06FF' or c in '،؛؟' for c in token)
            if token_is_ar:
                converted_word = convert_token_ar_to_en(token)
                stripped = token.strip('.,!?:;"\'-()[]{}')
                if len(stripped) == 1 and stripped.isalpha():
                    converted_word = ''.join(c.upper() if c.isalpha() else c for c in converted_word)
                converted_tokens.append(converted_word)
            else:
                converted_tokens.append(''.join(EN_TO_AR.get(c, c) for c in token))

    return ''.join(converted_tokens)


if __name__ == '__main__':
    # Test cases
    test_1 = ";dt phg;"
    converted_1 = fix_text(test_1)
    print(f"'{test_1}' -> '{converted_1}'")
    assert converted_1 == "كيف حالك", f"Expected 'كيف حالك', got '{converted_1}'"

    test_2 = "كيف حالك"
    converted_2 = fix_text(test_2)
    print(f"'{test_2}' -> '{converted_2}'")
    assert converted_2 == ";dt phg;", f"Expected ';dt phg;', got '{converted_2}'"

    test_3 = "hgsghl ugd;l"
    converted_3 = fix_text(test_3)
    print(f"'{test_3}' -> '{converted_3}'")
    assert converted_3 == "السلام عليكم", f"Expected 'السلام عليكم', got '{converted_3}'"

    test_franco = "mar7aba keefak 7abibi 3ala fekra"
    converted_franco = fix_text(test_franco)
    print(f"'{test_franco}' -> '{converted_franco}'")
    assert converted_franco == "مرحبا كيفك حبيبي على فكرة", f"Expected 'مرحبا كيفك حبيبي على فكرة', got '{converted_franco}'"

    print("All tests passed successfully!")
