def sxor(s1, s2):
	""" XOR strings
	"""
	return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))
	
	
import math

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
  """ encode v, which is a string of bytes, to base58.    
  """

  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += ord(c) << (8*i) # 2x speedup vs. exponentiation

  result = ''
  while long_value >= __b58base:
    div, mod = divmod(long_value, __b58base)
    result = __b58chars[mod] + result
    long_value = div
  result = __b58chars[long_value] + result

  # Bitcoin does a little leading-zero-compression:
  # leading 0-bytes in the input become leading-1s
  nPad = 0
  for c in v:
    if c == '\0': nPad += 1
    else: break

  return (__b58chars[0]*nPad) + result

def b58decode(v, length=None):
  """ decode v into a string of len bytes
  """
  long_value = 0L
  for (i, c) in enumerate(v[::-1]):
    long_value += __b58chars.find(c) * (__b58base**i)

  result = ''
  while long_value >= 256:
    div, mod = divmod(long_value, 256)
    result = chr(mod) + result
    long_value = div
  result = chr(long_value) + result

  nPad = 0
  for c in v:
    if c == __b58chars[0]: nPad += 1
    else: break

  result = chr(0)*nPad + result
  if length is not None and len(result) != length:
    return None

  return result
	
def get_code_string(base):
	if base == 16:
		return "0123456789abcdef"
	elif base == 58:
		return "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
	elif base == 256:
		return ''.join([chr(x) for x in range(256)])
	else:
		raise ValueError("Invalid base!")


def encode(val, base, minlen=0):
	code_string = get_code_string(base)
	result = ""
	val = int(val)
	while val > 0:
		result = code_string[val % base] + result
		val /= base
	if len(result) < minlen:
		result = code_string[0] * (int(minlen) - len(result)) + result
	return result


def decode(string, base):
	code_string = get_code_string(base)
	result = 0
	if base == 16:
		string = string.lower()
	while len(string) > 0:
		result *= base
		result += code_string.find(string[0])
		string = string[1:]
	return result
