from unittest import mock
from unittest.mock import Mock

import create_handicap_report
from create_handicap_report import get_course_handicap

player_content = b'{"Records":[{"Rank":0,"PassportId":393753,"Name":"Woods, Tiger",' \
                 b'"IsFriend":false,"Gender":"Male","HandicapIndexText":"16.2","HomeClubName":"Augusta' \
                 b'Club","FriendRequestId":null,"IsFriendRequestError":false,"FriendRequestErrorMessage":null,' \
                 b'"ProfileURL":"xxxxx",' \
                 b'"ShowProfileLink":true}],"IsError":false,"ErrorMessage":null} '


@mock.patch.object(create_handicap_report, "convert_index_to_course")
def test_called(convert_index_to_course):
    get_course_handicap(player_content)
    convert_index_to_course.assert_called_with('16.2')


def test_returns_string():
    create_handicap_report.convert_index_to_course = Mock(return_value=-3.4)
    assert get_course_handicap(player_content) == '-3.4'
