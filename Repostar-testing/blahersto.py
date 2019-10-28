#!/usr/bin/python
from backbone import Session
from time import sleep
import schedule
import EasyG
import os

#  POPIS VREMENA U KOJIMA BOT OBJAVLJUJE
vremena = ['00:00', '08:00', '15:00']
vremena.sort()

user = os.path.basename(__file__)[:-3]
print('Kao [' + user + '] objavljujem u ' + str(vremena))

def job():
	while True:
		if EasyG.jobbanje(user):
			print('Dunno what does but works')
			sleep(2)
		else:
			print('Jedan manje, keep it up')
			break

job()

#  TERMINI OBAJVA IDU OD NAJRANIJEG DO NAJKASNIJEG VREMENA
# for vrijeme in vremena:
#     schedule.every().day.at(vrijeme).do(job)
#
# while True:
#     schedule.run_pending()
#     sleep(1)
