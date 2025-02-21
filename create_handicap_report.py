#!/usr/bin/env python3
import json
import os
import time
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import *
from names_mapping import NAMES_MAPPING

DEFAULT_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.0.0 Safari/537.36 '
}
MASTER_SCOREBOARD_HANDICAP_URL = 'https://www.masterscoreboard.co.uk/results/HandicapList.php?CWID=' + MASTER_SCOREBOARD_CWID
EG_PLAYER_SEARCH_API_URL = 'https://members.whsplatform.englandgolf.org/api/member/FindPotentialFriends'
EG_LOGIN_SOUP_URL = 'https://members.whsplatform.englandgolf.org/igolf-login'
EG_LOGIN_URL = 'https://members.whsplatform.englandgolf.org/layouts/terraces_golfnz/Template.aspx'


def login_to_eg() -> requests.Session:
    session = requests.Session()
    login_soup = BeautifulSoup(session.get(EG_LOGIN_SOUP_URL, headers=DEFAULT_HEADERS).content, features="html.parser")

    params = {
        'page': 'igolf login',
    }
    login_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': (login_soup.find('input', attrs={'name': '__VIEWSTATE'})['value']),
        '__VIEWSTATEGENERATOR': (login_soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']),
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '600',
        '__EVENTVALIDATION': (login_soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']),
        # Looks like these ctlXX$ tags are dynamic, W/O them being correct it seems to stop us from getting the ApiToken
        grab_login_fields(login_soup, "tbMembershipNumber"): EG_MEMBERSHIP_NUMBER,
        grab_login_fields(login_soup, "tbPassword"): EG_PASSWORD,
        grab_login_fields(login_soup, "btnLogin"): 'Login',
    }

    session.post(EG_LOGIN_URL,
                 params=params,
                 data=login_data,
                 headers={**DEFAULT_HEADERS, **{"Host": "members.whsplatform.englandgolf.org",
                                                "Origin": "https://members.whsplatform.englandgolf.org",
                                                "Referer": "https://members.whsplatform.englandgolf.org/igolf-login",
                                                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                                                          "image/avif,image/webp,image/apng,*/*;q=0.8,"
                                                          "application/signed-exchange;v=b3;q=0.7",
                                                "Accept-Encoding": "gzip, deflate, br",
                                                "Cache-Control": "max-age=0",
                                                "Connection": "keep-alive",
                                                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,sk;q=0.7"}})

    if session.cookies.get("CWApiToken") is None:
        raise MyEgSessionProblem("ERROR: Missing CWApiToken cookie")

    return session


def grab_login_fields(soup: BeautifulSoup, field: str) -> str:
    regex = re.compile(r"ctl[0-9]+\$" + field, re.IGNORECASE)
    matches = soup.find_all('input', {'name': regex})
    if len(matches) == 0:
        raise MyEgUnableToFindCtrTagsProblem("ERROR: Unable to find anything for " + field)
    return matches[0]["name"]


def get_player_records(session, params):
    raw = session.get(url=EG_PLAYER_SEARCH_API_URL, params=params,
                      headers={**DEFAULT_HEADERS, **{'accept': 'application/json', 'content-type': 'application/json'}})
    result = json.loads(raw.content)
    return result['Records']


def convert_index_to_course(index) -> int:
    course_hcp = golf_round(float(index) * (float(SLOPE_INDEX)) / float(113) + (float(COURSE_RATING) - float(PAR)))
    return -course_hcp if index[0] == '+' else course_hcp


def write_handicaps_to_files(master_handicaps, eg_handicaps):
    lines = [formatted_row_from(name, master_handicaps, eg_handicaps) for name in master_handicaps]
    dataframe = pd.DataFrame(lines, columns=['Name', 'Course Handicap', 'Master Handicap', 'Master higher?'])
    dataframe.index = range(1, dataframe.shape[0] + 1)
    dataframe.to_excel('handicap-report.xlsx', index=False)


def formatted_row_from(name, master_handicaps, eg_handicaps) -> list[str, str, str, str]:
    course_raw = eg_handicaps[name] if name in eg_handicaps else ''
    master_raw = master_handicaps[name]
    higher_or_lower = master_higher_or_lower(course=course_raw, master=master_raw)
    course_handicap = add_plus_to_plus_handicaps(course_raw)
    master_handicap = add_plus_to_plus_handicaps(master_raw)
    return [name, course_handicap, master_handicap, higher_or_lower]


DIFF = {
    'higher': 'Higher',
    'lower': 'Lower',
    'same': 'Same',
    'n/a': 'N / A',
}


def master_higher_or_lower(course, master) -> str:
    if course and master:
        if int(master) > int(course):
            diff = 'higher'
        elif int(master) < int(course):
            diff = 'lower'
        else:
            diff = 'same'
    else:
        diff = 'n/a'
    return DIFF[diff]


def add_plus_to_plus_handicaps(course_raw) -> str:
    course_handicap = ''
    if course_raw:
        if int(course_raw) < 0:
            course_handicap = "+ " + str(-int(course_raw))
        else:
            course_handicap = course_raw
    return course_handicap


def login_to_master_scoreboard() -> requests.Session:
    login_url = 'https://www.masterscoreboard.co.uk/SocietyIndex.php?CWID=' + MASTER_SCOREBOARD_CWID

    s = requests.Session()
    res = s.get(login_url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(res.content, features="html.parser")
    login_path = soup.find('form').get('action')
    params = soup.find('input', attrs={'name': 'Params'})['value']
    login_data = {
        'Params': params,
        'ms_password': MASTER_SCOREBOARD_PASSWORD
    }
    post_headers = {
        'Referer': 'https://www.masterscoreboard.co.uk/SocietyIndex.php?CWID=' + MASTER_SCOREBOARD_CWID,
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    full_login_url = 'https://www.masterscoreboard.co.uk/' + login_path
    s.post(full_login_url, data=login_data, headers={**DEFAULT_HEADERS, **post_headers})

    return s


def get_handicaps_from_master() -> dict[str, str]:
    session = login_to_master_scoreboard()
    response = session.get(MASTER_SCOREBOARD_HANDICAP_URL, headers=DEFAULT_HEADERS)
    handicap_soup = BeautifulSoup(response.content, features="html.parser")
    table = handicap_soup.find('table', id='desktophcaplist')
    bs = BeautifulSoup('<html>' + str(table) + '</html>', features="html.parser")
    results = {}
    for row in bs.select('tr')[1:]:
        name = get_master_scoreboard_name_from(row)
        results[name] = get_master_scoreboard_handicap_from(row)
    return results


def get_master_scoreboard_handicap_from(row) -> str:
    raw_from_html = row.select_one('td:nth-of-type(2)').text
    handicap = -golf_round(float(raw_from_html[1:])) if raw_from_html[0] == '+' else golf_round(float(raw_from_html))
    return str(handicap)


def get_master_scoreboard_name_from(row) -> str:
    return row.select_one('td').text.strip()


def golf_round(val: float) -> int:
    val_half_or_above = val % 1 >= 0.5
    return val.__ceil__() if val_half_or_above else round(val)


def get_handicaps_from_eg(names) -> dict[str, str]:
    session = login_to_eg()
    problem_names = {}
    eg_handicaps = {}
    for name in names:
        search_name = NAMES_MAPPING[name] if name in NAMES_MAPPING else name
        params = {'clubId': EG_CLUB_ID, 'searchName': search_name, 'userPassportId': ''}
        player = get_player_records(session, params)
        if len(player) > 1:
            handicaps = [pl['HandicapIndexText'] for pl in player]
            if handicaps.count('Pending') == len(handicaps) - 1:
                index = player[0]['HandicapIndexText']
                eg_handicaps[name] = str(convert_index_to_course(index))
                continue
            print("WARNING: too many results for search [" + name + "] on England Golf")
            problem_names[name] = 'England Golf - too many results when searching for player'
        elif len(player) == 1:
            index = player[0]['HandicapIndexText']
            if index != 'Pending':
                eg_handicaps[name] = str(convert_index_to_course(index))
            else:
                print("WARNING: Found player [" + name + "] with a pending handicap")
        else:
            print("WARNING: failed to find player with name [" + name + "] on England Golf")
            problem_names[name] = 'England Golf - no results when searching for player'
    write_problem_names_file(problem_names)
    return eg_handicaps


def write_problem_names_file(problem_names):
    if os.path.exists('problem-names.txt'):
        os.remove('problem-names.txt')
    with open('problem-names.txt', 'w') as file:
        for name, reason in problem_names.items():
            file.write(name + ': ' + reason + '\n')


def trim_names_from(master_handicaps):
    return list(map(str.strip, master_handicaps.keys()))


class MyEgSessionProblem(Exception):
    pass


class MyEgUnableToFindCtrTagsProblem(Exception):
    pass


def main():
    master_handicaps = get_handicaps_from_master()
    names = trim_names_from(master_handicaps)
    eg_handicaps = get_handicaps_from_eg(names)
    write_handicaps_to_files(master_handicaps, eg_handicaps)


if __name__ == '__main__':
    try:
        start = time.time()
        main()
        elapsed = time.time() - start
        print("Completed in " + str(round(elapsed, 2)) + " secs. Press any key to exit...")
        input()
    except BaseException:
        import sys

        print(sys.exc_info()[0])
        import traceback

        print(traceback.format_exc())
        print("Press Enter to continue ...")
        input()
