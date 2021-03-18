import re


def preprocess(sentence, is_case_sensitive=True):

    # Preprocessing and check punctuation!
    # If it's a table it'll append into a single sentence
    # If it's a text without punctuation it'll append everything into a single sentence
    punctuation = [".", ",", ";", ":", "!", "?"]
    sentence = sentence.strip()

    if (len(sentence) > 0) and sentence[-1] not in punctuation:
        # print('String does not contain punctuation_string', text)
        sentence = sentence + '. '
    else:
        # print('String contains punctuation_string', text)
        sentence = sentence + ' '

    # Removing Square Brackets and Extra Spaces
    sentence = re.sub(r"[^A-Za-z0-9(),.!?\'\`]", " ", sentence)
    sentence = re.sub(r"\s{2,}", " ", sentence)

    # finditer is register sensitive. But source is lowercase-overrides if the requested word is in lowercase,
    # otherwise (if the word is capitalized or whatnot) exact match is required
    if not is_case_sensitive:
        sentence = sentence.lower()

    return re.sub(r'\s+', ' ', sentence)
