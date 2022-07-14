from unittest.mock import Mock

import create_handicap_report
from create_handicap_report import get_handicaps_from_eg

too_many_players = [
    {'Rank': 0, 'PassportId': 2352333, 'Name': 'Woods, Tiger', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '20.7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'ssssss', 'ShowProfileLink': True},
    {'Rank': 0, 'PassportId': 219742, 'Name': 'Woods, Tiger', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '-7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'sssssss', 'ShowProfileLink': True}
]
one_player = [
    {'Rank': 0, 'PassportId': 1245135, 'Name': 'Els, Ernie', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '20.7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'ssssss', 'ShowProfileLink': True}
]
expected_output = {'Els, Ernie': '24'}


def test_too_many(capfd):
    create_handicap_report.login_to_eg = Mock()
    create_handicap_report.get_player_records = Mock(side_effect=[too_many_players, one_player])
    create_handicap_report.convert_index_to_course = Mock(return_value='24')
    assert get_handicaps_from_eg(['Woods, Tiger', 'Els, Ernie']) == expected_output
    out, err = capfd.readouterr()
    assert out == "WARNING: too many results for search Woods, Tiger on England Golf\n"


def test_none(capfd):
    create_handicap_report.login_to_eg = Mock()
    create_handicap_report.get_player_records = Mock(side_effect=[[], one_player])
    create_handicap_report.convert_index_to_course = Mock(return_value='24')
    assert get_handicaps_from_eg(['Woods, Tiger', 'Els, Ernie']) == expected_output
    out, err = capfd.readouterr()
    assert out == "WARNING: failed to find player with name Woods, Tiger on England Golf\n"


def xtest_one(capfd):
    create_handicap_report.login_to_eg = Mock()
    create_handicap_report.get_player_records = Mock(side_effect=[one_player])
    create_handicap_report.convert_index_to_course = Mock(return_value='24')
    assert get_handicaps_from_eg(['Els, Ernie']) == expected_output
    out, err = capfd.readouterr()
    assert out == ""
