import re
from datetime import datetime
from typing import Optional

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "musica":     ["show", "banda", "música", "concerto", "forró", "samba", "jazz", "rock", "pagode"],
    "teatro":     ["peça", "teatro", "espetáculo", "dramaturgia", "ator", "atriz"],
    "cinema":     ["filme", "cinema", "sessão", "curta", "documentário", "projeção"],
    "festa":      ["festa", "balada", "party", "dj", "open bar", "aniversário"],
    "exposicao":  ["exposição", "mostra", "instalação", "vernissage", "galeria"],
    "arte":       ["arte visual", "arte urbana", "grafite", "intervenção"],
    "workshop":   ["workshop", "oficina", "curso", "aula", "capacitação"],
    "palestra":   ["palestra", "debate", "mesa redonda", "seminário", "simpósio"],
    "esporte":    ["corrida", "torneio", "campeonato", "esporte", "maratona"],
    "gastronomia": ["gastronômico", "culinária", "chef", "degustação", "foodfest"],
}

FREE_PATTERNS = re.compile(
    r"\b(grátis|gratuito|entrada\s+franca|free|acesso\s+gratuito)\b", re.IGNORECASE
)

DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?\b"),
    re.compile(r"\bdia\s+(\d{1,2})\b", re.IGNORECASE),
]

MONTH_NAMES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

TIME_PATTERNS = [
    re.compile(r"\b(\d{1,2})h(\d{2})\b", re.IGNORECASE),  # 20h30
    re.compile(r"\b(\d{1,2})h\b", re.IGNORECASE),          # 20h
    re.compile(r"\b(\d{1,2}):(\d{2})\b"),                   # 20:00
]

PRICE_PATTERNS = [
    re.compile(r"R\$\s*(\d+)\s*(?:a|ao?)\s*R\$\s*(\d+)"),  # range
    re.compile(r"R\$\s*(\d+(?:[,.]\d{2})?)"),               # single
]


def extract_date(text: str) -> Optional[datetime]:
    now = datetime.now()

    # Try DD/MM or DD/MM/YYYY
    m = DATE_PATTERNS[0].search(text)
    if m:
        try:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else now.year
            if year < 100:
                year += 2000
            return datetime(year, month, day)
        except ValueError:
            pass

    # Try "dia NN de MMMM"
    m = re.search(r"\bdia\s+(\d{1,2})(?:\s+de\s+(\w+))?", text, re.IGNORECASE)
    if m:
        try:
            day = int(m.group(1))
            month_name = (m.group(2) or "").lower()
            month = MONTH_NAMES.get(month_name, now.month)
            return datetime(now.year, month, day)
        except ValueError:
            pass

    return None


def extract_time(text: str) -> Optional[str]:
    # 20h30
    m = TIME_PATTERNS[0].search(text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    # 20h
    m = TIME_PATTERNS[1].search(text)
    if m:
        return f"{int(m.group(1)):02d}:00"

    # 20:00
    m = TIME_PATTERNS[2].search(text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    return None


def extract_price(text: str) -> Optional[str]:
    # Range: R$ 30 a R$ 80
    m = PRICE_PATTERNS[0].search(text)
    if m:
        return f"R$ {m.group(1)} a R$ {m.group(2)}"

    # Single: R$ 40
    m = PRICE_PATTERNS[1].search(text)
    if m:
        return f"R$ {m.group(1)}"

    return None


def is_free_event(text: str) -> bool:
    return bool(FREE_PATTERNS.search(text))


def detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "outros"


def extract_event_data(text: str, source_url: str, image_url: str = None) -> dict:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    title = lines[0][:255] if lines else "Evento sem título"

    price = extract_price(text)
    free = is_free_event(text)
    if free:
        price = price or "Gratuito"

    return {
        "title": title,
        "description": text,
        "event_date": extract_date(text),
        "event_time": extract_time(text),
        "price": price,
        "is_free": free,
        "category": detect_category(text),
        "source_url": source_url,
        "image_url": image_url,
        "approved": False,
    }
