import os.path
import sqlite3


def open():
	return sqlite3.connect('igloo.dat')
	
def close(conn):
	conn.commit()
	conn.close()
	return True
	
def testDec():
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
	
