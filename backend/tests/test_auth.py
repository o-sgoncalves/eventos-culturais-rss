import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    hashed = hash_password("mysecret123")
    assert verify_password("mysecret123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_hash_is_not_plaintext():
    hashed = hash_password("mysecret123")
    assert hashed != "mysecret123"
    assert len(hashed) > 20


def test_create_and_decode_token():
    token = create_token({"sub": "admin", "user_id": 1})
    payload = decode_token(token)
    assert payload["sub"] == "admin"
    assert payload["user_id"] == 1


def test_decode_invalid_token_returns_none():
    result = decode_token("not.a.valid.token")
    assert result is None


def test_decode_tampered_token_returns_none():
    token = create_token({"sub": "admin"})
    tampered = token[:-5] + "XXXXX"
    assert decode_token(tampered) is None
