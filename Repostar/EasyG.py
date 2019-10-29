#!/usr/bin/python
from backbone import Session
import os
import urllib3
import warnings
import random


def jobbanje(user):

    path = str(os.getcwd()) + '/' + user + '/'

    # BLAH
    warnings.filterwarnings("ignore")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ZEMI PODATKE O USERU
    with open(path + 'data.txt', 'r') as file:
        row = file.read().splitlines()
        instagramUsername = row[0]
        instagramPassword = row[1]
        intro = row[2]
        htags = row[3]
        intro = intro.split(', ')
        htags = htags.split(', ')
        min_likes = row[4][10:]
        margin = row[5][7:]

    # ROKAVELA
    s = Session(user, path, random.choice(intro), htags, instagramUsername, instagramPassword, min_likes, margin)
    s.find_users_to_scrape()
    s.whitelist()
    for _ in s.users:
        if s.is_user_used_in_this_loop(_):
            continue
        if s.get_target_html(_):
            continue
        if s.find_most_liked(_):
            continue
        if s.is_picture_used(_):
            continue
        s.download_pic()
        if s.tensac(_):
            return True
        if s.upload(_):
            break
    s.loop_done()
    return False
