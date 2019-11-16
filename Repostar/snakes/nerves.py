#!/usr/bin/python
from time import sleep
import requests
import json
import bs4
import sys
import os

def some_html(username, me):
    test_string = '{"config":{"csrf_token":'

    a = requests.get('https://www.instagram.com/' + str(username) + '/')
    sleep(1)
    soup = bs4.BeautifulSoup(a.text, 'html.parser')
    sleep(1)
    scripts = soup.find_all('script')
    sleep(1)
    modified = str(scripts[4])[:-10][52:]
    if test_string in modified:
        try:
            html = json.loads(modified)
        except ValueError:
            #  ValueError se najcesce pojavljuje ako user:
            #  1. ima privatan profil
            #  2. izbrisao je profil
            #  3. spelling greska u users.txt

            #  Spremi username u fix_users.txt
            with open(os.getcwd() + '/' + me + '/fix_users.txt', 'a+') as fix:
                already_inside = fix.read()
                if username not in already_inside:
                    fix.write(username + '\n')
                    print('Lazy is not good, fix_users.txt NOW!')
            return 0

    else:
        modified = str(scripts[3])[:-10][52:]
        try:
            html = json.loads(modified)
        except ValueError:
            #  Spremi username u fix_users.txt
            with open(os.getcwd() + '/' + me + '/fix_users.txt', 'a+') as fix:
                already_inside = fix.read()
                if username not in already_inside:
                    fix.write(username + '\n')
                    print('Lazy is not good, fix_users.txt NOW!')
            return 0

    if 'html' not in locals():
        print('Gasim program')
        sys.exit()
    return html

def me_html(me):
    a = requests.get('https://www.instagram.com/' + me + '/')
    soup = bs4.BeautifulSoup(a.text, 'html.parser')
    scripts = soup.find_all('script')
    modified = str(scripts[4])[:-10][52:]
    html = json.loads(modified)
    return html
