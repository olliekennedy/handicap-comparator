from create_handicap_report import master_higher_or_lower


def test_higher():
    assert master_higher_or_lower(course='8', master='11') == 'Higher'
    assert master_higher_or_lower(course='-2', master='-1') == 'Higher'
    assert master_higher_or_lower(course='-2', master='2') == 'Higher'
    assert master_higher_or_lower(course='0', master='1') == 'Higher'
    assert master_higher_or_lower(course='-1', master='0') == 'Higher'


def test_lower():
    assert master_higher_or_lower(course='0', master='-1') == 'Lower'
    assert master_higher_or_lower(course='1', master='0') == 'Lower'
    assert master_higher_or_lower(course='5', master='-5') == 'Lower'


def test_same():
    assert master_higher_or_lower(course='0', master='0') == 'Same'
    assert master_higher_or_lower(course='-1', master='-1') == 'Same'
    assert master_higher_or_lower(course='5', master='5') == 'Same'


def test_na():
    assert master_higher_or_lower(course='', master='0') == 'N / A'
    assert master_higher_or_lower(course='-1', master='') == 'N / A'
