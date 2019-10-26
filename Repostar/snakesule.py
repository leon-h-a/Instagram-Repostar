#!/usr/bin/python
from backbone import Session
from time import sleep
import schedule
import EasyG
import os
import gc

user = os.path.basename(__file__)[:-3]

# VREMENA
vremena = Session.times(user)

print('Kao [' + user + '] objavljujem u: {}h i u {}h'.format(vremena[0], vremena[1]))

def job():
	while True:
		if EasyG.jobbanje(user):
			print('Geez, wrong img')
			sleep(2)
		else:
			print('Gotov za danas')
			break

schedule.every().day.at(vremena[0]).do(job)
if vremena[1] != ' None':
	schedule.every().day.at(vremena[1]).do(job)


while True:
    schedule.run_pending()
    sleep(1)
