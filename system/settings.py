import io.inp as inp
import time

class passW:
	
	password = ''
	
	def setPass(self):
		print('Welcome to inuit')
		time.sleep(1)
		print('To encrypt your database please enter a password.')
		time.sleep(1)
		print('Keep this password safe as it is not stored anywhere.')
		time.sleep(1)
		print('If you loose it, you will loose access to all of your private keys')
		print('')
		time.sleep(1)
		self.getPass(True)
		print('Your password has been set')
		return
	
	def getPass(self, confirm=False):
		self.password = inp.secure_passphrase('Enter your database password')
		if confirm is True:
			pass2 = inp.secure_passphrase('Enter it again to confirm')
			if self.password != pass2:
				print('The passwords did not match')
				self.getPass(True)
				return
		return self.password
		
	def editPass(self):
		currentpass = inp.secure_passphrase('Enter your current password')
		if currentpass != self.password:
			print('Incorrect password entered')
			return
		self.getPass(True)
		print('password changed')
		return
		
		
