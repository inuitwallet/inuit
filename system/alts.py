import system.db as db

def base58_to_hex(b58str):
	"""
	convert a base58 encoded string to hex
	"""
	n = 0
	b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	for s in b58str:
		n *= 58
		digit = b58_digits.index(s)
		n += digit
	return hex(n)
  	
def scan(privK, minimum=0):
	"""
	return the version of a currency which is encoded in the private key
	"""
	hexK = base58_to_hex(privK)
	prefix = hexK[0:3]
	i = 3
	while int(prefix, 16) < minimum:
		prefix += hexK[i]
		i += 1
	return int(prefix, 16)-minimum
  	
def addAlt(cur):
	"""
	add an alt currency to the inuit system.
	check if it already exists and prompt for a version number or private key if it doesn't
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select id from inuit_currencies where currency=?;', (cur.upper(),))
	if c.fetchone() is not None:
		print(cur.upper() + ' already exists in the system')
		db.close(conn)
		return
	longName = raw_input('Enter the full name of the currency : ').capitalize().strip()
	if longName == '':
		print('Currencies need a full name')
		db.close(conn)
		return False
	versionString = raw_input('Enter a private key or version number for ' + cur.upper() + ' : ').strip()
	if versionString == '':
		print('No data was entered')
		db.close(conn)
		return False
	#decide what we're dealing with
	if len(versionString) <= 3:
		#length of the string is up to 3 characters, it's a version number
		version = int(versionString)
	elif len(versionString) > 30 and len(versionString) < 35:
		#between 30 and 35 length, it's an address
		version = scan(versionString)
	elif len(versionString) > 50:
		#over 50 length, it's a private key
		version = scan(versionString, 128)
	else:
		print(versionString + ' doesn\'t look like an address or private key and is too long to be a version number.')
		db.close(conn)
		return False
	#all version from 145-255 have the same prefix etc.
	#we only store up to 145 in the database
	versionInt = version if version < 145 else 145
	c.execute('select id from inuit_versions where version=?;', (versionInt,))
	versionId = c.fetchone()
	if versionId is None:
		print('Version ' + str(versionId[0]) + ' does not exist in the system')
		db.close(conn)
		return
	c.execute('insert into inuit_currencies (currency, longName, version) values (?,?,?);', (cur.upper(), longName, versionId[0]))
	print(longName + ' is version ' + str(version))
	db.close(conn)
	return
	
def editAlt(cur):
	"""
	edit a currency that is already in the system
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select c.id,c.currency,c.longName,v.version from inuit_currencies as c inner join inuit_versions as v on c.version = v.id where c.currency=?;', (cur.upper(), ))
	curId = c.fetchone()
	if curId is None:
		print(cur.upper() + ' doesn\'t exist in the system')
		db.close(conn)
		return False
	newCur = raw_input('Enter the new currency abbreviation (' + curId[1] + ') : ').upper().strip()
	newCur = curId[1] if newCur == '' else newCur
	newLongName = raw_input('Enter the new full name (' + curId[2] + ') : ').capitalize().strip()
	newLongName = curId[2] if newLongName == '' else newLongName
	versionString = raw_input('Enter a private key or version number for ' + newCur.upper() + ' (' + str(curId[3]) + ') : ').strip()
	if versionString == '':
		version = curId[3]
	#decide what we're dealing with
	elif len(versionString) > 0 and len(versionString) <= 3:
		#length of the string is up to 3 characters, it's a version number
		version = int(versionString)
	elif len(versionString) > 30 and len(versionString) < 35:
		#between 30 and 35 length, it's an address
		version = scan(versionString)
	elif len(versionString) > 50:
		#over 50 length, it's a private key
		version = scan(versionString, 128)
	else:
		print(versionString + ' doesn\'t look like an address or private key and is too long to be a version number.')
		version = curId[3]
	versionInt = version if version < 145 else 145
	c.execute('select id from inuit_versions where version=?;', (versionInt,))
	versionDb = c.fetchone()
	if versionDb is None:
		print('Version ' + str(version) + ' does not exist in the system')
		return False
	else:
		newVersion = versionDb[0]
	c.execute('update inuit_currencies set currency=?, longName=?, version=? where id=?;', (newCur, newLongName, newVersion, curId[0]))
	db.close(conn)
	print(newCur + ' saved as version ' + str(version))
	return True
