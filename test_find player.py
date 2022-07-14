from unittest.mock import Mock

import requests

import create_handicap_report
from create_handicap_report import find_player

too_many_players = [
    {'Rank': 0, 'PassportId': 1241234, 'Name': 'Woods, Tiger', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '20.7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'ssssss', 'ShowProfileLink': True},
    {'Rank': 0, 'PassportId': 219742, 'Name': 'Woods, Charlie', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '-7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'sssssss', 'ShowProfileLink': True}
]
one_player = [
    {'Rank': 0, 'PassportId': 1241234, 'Name': 'Woods, Tiger', 'IsFriend': False, 'Gender': 'Male',
     'HandicapIndexText': '20.7', 'HomeClubName': 'Augusta', 'FriendRequestId': None,
     'IsFriendRequestError': False, 'FriendRequestErrorMessage': None,
     'ProfileURL': 'ssssss', 'ShowProfileLink': True}
]


def test_too_many(capfd):
    create_handicap_report.get_player_records = Mock(return_value=too_many_players)
    assert find_player(requests.Session, 'Woods') == too_many_players
    out, err = capfd.readouterr()
    assert out == "WARNING: too many results for search Woods on England Golf\n"


def test_none(capfd):
    create_handicap_report.get_player_records = Mock(return_value=[])
    assert find_player(requests.Session, 'Woods') == []
    out, err = capfd.readouterr()
    assert out == "WARNING: failed to find player with name Woods on England Golf\n"


def test_one(capfd):
    create_handicap_report.get_player_records = Mock(return_value=one_player)
    assert find_player(requests.Session, 'Woods') == one_player
    out, err = capfd.readouterr()
    assert out == ""
