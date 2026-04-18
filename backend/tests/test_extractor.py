import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workers.event_extractor import extract_date, extract_time, extract_price, detect_category, is_free_event, extract_event_data


def test_extract_date_slash_format():
    result = extract_date("Show dia 25/04/2026 no Casarão")
    assert result is not None
    assert result.day == 25
    assert result.month == 4


def test_extract_date_keyword_dia():
    result = extract_date("Evento dia 10 de abril")
    assert result is not None
    assert result.day == 10


def test_extract_date_returns_none_when_absent():
    assert extract_date("Sem data nenhuma aqui") is None


def test_extract_time_with_h():
    assert extract_time("Começa às 20h no Espaço") == "20:00"


def test_extract_time_with_h_minutes():
    assert extract_time("Abertura 19h30") == "19:30"


def test_extract_time_colon_format():
    assert extract_time("A partir das 21:00") == "21:00"


def test_extract_time_returns_none_when_absent():
    assert extract_time("Sem horário definido") is None


def test_extract_price_real():
    assert extract_price("Ingresso R$ 40") == "R$ 40"


def test_extract_price_range():
    result = extract_price("Ingressos de R$ 30 a R$ 80")
    assert "30" in result and "80" in result


def test_extract_price_returns_none_when_absent():
    assert extract_price("Sem info de preço") is None


def test_is_free_gratuis():
    assert is_free_event("Entrada franca para todos") is True
    assert is_free_event("Acesso gratuito") is True
    assert is_free_event("Show grátis!") is True
    assert is_free_event("Free admission") is True


def test_is_free_false_when_paid():
    assert is_free_event("Ingresso R$ 50") is False


def test_detect_category_music():
    assert detect_category("Grande show com banda ao vivo") == "musica"


def test_detect_category_theater():
    assert detect_category("Peça de teatro imperdível") == "teatro"


def test_detect_category_exposition():
    assert detect_category("Exposição de arte contemporânea") == "exposicao"


def test_detect_category_returns_outros():
    assert detect_category("Algo sem categoria definida") == "outros"


def test_extract_event_data_full_text():
    text = """
    Show da Banda Xpto no Casarão Cultural
    Dia 25/04 às 20h
    Ingresso: R$ 40
    Setor Bueno, Goiânia
    """
    result = extract_event_data(text, source_url="https://instagram.com/p/test")
    assert result["title"] is not None
    assert result["event_time"] == "20:00"
    assert result["price"] == "R$ 40"
    assert result["category"] == "musica"
    assert result["is_free"] is False
