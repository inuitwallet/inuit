import hashlib

import io.get as get
import io.out as out
import num.rand as rand

def secure_passphrase(msg):
	progress_step = 0
	pretty_progress = ['\b@', '\b#', '\b*', '\b!']
	keypress = get._Getch()
	single_key = passw = ''
	out.prnt(msg + ' :  ')
	
	while single_key != "\n" and single_key != chr(13):
		while True:
			single_key = keypress()
			if single_key != '':
				break
	   
		if single_key != "\n" and single_key != chr(13):
			passw += single_key
		out.prnt(pretty_progress[progress_step % 4])
		progress_step += 1
	print('\b')
	return passw
	
def keyboardEntropy(keynum=64):
	"""
	512 bit random number from keyboard and keypress timer
	"""

	keypress = get._Getch()
	typed = kr = 'Press some keys to generate a secure address...'
	hashes = rand.clockrnd()
	print(kr)
	for step in range(keynum, 0, -1):
		for cnt in xrange(10000000):  # only loops on OSX
			hashes ^= rand.clockrnd()
			kr = keypress()
			get.flushKeybuffer(keypress)
			if kr != '':
				break
		typed += kr
		hashes ^= rand.clockrnd()
		out.prnt('\b\b\b\b\b\b{0:4d}\b\b\b\b\b'.format(step-1))
	get.flushKeybuffer(keypress)
	out.prnt('\b\b\b\b\b\b{0:4s}\b\b\b\b\b\n'.format('  OK'))
	get.flushKeybuffer(keypress)
	return hashes ^ int(hashlib.sha512(typed*8).hexdigest(), 16)
