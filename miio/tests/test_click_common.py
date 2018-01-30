from miio.click_common import validate_token, validate_ip


def test_validate_token_empty():
    assert not validate_token(None, None, None)


def test_validate_ip_empty():
    assert validate_ip(None, None, None) is None

