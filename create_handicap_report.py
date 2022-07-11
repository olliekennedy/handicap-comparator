#!/usr/bin/env python3
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import MASTER_SCOREBOARD_CWID, EG_CLUB_ID, MASTER_SCOREBOARD_PASSWORD, EG_MEMBERSHIP_NUMBER, EG_PASSWORD
from names_mapping import NAMES_MAPPING

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.0.0 Safari/537.36 '
}
MASTER_SCOREBOARD_HANDICAP_URL = 'https://www.masterscoreboard.co.uk/results/HandicapList.php?CWID=' + MASTER_SCOREBOARD_CWID
EG_PLAYER_SEARCH_API_URL = 'https://members.whsplatform.englandgolf.org/api/member/FindPotentialFriends'
EG_LOGIN_URL = 'https://members.whsplatform.englandgolf.org/layouts/terraces_golfnz/Template.aspx?page=my+golf+login'


def login_to_eg(email, password):
    session = requests.Session()
    login_soup = BeautifulSoup(session.get(EG_LOGIN_URL, headers=HEADERS).content, features="html.parser")
    login_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': (login_soup.find('input', attrs={'name': '__VIEWSTATE'})['value']),
        '__VIEWSTATEGENERATOR': (login_soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})['value']),
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        '__EVENTVALIDATION': (login_soup.find('input', attrs={'name': '__EVENTVALIDATION'})['value']),
        'ctl36$tbMembershipNumber': email,
        'ctl36$tbPassword': password,
        'ctl36$btnLogin': 'Login'
    }
    session.post(EG_LOGIN_URL, data=login_data)
    return session


def find_player(s, name):
    search_name = NAMES_MAPPING[name] if name in NAMES_MAPPING else name
    params = {'clubId': EG_CLUB_ID, 'searchName': search_name, 'userPassportId': ''}
    player = s.get(
        url=EG_PLAYER_SEARCH_API_URL,
        params=params
    )
    if len(json.loads(player.content)['Records']) > 1:
        print("WARNING: too many results for search " + name + " on England Golf")
    if not json.loads(player.content)['Records']:
        print("WARNING: failed to find player with name " + name + " on England Golf")

    return player


def convert_index_to_course(index, slope):
    course_hcp = int(round((float(index) * (float(slope)) / float(113))))
    return -course_hcp if index[0] == '+' else course_hcp


def get_course_handicap(player):
    index = json.loads(player.content)['Records'][0]['HandicapIndexText']
    return str(convert_index_to_course(index, 130))


def write_to_files(player_handicap_data):
    lines = []
    for name in player_handicap_data:
        lines.append(formatted_row_from(name, player_handicap_data))
    dataframe = pd.DataFrame(lines, columns=['Name', 'Course Handicap', 'Master Handicap', 'Master higher?'])
    dataframe.index = range(1, dataframe.shape[0] + 1)
    dataframe.to_excel('handicap-report.xlsx', index=False)


def formatted_row_from(name, player_handicap_data):
    course_raw = player_handicap_data[name]['course']
    master_raw = player_handicap_data[name]['master']
    diff = higher_or_lower(course_raw, master_raw)
    course_handicap = add_plus_to_plus_handicaps(course_raw)
    master_handicap = add_plus_to_plus_handicaps(master_raw)
    return [name, course_handicap, master_handicap, diff]


def higher_or_lower(course, master):
    if course and master:
        if int(master) > int(course):
            diff = 'Higher'
        elif int(master) < int(course):
            diff = 'Lower'
        else:
            diff = 'Same'
    else:
        diff = 'N / A'
    return diff


def add_plus_to_plus_handicaps(course_raw):
    course_handicap = ''
    if course_raw:
        if int(course_raw) < 0:
            course_handicap = "+ " + str(-int(course_raw))
        else:
            course_handicap = course_raw
    return course_handicap


def login_to_master_scoreboard():
    login_url = 'https://www.masterscoreboard.co.uk/SocietyIndex.php?CWID=' + MASTER_SCOREBOARD_CWID

    s = requests.Session()
    res = s.get(login_url, headers=HEADERS)
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
        'sec-ch-ua-platform': '"macOS"',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    full_login_url = 'https://www.masterscoreboard.co.uk/' + login_path
    s.post(full_login_url, data=login_data, headers=post_headers)

    return s


def get_handicaps_from_master():
    session = login_to_master_scoreboard()
    response = session.get(MASTER_SCOREBOARD_HANDICAP_URL, headers=HEADERS)
    handicap_soup = BeautifulSoup(response.content, features="html.parser")
    table = handicap_soup.find('table', id='desktophcaplist')
    bs = BeautifulSoup('<html>' + str(table) + '</html>', features="html.parser")
    results = {}
    for row in bs.select('tr')[1:]:
        handicap = row.select_one('td:nth-of-type(2)').text
        if handicap[0] == '+':
            handicap = str(-int(float(handicap[1:])))
        else:
            handicap = str(int(float(handicap)))
        results[row.select_one('td').text] = {'course': '', 'master': handicap}
    return results


def get_handicaps_from_eg(master_handicaps, names):
    session = login_to_eg(EG_MEMBERSHIP_NUMBER, EG_PASSWORD)
    problem_names = []
    for name in names:
        found_player = find_player(session, name)
        if len(json.loads(found_player.content)['Records']) == 1:
            master_handicaps[name]['course'] = get_course_handicap(found_player)
        else:
            problem_names.append(name)
    write_lines_to_file(problem_names)
    return master_handicaps


def write_lines_to_file(problem_names):
    if os.path.exists('problem-names.txt'):
        os.remove('problem-names.txt')
    with open('problem-names.txt', 'w') as file:
        for name in problem_names:
            file.write(name + '\n')


def main():
    master_handicaps = get_handicaps_from_master()
    names = master_handicaps.keys()
    player_handicap_data = get_handicaps_from_eg(master_handicaps, names)
    write_to_files(player_handicap_data)


if __name__ == '__main__':
    main()
