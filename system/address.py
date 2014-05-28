import hashlib

import io.inp as inp
import io.get as get
import encrypt.bip38 as bip38
import num.elip as elip
import num.enc as enc
import num.rand as rand
import system.db as db
import random

def privateKey2Wif(privateKey, version=0, prefix=1, length=0):
	"""
	convert a private key to WIF format
	"""
	return base58Encode(enc.encode(privateKey, 256, 32) + '\x01', (128+int(version)), prefix, length)


def privateKey2PublicKey(priv):
	"""
	integer 256 bit ECC private key to hexstring compressed public key
	"""
	pub = elip.base10_multiply(elip.G, priv)
	return '0' + str(2 + (pub[1] % 2)) + enc.encode(pub[0], 16, 64)


def publicKey2Address(publicKey, version=0, prefix=1, length=0):
	"""
	Compressed ECC public key hex to address
	"""
	return base58Encode(hashlib.new('ripemd160', hashlib.sha256(publicKey.decode('hex')).digest()).digest(), (0+version), prefix, length)


def base58Encode(r160, magicbyte=0, prefix=1, length=0):
	"""
	Base58 encoding w leading zero compact
	"""
	from re import match as re_match
	inp_fmtd = chr(int(magicbyte if magicbyte < 255 else 255)) + r160
	leadingzbytes = len(re_match('^\x00*', inp_fmtd).group(0))
	checksum = hashlib.sha256(hashlib.sha256(inp_fmtd).digest()).digest()[:4]
	return str(prefix) * leadingzbytes + enc.encode(enc.decode(inp_fmtd + checksum, 256), 58, 0)


def generate(cur, bip=False):
	"""
		public and private key generator.
		optional BIP0038 encryption
	"""
	#check that the given currency is in the system
	conn = db.open()
	c = conn.cursor()
	#pull the version details from the database
	c.execute('select v.version,v.prefix,v.length,c.id,c.longName,c.version from inuit_versions as v inner join inuit_currencies as c on c.version = v.id where c.currency=?;', (cur.upper(),))
	version = c.fetchone()
	if version is None:
		print(cur.upper() + ' is not currently listed as a currency')
		return False
	#randomly choose a prefix if multiples exist
	prefixes = version[1].split('|') 
	prefix = prefixes[random.randint(0, (len(prefixes)-1))] 
	#generate the private and public keys
	privateKey = rand.randomKey(inp.keyboardEntropy())
	privK256 = enc.encode(privateKey, 256, 32)
	publicAddress = publicKey2Address(privateKey2PublicKey(privateKey), version[0], prefix,  version[2])
	#optional BIP0038 encryption
	get.flushKeybuffer(get._Getch())
	encrypt = 'y'
	if encrypt == 'y':
		bipPass1 = 'pass1' 
		bipPass2 = 'pass2'
		while bipPass1 != bipPass2 or len(bipPass1) < 1:
			bipPass1 = inp.secure_passphrase('Enter your BIP0038 passphrase')
			bipPass2 = inp.secure_passphrase('Re-enter your passphrase to confirm')
			if bipPass1 != bipPass2:
				print('The passphrases entered did not match.')
			elif len(bipPass1) < 1:
				print('No passphrase was entered!')
		reminder = raw_input('Enter an optional reminder for your password : ').strip()
		#print('')
		#print('Enter the number of rounds of encryption.')
		#p = raw_input('A smaller number means quicker but less secure. (8) : ').strip()
		#p = 8 if p == '' else int(p)
		p = 8
		privK = bip38.encrypt(privK256, publicAddress, bipPass1, p)
		isBip = True
	else:
		privK = privateKey
		isBip = False
	#save details to the database
	c.execute('insert into inuit_privK (privK, currency) values (?,?);', (str(privK).encode('base64','strict'), version[3]))
	privKid = c.lastrowid
	c.execute('insert into inuit_addresses (address, currency) values (?,?);', (publicAddress.encode('base64','strict'), version[3]))
	addId = c.lastrowid
	c.execute('insert into inuit_master (address, privK, version) values (?,?,?);', (addId, privKid, version[5]))
	if isBip is True:
		c.execute('insert into inuit_bip (privK, reminder, p) values (?,?,?);', (privKid, reminder, p))
	db.close(conn)
	print('')
	print(version[4] + ' Address : ' + publicAddress)
	return privK, publicAddress

	
def dumpPrivKey(address):
	"""
		retrieve private key from database for given address
		option to decrypt BIP0038 encrypted keys
		display as base58 and WIF
	"""
	conn = db.open()
	c = conn.cursor()
	#get the needed data from the database
	c.execute('select p.id,p.privK,v.version,v.prefix,v.length,c.longName from inuit_privK as p inner join inuit_master as m on p.id = m.privK inner join inuit_addresses as a on a.id = m.address inner join inuit_currencies as c on p.currency = c.id inner join inuit_versions as v on c.version = v.id where a.address=?;', (address.encode('base64', 'strict'),))
	privData = c.fetchone()
	if privData is None:
		print(address + ' was not found')
		return False
	#check if the private key is bip encoded and get the password reminder if it is
	c.execute('select reminder, p from inuit_bip where privK=?;', (privData[0],))
	bip = c.fetchone()
	if bip is None:
		isBip = False
	else:
		isBip = True
		reminder = bip[0]
		p = bip[1]
	privK = privData[1].decode('base64', 'strict')
	#ask if the user wants to decrypt a bip encrypted key
	if isBip:
		#print('The private key found is BIP0038 encrypted.')
		decrypt = raw_input('Would you like to decrypt your private key? (n) ').lower().strip()
		if decrypt == 'y':
			bipPass1 = 'pass1' 
			bipPass2 = 'pass2'
			while bipPass1 != bipPass2 or len(bipPass1) < 1:
				bipPass1 = inp.secure_passphrase('Enter your BIP0038 passphrase ' + ('(' + bip[0] + ')' if bip[0] != '' else ''))
				bipPass2 = inp.secure_passphrase('Re-enter your passphrase to confirm')
				if bipPass1 != bipPass2:
					print('The passphrases entered did not match.')
				elif len(bipPass1) < 1:
					print('No passphrase was entered')
			#decrypt the private key using the supplied password
			privK, addresshash = bip38.decrypt(privK, bipPass1, p)
			#decode the privK from base 256
			privK = enc.decode(privK, 256)
			#hash the address to check the decryption
			address = publicKey2Address(privateKey2PublicKey(privK), privData[2], privData[3], privData[4])
			if hashlib.sha256(hashlib.sha256(address).digest()).digest()[0:4] != addresshash:
				print('\nUnable to decrypt.')
				print('Please try again with a different passphrase.')
				return False
		else:
			print('\n' + privData[5] + ' Address = ' + str(address))
			print('\nBIP0038 encrypted private key : ' + privK)
			return True	
	print('\n' + privData[5] + ' Address = ' + str(address))			
	print('\nPrivate key : ')
	print('HEX : ' + enc.encode(privK, 16))
	print('WIF : ' + privateKey2Wif(privK, privData[2], privData[3], privData[4]))
	return True
