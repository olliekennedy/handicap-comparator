from create_handicap_report import add_plus_to_plus_handicaps


def test_plus():
    assert add_plus_to_plus_handicaps('-9') == '+ 9'


def test_low():
    assert add_plus_to_plus_handicaps('5') == '5'


def test_scratch():
    assert add_plus_to_plus_handicaps('0') == '0'
