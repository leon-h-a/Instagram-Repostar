#!/usr/bin/python
from time import sleep
import requests
import json
import bs4
import sys

def some_html(username):
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
            print('Provjeri spelling korisnickog imena i jel uopce postoji: {}'.format(username))

    else:
        modified = str(scripts[3])[:-10][52:]
        try:
            html = json.loads(modified)
        except ValueError:
            print('Provjeri spelling korisnickog imena i jel uopce postoji: {}'.format(username))

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
