import os.path
import sqlite3


def open():
	"""
	open the database connection
	"""
	return sqlite3.connect('igloo.dat')
	
def close(conn):
	"""
	close the given connection
	"""
	conn.commit()
	conn.close()
	return True
	
def testDec():
	"""
	test the encryption state of the database file
	"""
	if os.path.isfile('igloo.dat'):
		conn = open()
		c = conn.cursor()
		try:
			c.execute('select * from inuit_versions where id=?;', (1,))
		except sqlite3.Error, e:
			if e.args[0] == 'file is encrypted or is not a database':
				return False
			else:
				print(e)
				return False
		return True
	else:
		return False
	
