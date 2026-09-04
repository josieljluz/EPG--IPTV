import re
import unicodedata


def normalize_text(text):

    if not text:
        return ""

    text = str(text).strip().lower()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return " ".join(text.split())


def clean_title(title):

    if not title:
        return "Programação"

    title = re.sub(
        r"\s+",
        " ",
        str(title)
    )

    return title.strip()


def parse_time(value):

    if not value:
        return None

    value = str(value).strip()

    patterns = [
        "%H:%M",
        "%Hh%M",
        "%Hh",
        "%H.%M"
    ]

    from datetime import datetime

    for pattern in patterns:

        try:
            return datetime.strptime(
                value,
                pattern
            ).time()

        except ValueError:
            pass

    return None