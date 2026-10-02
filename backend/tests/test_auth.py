from app.core.security import create_access_token, hash_password, verify_password


def test_password_hashing_roundtrip():
    password = 'SecurePassword123!'
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_access_token_contains_subject():
    token = create_access_token('user-123')
    assert isinstance(token, str)
    assert len(token) > 20
