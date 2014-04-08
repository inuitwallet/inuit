import system.db as db

def showAddresses(cur):
	conn = db.open()
	c = conn.cursor()
	#get the current version of the currency
	c.execute('select version from inuit_currencies where currency=?;', (cur.upper(),))
	version = c.fetchone()
	c.execute('select a.address from inuit_addresses as a inner join inuit_currencies as c on a.currency = c.id inner join inuit_master as m on a.id = m.address where c.currency = ? and m.version=?;', (cur.upper(), version[0]))
	addresses = c.fetchall()
	db.close(conn)
	if not addresses:
		print('No addresses found for ' + cur.upper())
		return False
	print('')
	for address in addresses:
		print(str(address[0]).decode('base64', 'strict'))
	return True
	
def showCurrencies():
	conn = db.open()
	c = conn.cursor()
	c.execute('select c.id,c.currency,c.longName,v.version,v.id from inuit_currencies as c inner join inuit_versions as v on c.version=v.id order by c.currency;')
	currencies = c.fetchall()
	if not currencies:
		print('No currencies exist in the system')
		return False
	print('')
	for currency in currencies:
		c.execute('select count(a.id) from inuit_addresses as a inner join inuit_master as m on a.id = m.address where a.currency=? and m.version=?;', (currency[0],currency[4]))
		addr = c.fetchone()
		if addr is None:
			numAddr = 0
		else:
			numAddr = addr[0]
		print('{0: ^8}'.format(str(currency[1])) + '   |   ' + '{0: ^16}'.format(str(currency[2])) + '   |   ' + '{0:>4}'.format(str(currency[3])) + '   |   ' + '{0:>4}'.format(str(numAddr)))
	db.close(conn)
	return True
	
def help():
	print('')
	print('inuit - crypto-currency cold storage')
	print('')
	print('DISCLAIMER')
	print('##########')
	print('inuit comes as is.')
	print('No promises are made as to the suitability or security of the addresses it generates.')
	print('It is up to you to ensure the continued security of your crypto-currencies.')
	print('No liability is assumed by inuit or its creators.')
	print('')	
	print('== commands ==')
	print('')
	print('exit')
	print('  Quit inuit. (you can use ctrl+c too).')
	print('help')
	print('  Show this dialogue.') 
	print('gen <cur>')
	print('  Generate an address/private key pair for the supplied currency abbreviation.')
	print('  BIP38 encryption is an option.')
	print('dumpprivkey <address>')
	print('  View the private key for the given inuit generated address.')
	print('listaddr <cur>')
	print('  list the addresses which inuit has generated for the given currency abbreviation.')
	print('listcur')
	print('  List the currencies available in the inuit system.')
	print('addcur')
	print('  Add a new crypto-currency to your inuit system.')
	print('editcur')
	print('  Edit an existing crypto-currency.')
	print('exportcur')
	print('  Export your systems currency data to a currencies.json file')
	print('importcur')
	print('  Import a currencies.json currency data file into your system.')
	print('entropycheck')
	print('  Check your platform for a strong source of time based entropy.')
	print('setpass')
	print('  Set a new database encryption password.')
	print('')
	print('==============')
	return
	
