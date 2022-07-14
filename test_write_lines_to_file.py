from unittest.mock import mock_open, patch

from create_handicap_report import write_lines_to_file

problem_names = ['Rose, Justin']


def test_plus():
    open_mock = mock_open()
    with patch("create_handicap_report.open", open_mock, create=True):
        write_lines_to_file(problem_names)

    open_mock.assert_called_with("problem-names.txt", "w")
    open_mock.return_value.write.assert_called_with('Rose, Justin\n')

