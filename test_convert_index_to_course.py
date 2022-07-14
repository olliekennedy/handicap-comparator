from create_handicap_report import convert_index_to_course


def test_mid():
    assert convert_index_to_course(index='13.1') == 15


def test_low():
    assert convert_index_to_course(index='1.6') == 2


def test_plus():
    assert convert_index_to_course(index='-4.4') == -5


def test_scratch():
    assert convert_index_to_course(index='0') == 0
