"""
The inbuilt round function uses bankers rounding, rounding to the nearest even number on halves
i.e. round(1.5) == 2 and round(2.5) == 2 -> True

Golf handicaps always round up on halves, even if negative
i.e. golf_round(1.5) == 2 and golf_round(2.5) == 3 and golf_round(-1.5) == -1 and golf_round(-2.5) == -2 -> True

"""
from create_handicap_report import golf_round


def test_various():
    assert round(3.8) == 4
    assert golf_round(3.8) == 4

    assert golf_round(3.4) == 3
    assert round(3.4) == 3

    assert golf_round(4.0) == 4
    assert round(4.0) == 4

    assert golf_round(3.5) == 4
    assert round(3.5) == 4

    assert golf_round(4.5) == 5
    assert round(4.5) == 4

    assert golf_round(0.0) == 0
    assert round(0.0) == 0

    assert golf_round(-1.5) == -1
    assert round(-1.5) == -2

    assert golf_round(-2.5) == -2
    assert round(-2.5) == -2

    assert golf_round(-1.6) == -2
    assert round(-1.6) == -2

    assert golf_round(-1.0) == -1
    assert round(-1.0) == -1
