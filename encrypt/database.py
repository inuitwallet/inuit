from hashlib import md5
import os

import encrypt.slowAes as aes
import io.inp as inp
import num.rand as rand
import system.db as db


def derive_key_and_iv(password, salt, key_length, iv_length):
	'''
		accept a password and salt and return hex key and iv values
	'''
	d = d_i = ''
	while len(d) < key_length + iv_length:
		d_i = md5(d_i + password + salt).digest()
		d += d_i
	return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(passW):
	'''
		encrypt the sqlite database
	'''
	#double check the password
	checkPass = inp.secure_passphrase('Please enter your database password')
	if checkPass != passW.password:
		print('Your passwords don\'t match')
		passW.getPass(True)
	print('Encrypting database. Please wait...')
	bs = 128
	inFile = 'igloo.dat'
	outFile = 'iceblock'
	if not os.path.isfile(inFile) and os.path.isfile(outFile):
		print('Database is already encrypted')
		return
	salt = str(rand.clockrnd())[:(bs - len('Salted__'))]
	in_file = open('igloo.dat', 'rb')
	out_file = open('iceblock', 'wb')
	key, iv = derive_key_and_iv(passW.password, salt, 32, bs)
	out_file.write('Salted__' + salt)
	finished = False
	while not finished:
		chunk = in_file.read(1024 * bs)
		if len(chunk) == 0 or len(chunk) % bs != 0:
			padding_length = (bs - len(chunk) % bs) or bs
			chunk += padding_length * chr(padding_length)
			finished = True
		out_file.write(aes.encryptData(key, chunk))
	in_file.close()
	out_file.close()
	os.remove(inFile)
	return

def decrypt(passW):
	'''
		decrypt the sqlite database
		retry if decryption fails
	'''
	bs = 128
	inFile = 'iceblock'
	outFile = 'igloo.dat'
	if os.path.isfile(outFile):
		passW.getPass(True)
	else:
		passW.getPass(False)
	in_file = open(inFile, 'rb')
	out_file = open(outFile, 'wb')
	print('Decrypting database. Please wait...')
	salt = in_file.read(bs)[len('Salted__'):]
	key, iv = derive_key_and_iv(passW.password, salt, 32, bs)
	next_chunk = ''
	finished = False
	while not finished:
		chunk, next_chunk = next_chunk, aes.decryptData(key, in_file.read(1024 * bs))
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1])
			chunk = chunk[:-padding_length]
			finished = True
		out_file.write(chunk)
	in_file.close()
	out_file.close()
	if db.testDec():
		os.remove(inFile)
		return True
	else:
		print('Incorrect password was entered')
		print('')
		os.remove(outFile)
		decrypt(passW)
		return False
