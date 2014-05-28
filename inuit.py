#!/usr/bin/env python
"""
inuit

Cold storage crypto-currency address generator

"""

import os.path
import sys

import encrypt.database as database
import io.list as list
import num.rand as rand
import system.address as address
import system.alts as alts
import system.data as data
import system.dbCreate as dbCreate
from system.settings import passW
passW = passW()

#build the database if it doesn't exist
if not os.path.isfile('igloo.dat') and not os.path.isfile('iceblock'):
	passW.setPass()
	dbCreate.buildDB()

else:
	if not os.path.isfile('igloo.dat') and os.path.isfile('iceblock'):
		#decrypt the database if the encrypted version exists
		database.decrypt(passW)
	else:
		#otherwise get the password so that password encryption can take place
		print('It looks like your database wasn\'t encrypted the last time you used inuit') 
		passW.getPass()
	
try:
	
	while True:
		
		print('')
		command = raw_input('Enter command >> ').strip().split()

		if len(command) < 1:
			continue
		
		elif command[0].lower() == 'exit':
			database.encrypt(passW)
			sys.exit()

		elif command[0].lower() == 'help':
			list.help()
			continue
			
		elif command[0].lower() == 'setpass':
			dbCreate.setPwd(2)
			continue
			
		elif command[0].lower() == 'dumpprivkey':
			if len(command) < 2:
				print('dumpprivkey requires an address as its first parameter')
				continue
			address.dumpPrivKey(command[1])
			continue		

		elif command[0].lower() == 'entropycheck':
			rand.platformCheck()
			continue

		elif command[0].lower() == 'listaddr':
			if len(command) < 2:
				print('listaddr requires a currency abbreviation as its first parameter')
				continue
			list.showAddresses(command[1])
			continue

		elif command[0].lower() == 'listcur':
			list.showCurrencies()
			continue

		elif command[0].lower() == 'addcur':
			if len(command) < 2:
				print('addcur requires a currency abbreviation as its first parameter')
				continue
			alts.addAlt(command[1])
			continue
			
		elif command[0].lower() == 'editcur':
			if len(command) < 2:
				print('editcur requires a currency abbreviation as its first parameter')
				continue
			alts.editAlt(command[1])
			continue
			
		elif command[0].lower() == 'importcur':
			data.importAlts()
			continue
			
		elif command[0].lower() == 'exportcur':
			data.exportAlts()
			continue

		elif command[0].lower() == 'gen':
			if len(command) < 2:
				print('gen requires a currency abbreviation as its first parameter')
				continue
			address.generate(command[1])
			continue
		
		#a couple of unit test functions here.
		#the first generates address and priv keys for all currencies in the system
		#the second does the same but with BIP38 encryption which it also tests
		elif command[0].lower() == 'genall':
			data.genAll()
			continue
			
		elif command[0].lower() == 'bipall':
			data.genAll(True)
			continue

		else:
			print(command[0] + ' was not recognised as a command')
			continue

except:
	#naughty I know but this should ensure that the database gets encrypted if an unforeseen error occurs
	if str(sys.exc_info()[0]) != '<type \'exceptions.SystemExit\'>':
		print('An unforeseen error occurred. Attempting to encrypt database.')
		database.encrypt(passW)
	sys.exit()
