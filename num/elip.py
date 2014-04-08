### Elliptic curve math - pybitcointools

#P = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
P = 115792089237316195423570985008687907853269984665640564039457584007908834671663
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
A = 0
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)


def inv(a, n):
	lm, hm = 1, 0
	low, high = a % n, n
	while low > 1:
		r = high / low
		nm, new = hm - lm * r, high - low * r
		lm, low, hm, high = nm, new, lm, low
	return lm % n


def isinf(p):
	return p[0] == 0 and p[1] == 0


def base10_add(a, b):
	if isinf(a):
		return b[0], b[1]
	if isinf(b):
		return a[0], a[1]
	if a[0] == b[0]:
		if a[1] == b[1]:
			return base10_double((a[0], a[1]))
		else:
			return 0, 0
	m = ((b[1] - a[1]) * inv(b[0] - a[0], P)) % P
	x = (m * m - a[0] - b[0]) % P
	y = (m * (a[0] - x) - a[1]) % P
	return x, y


def base10_double(a):
	if isinf(a):
		return 0, 0
	m = ((3 * a[0] * a[0] + A) * inv(2 * a[1], P)) % P
	x = (m * m - 2 * a[0]) % P
	y = (m * (a[0] - x) - a[1]) % P
	return x, y


def base10_multiply(a, n):
	if isinf(a) or n == 0:
		return 0, 0
	if n == 1:
		return a
	if n < 0 or n >= N:
		return base10_multiply(a, n % N)
	if (n % 2) == 0:
		return base10_double(base10_multiply(a, n / 2))
	if (n % 2) == 1:
		return base10_add(base10_double(base10_multiply(a, n / 2)), a)