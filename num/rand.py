import hashlib

import io.out as out
import num.elip as elip
import num.enc as enc

def clockbase():
	"""
	256 bit hex: 4 x 16 byte long from float using clock (process time) + time (UTC epoch time)
	Note: not enough clock precision on Linuxes to be unique between two immediate calls
	"""
	from struct import pack
	from time import time, clock

	return pack('<dddd', clock(), time(), clock(), time()).encode('hex')


def clockrnd():
	"""
	512 bit int: random delay while hashing data,
	return result of 192-1725 time-based hashes.
	execution time on 2.8GHz Core2: 1.8-15.7ms
	"""
	loopcount = 64 + int(hashlib.sha256(clockbase()).hexdigest()[:3], 16)/8  # 64-575 loops, random
	hash1 = hash2 = int(clockbase()+clockbase(), 16)
	for i in xrange(loopcount):
		hash1 ^= int(hashlib.sha512(clockbase() + hashlib.sha512(clockbase()).hexdigest()).hexdigest(), 16)
		hash2 ^= int(hashlib.sha512((hex(hash1)) + ('%d' % hash1)).hexdigest(), 16)
	return hash1 ^ hash2


def platformCheck(checks=1000):
	from collections import Counter
	print('Checking for good entropy')
	randList = []
	count = 0
	for zbit in xrange(checks):
		out.prnt('\b\b\b\b\b\b{0:4d}'.format(1000-count))
		count += 1
		randList.append(clockrnd())
	out.prnt('\b\b\b\b\b\b\b\b\b')
	duplicateCheck = Counter(randList).most_common(1)
	x, count = duplicateCheck[0]
	if count != 1:
		print('FAIL: time-based entropy is not always unique!')
		return False
	print('...pass')
	return True

def randomKey(entropy):
	"""
	256 bit number from equally strong urandom, user entropy, and timer parts
	"""
	if entropy.bit_length() < 250:
		print('Insufficent entropy parameter to generate key')
		return False
	from random import SystemRandom
	osrndi = SystemRandom()
	entstr = enc.encode(entropy, 16) + enc.encode(osrndi.getrandbits(512), 256) + str(clockrnd())
	osrnd = SystemRandom(entstr)
	privkey = 0
	while privkey < 1 or privkey > elip.N:
		privkey = enc.decode(hashlib.sha256(enc.encode(osrnd.getrandbits(512), 256)).digest(), 256) ^ osrnd.getrandbits(256)
		for lbit in xrange(clockrnd() % 64 + 64):
			clockstr = hex(clockrnd()) + str(clockrnd()) + entstr
			# Confused? These slice a moving 256 bit window out of SHA512
			clock32 = hashlib.sha512(clockstr).digest()[1+(lbit % 29): 33+(lbit % 29)]
			randhash = hashlib.sha512(enc.encode(osrnd.getrandbits(512), 256)).digest()[0+(lbit % 31): 32+(lbit % 31)]
			privkey ^= enc.decode(randhash, 256) ^ enc.decode(clock32, 256) ^ osrndi.getrandbits(256)
			osrnd = SystemRandom(hashlib.sha512(clock32 + randhash + entstr).digest())  # reseed
	return privkey
