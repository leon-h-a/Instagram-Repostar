#!/usr/bin/python
from InstagramAPI import InstagramAPI
from nerves import some_html
from nerves import me_html
from emoji import emojize
import tensorflow as tf
from time import sleep
from io import open
import datetime
import sqlite3
import urllib
import os
import re


class Session:
    def __init__(self, me, path, intro, htags, ig_user, ig_pass, min_likes, margin):
        self.margin = margin
        self.img_dir = path
        self.someone = 0
        self.me = me
        self.all_image_urls = []
        self.all_image_likes = []
        self.urls_n_likes = []
        self.posts = 0
        self.followers = 0
        self.following = 0
        self.most_liked = 0
        self.user_num = 0
        self.pic_num = 0
        self.done = False
        self.mot_liked_cap = 0
        self.captions = []
        self.user_used = None
        self.instagramUsername = ig_user
        self.instagramPassword = ig_pass
        self.intro = intro
        self.my_htags = htags
        self.users = []
        self.min_likes = min_likes
        self.intro = intro
        self.my_htags = htags
        self.my_html = me_html(self.me)
        self.will_post_it = None
        self.downloaded = None
        self.low_like = False
        self.whitelist_users = []

    def whitelist(self):
        #  define users that don't need to pass min_likes value
        '''
        users are defined by adding " +" after their username in users.txt
        '''
        with open(self.img_dir + 'users.txt') as users_file:
            users = users_file.read().splitlines()
            for _ in users:
                if ' +' in str(_):
                    self.whitelist_users.append(_.strip(' +'))

        if not self.whitelist_users:
            print('Not a single user is whitelisted')
        else:
            print('--- Whitelisted guys ---')
            print(*self.whitelist_users, sep = '\n')


    #  PROVJERI DAL thisLoop ODGOVARA SUMI SVIH USERA, AKO DA, KRENI ISPOCETKA SA VRHA POPISA
    def loop_done(self):
        with open(self.img_dir + 'users.txt') as users_file:
            users = users_file.read().strip(' +').splitlines()

        with open(self.img_dir + 'thisLoop.txt') as loop_file:
            loop_users = loop_file.read().splitlines()
        i = 0
        for _ in users:
            for one in loop_users:
                if one == _:
                    i += 1

        if i == len(users):
            print('\nGotov sa svim korisnicima, brisem thisLoop.txt')
            print('thisLoop.txt izbirsan i pocinjem ispocetka')

            '''OVO PREBACIT U .db + dodat racunjanja'''
            # with open(self.img_dir + 'underperforming.txt') as unders:
            #     unders.write('\n\n\n')

            os.remove(self.img_dir + 'thisLoop.txt')
        else:
            print('Ima jos korisnika')

    #  UZMI PAGE SOURCE OD METE
    def get_target_html(self, someone_html):
        self.someone_html = some_html(someone_html)

    #  IZ PAGE SURCE UZMI BROJ LAJKOVA ZADNJIH 10 SLIKA
    def all_image_like_count(self):
        for _ in range(10):
            self.all_image_likes.append(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['edge_liked_by']['count'])
        return self.all_image_likes

    #  UZMI 10 x 1080px SLIKA
    def all_image_urls_count(self):
        for _ in range(10):
            self.all_image_urls.append(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['display_url'])
        return self.all_image_urls

    #  SORTIRAJ LIKE CNT + LINK OD NAJVECEG DO NAJNIZE
    def find_most_liked(self, user):
        self.captions = []
        self.all_image_urls = []
        self.all_image_likes = []

        try:
            for _ in range(10):
                img_type = str(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['__typename'])
                if img_type == 'GraphImage':
                    self.all_image_likes.append(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['edge_liked_by']['count'])
                    self.all_image_urls.append(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['display_url'])
                    self.captions.append(self.someone_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][_]['node']['edge_media_to_caption']['edges'][0]['node']['text'])
                else:
                    print('[{}] Objava broj {} je video ili album, preskacem ju'.format(user, _))
                    continue

        except IndexError:
            print('[' + user + '] Slika broj: ' + str(_+1) + ' nema opisa, izlazim...')
            return True

        for _ in range(len(self.all_image_urls)):
            self.urls_n_likes.append(self.all_image_likes[_])
            self.urls_n_likes.append(self.all_image_urls[_])

        list1, list2, list3 = zip(*sorted(zip(self.all_image_likes, self.all_image_urls, self.captions)))

        #  check if user is whitelisted, if not, examine if above min_likes variable
        for _ in self.whitelist_users:
            if _ == user:
                print('User is whitelisted going forward with his best unused pic')
                return False

        if int(list1[-1]) >= int(self.min_likes):
            print('[{}] Najpopularnija slika ima {} lajkova (>{}). Prolazi'.format(user, list1[-1], self.min_likes))
            self.most_liked = list2[-1]
            self.most_liked_caption = list3[-1]
            return False
        else:
            print('[{}] Najpopularnija slika ima {} lajkova (<{}). Preskacem'.format(user, list1[-1], self.min_likes))
            return True

    #  POKUPI MOJ BROJ: PRATITELJA / PRATIOCA / OBJAVA
    def my_stats(self):
        self.followers = int(self.my_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count'])
        self.following = int(self.my_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count'])
        self.posts = int(self.my_html['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count'])

        if not os.path.exists(self.img_dir + 'myStats.txt'):
            print('Making text file path/myStats.txt')
            os.makedirs(self.img_dir + 'myStats.txt')

        tmp_list = []
        tmp_list.append(datetime.date.today())

        stats = open(self.img_dir + 'myStats.txt', 'a+')
        stats.write(str(tmp_list[0]) + '\tPOSTOVI: ' + str(self.posts) + '\n\t\tPRATITELJI: ' + str(self.followers) + '\n\t\tPRATI: ' + str(self.following) + '\n\n')
        stats.close()

        return (self.posts, self.followers, self.following)

    #  PROVJERI DAL SE SORTIRANA SLIKA NALAZI U BAZI OBJAVLJENIH
    def is_picture_used(self, user):
        if not os.path.exists(self.img_dir + self.me + '.db'):
            raise FileNotFoundError('Baza ne postoji napravi ju (format je <instagramUsername.db>)')

        conn = sqlite3.connect(self.img_dir + self.me + '.db')
        c = conn.cursor()

        c.execute("SELECT short_url FROM Reposter")
        urls = c.fetchall()

        for _ in urls:
            if _[0] == str(self.most_liked[-85:][:-45]):
                print('[' + user + '] Slika vec objavljena, prelazim na sljedeceg korisnika')
                return True

        conn.commit()
        conn.close()

    #  SKINI SLIKU
    def download_pic(self):
        urllib.request.urlretrieve(self.most_liked, self.img_dir + 'images/' + str(self.most_liked)[-85:][:-45] + '.jpg')

    #  UCITAJ SVE KORISNIKE
    def find_users_to_scrape(self):
        if not os.path.exists(self.img_dir + 'users.txt'):
            print('Please provide users to scrape in path/users.txt')
        with open(self.img_dir + 'users.txt', 'r', encoding='utf-8') as scrape_them:
            users = scrape_them.read().splitlines()
            for _ in users:
                self.users.append(_.strip(' +'))

    #  PROVJERI DAL JE KORISNIK VEC SCRAPE-AN U OVOM KRUGU
    def is_user_used_in_this_loop(self, user):
        header = '\n' + 30 * '-' + '[' + user + ']'
        print(header + (70 - len(header)) * '-')
        if not os.path.exists(self.img_dir + 'thisLoop.txt'):
            os.mknod(self.img_dir + 'thisLoop.txt')
            print('thisLoop.txt je kreiran')

        with open(self.img_dir + 'thisLoop.txt', 'r') as loop_file:
            users = loop_file.read().splitlines()
        for one in users:
            if str(one + '\n') == user or str(one) == user:
                print('Korisnik vec odraden u ovom krugu')
                return True
        with open(self.img_dir + 'thisLoop.txt', 'a') as loop_file:
            loop_file.write(user + '\n')

    #  OBJAVI SLIKU
    def upload(self, user):
        pattern = re.compile(r'#')
        matches = len(pattern.findall(self.most_liked_caption))
        mah_htags = ''
        num_of_my_htags = 30 - matches

        if num_of_my_htags >= 10:
            num_of_my_htags = 10
            for one in range(num_of_my_htags):
                mah_htags = mah_htags + str(self.my_htags[one])
            caption = emojize(self.intro + '\n:snake: Credit @' + str(user) + ': ' + self.most_liked_caption + mah_htags[:-1] + '\n:four_leaf_clover:\n' + 15 * ' :four_leaf_clover: ' + '\nChance for a FREE shoutout if you tag @' + self.instagramUsername + ' or use #' + self.instagramUsername, use_aliases=True)

        elif num_of_my_htags <= 3:
            caption = emojize(self.intro + '\n:snake: Credit @' + str(user) + ': ' + self.most_liked_caption + '\n:four_leaf_clover:\n' + 15 * ' :four_leaf_clover: ' + '\nChance for a FREE shoutout if you tag @' + self.instagramUsername + ' or use #' + self.instagramUsername, use_aliases=True)

        else:
            for one in range(num_of_my_htags):
                mah_htags = mah_htags + str(self.my_htags[one])

            caption = emojize(self.intro + '\n:snake: Credit @' + str(user) + ': ' + self.most_liked_caption + mah_htags[:-1] + '\n:four_leaf_clover:' + 15 * ' :four_leaf_clover: ' + '\nChance for a FREE shoutout if you tag @' + self.instagramUsername + ' or use #' + self.instagramUsername, use_aliases=True)

        image = self.img_dir + '/images/' + str(self.most_liked)[-85:][:-45] + '.jpg'
        ig = InstagramAPI(self.instagramUsername, self.instagramPassword)
        ig.login()
        ig.uploadPhoto(image, caption=caption)
        # PROVJERI JEL BAZA POSTOJI, AKO NE, NAPRAVI JU
        if not os.path.exists(self.img_dir + str(self.me) + '.db'):
            database = sqlite3.connect(self.me + '.db')
            c = database.cursor()
            c.execute('''CREATE TABLE Reposter
                        (user, short_url, full_url, time)''')
            print('Database created')
            database.close()
        else:
            print('Database already exists')

        # UNESI PODATKE U BAZU
        database = sqlite3.connect(self.img_dir + self.me + '.db')
        c = database.cursor()
        c.execute("INSERT INTO Reposter VALUES('{}', '{}', '{}', '{}')".format(user, str(self.most_liked[-85:][:-45]), str(self.most_liked), str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))))
        database.commit()
        database.close()
        print('Database entry done')

        # IZBRISI SLIKU
        os.remove(self.img_dir + '/images/' + str(self.most_liked)[-85:][:-45] + '.jpg')
        return True

    def tensac(self, user):
        # PATH SLIKE ZA PROVJERIT
        image_path = self.img_dir + '/images/' + str(self.most_liked)[-85:][:-45] + '.jpg'
        # UCITAJ U SLIKU image_data
        image_data = tf.gfile.FastGFile(image_path, 'rb').read()
        label_lines = [line.rstrip() for line in tf.gfile.GFile(self.img_dir + 'tensor/retrained_labels.txt')]
        # GRAF IZ FAJLA
        with tf.gfile.FastGFile(self.img_dir + 'tensor/retrained_graph.pb', 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            # UBACI image_data KAO input ZA GRAF I DOBIJ REZULTAT
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

            predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

            print(10 * '-' + user + 10 * '-')

            blah1 = []
            blah2 = []

            for node_id in top_k:
                human_string = label_lines[node_id]
                blah1.append(human_string)
                score = predictions[0][node_id]
                blah2.append(score)
                print('%s (score = %.5f)' % (human_string, score))

            print('Na slici je: ' + str(blah1[0]) + ' i ovoliko sam siguran: ' + str(blah2[0] * 100))


            if str(blah1[0]) == 'snake' and int(blah2[0] * 100) >= int(self.margin):
                print('Tako da bum objavio')
            else:
                print('Tako da bome nebum objavio')
                os.remove(self.img_dir + '/images/' + str(self.most_liked)[-85:][:-45] + '.jpg')
                print('Restartam program')
                return True
