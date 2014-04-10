import json
import os.path
import sqlite3
import system.db as db


def exportAlts():
	conn = db.open()
	c = conn.cursor()
	c.execute('select c.currency, c.longName, v.version from inuit_currencies as c inner join inuit_versions as v on c.version = v.id order by c.longName;')
	currencies = c.fetchall()
	db.close(conn)
	currs = []
	for cur in currencies:
		currs.append({'currency': str(cur[0]), 'longName': str(cur[1]), 'version': int(cur[2])}) 
	with open('currencies.json', 'w') as outfile:
		json.dump(currs, outfile)
	print('exported all currency data')
	return True

def importAlts():
	if not os.path.isfile('currencies.json'):
		print('no currencies.json file in your inuit directory')
		return False
	with open('currencies.json', 'r') as dataFile:
		currencies = json.load(dataFile)
	conn = db.open()
	c = conn.cursor()
	for cur in currencies:
		version = cur['version'] if cur['version'] < 145 else 145
		c.execute('select id from inuit_versions where version=?;', (version,))
		versionId = c.fetchone()
		if versionId is None:
			continue
		c.execute('select id from inuit_currencies where currency=?;', (cur['currency'],))
		curId = c.fetchone()
		if curId is None:
			#currency doesn't exist in the system so add it
			c.execute('insert into inuit_currencies (currency, longName, version) values (?,?,?);', (cur['currency'], cur['longName'], versionId[0]))
		else:
			c.execute('update inuit_currencies set currency=?, longName=?, version=? where id=?;', (cur['currency'], cur['longName'], versionId[0], curId[0]))
	db.close(conn)
	print('import finished')
	return True
	
#This function is a debugging function.
#It allows me to generate an address and private key for each currency to test the import into their wallets.
def genAll(bip=False):
	import random
	import num.rand as rand
	import system.address as address
	import num.enc as enc
	import encrypt.bip38 as bip38
	import hashlib
	
	genFile = open('allKeys', 'w')
	genFile.close()
	
	conn = db.open()
	c = conn.cursor()
	c.execute('select currency from inuit_currencies order by currency;')
	currencies = c.fetchall()
	for cur in currencies:
		c.execute('select v.version,v.prefix,v.length,c.id,c.longName from inuit_versions as v inner join inuit_currencies as c on c.version = v.id where c.currency=?;', (cur[0].upper(),))
		version = c.fetchone()
		if version is None:
			continue
		#randomly choose a prefix if multiples exist
		prefixes = version[1].split('|') 
		prefix = prefixes[random.randint(0, (len(prefixes)-1))] 
		#generate the private and public keys
		privateKey = rand.randomKey(random.getrandbits(512))
		privK256 = enc.encode(privateKey, 256, 32)
		WIF = address.privateKey2Wif(privateKey, version[0], prefix,  version[2])
		publicAddress = address.publicKey2Address(address.privateKey2PublicKey(privateKey), version[0], prefix,  version[2])
		if bip is True:
			BIP = bip38.encrypt(privK256, publicAddress, 'biptest', 1)
			privK, addresshash = bip38.decrypt(BIP, 'biptest', 1)
			#decode the privK from base 256
			privK = enc.decode(privK, 256)
			#hash the address to check the decryption
			addr = address.publicKey2Address(address.privateKey2PublicKey(privK), version[0], prefix,  version[2])
			fail = False
			if hashlib.sha256(hashlib.sha256(addr).digest()).digest()[0:4] != addresshash:
				fail = True
				reason = 'Address Hash doesn\'t match'
			if privK != privateKey:
				fail = True
				reason = 'Private Keys don\'t match'
			BIPWIF =  address.privateKey2Wif(privK, version[0], prefix,  version[2])
		with open('allKeys', 'a') as outfile:
			outfile.write('####### ' + cur[0].upper() + ' - ' + version[4] + ' #######\n')
			outfile.write('Address = ' + publicAddress + '\n')
			outfile.write('WIF     = ' + WIF + '\n')
			if bip is True:
				outfile.write('BIP     = ' + BIP + '\n')
				if fail is True:
					outfile.write('BIP Failed - ' + reason + '\n')
				else:
					outfile.write('BIPWIF  = ' + BIPWIF + '\n')
			outfile.write('\n')
		outfile.close()
	db.close(conn)
	return True