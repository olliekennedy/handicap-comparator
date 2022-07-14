from unittest.mock import Mock

import create_handicap_report
from create_handicap_report import formatted_row_from

master_handicaps = {'Woods, Tiger': '5', 'Player, Gary': '12'}

eg_handicaps = {'Woods, Tiger': '-8', 'Player, Gary': '-6'}


def test_row():
    create_handicap_report.master_higher_or_lower = Mock(return_value='lemons')
    create_handicap_report.add_plus_to_plus_handicaps = Mock(side_effect=['+ 8', '5'])
    assert formatted_row_from('Woods, Tiger', master_handicaps, eg_handicaps) == ['Woods, Tiger', '+ 8', '5', 'lemons']
