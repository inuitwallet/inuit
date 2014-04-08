# pbkdf2/scrypt
# Copyright (c) 2011 Allan Saddi <allan@saddi.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import hashlib
import hmac
import struct

DEFAULT_DIGESTMOD = hashlib.sha1


def f(password, salt, itercount, i, digestmod):
    u = hmac.new(password, salt + struct.pack('>i', i), digestmod).digest()
    result = [ord(x) for x in u]
    for j in range(1, itercount):
        u = hmac.new(password, u, digestmod).digest()
        u_result = [ord(x) for x in u]
        for x in range(len(u_result)):
            result[x] ^= u_result[x]
    return ''.join([chr(x) for x in result])


def pbkdf(password, salt, itercount, dklen, digestmod=DEFAULT_DIGESTMOD, digest_size=None):
    if digest_size is None:
        digest_size = digestmod().digest_size
    if dklen > (2**32-1) * digest_size:
        raise ValueError('derived key too long')
    l = (dklen + digest_size - 1) / digest_size
    dk = []
    for i in range(1, l+1):
        dk.append(f(password, salt, itercount, i, digestmod))
    return ''.join(dk)[:dklen]

# Scrypt

from itertools import izip
MASK32 = 2**32-1
BLOCK_WORDS = 16


def rotl(n, r):
    return ((n << r) & MASK32) | ((n & MASK32) >> (32 - r))


def doubleround(x):
    x[4] ^= rotl(x[0]+x[12], 7)
    x[8] ^= rotl(x[4]+x[0], 9)
    x[12] ^= rotl(x[8]+x[4], 13)
    x[0] ^= rotl(x[12]+x[8], 18)
    x[9] ^= rotl(x[5]+x[1], 7)
    x[13] ^= rotl(x[9]+x[5], 9)
    x[1] ^= rotl(x[13]+x[9], 13)
    x[5] ^= rotl(x[1]+x[13], 18)
    x[14] ^= rotl(x[10]+x[6], 7)
    x[2] ^= rotl(x[14]+x[10], 9)
    x[6] ^= rotl(x[2]+x[14], 13)
    x[10] ^= rotl(x[6]+x[2], 18)
    x[3] ^= rotl(x[15]+x[11], 7)
    x[7] ^= rotl(x[3]+x[15], 9)
    x[11] ^= rotl(x[7]+x[3], 13)
    x[15] ^= rotl(x[11]+x[7], 18)
    x[1] ^= rotl(x[0]+x[3], 7)
    x[2] ^= rotl(x[1]+x[0], 9)
    x[3] ^= rotl(x[2]+x[1], 13)
    x[0] ^= rotl(x[3]+x[2], 18)
    x[6] ^= rotl(x[5]+x[4], 7)
    x[7] ^= rotl(x[6]+x[5], 9)
    x[4] ^= rotl(x[7]+x[6], 13)
    x[5] ^= rotl(x[4]+x[7], 18)
    x[11] ^= rotl(x[10]+x[9], 7)
    x[8] ^= rotl(x[11]+x[10], 9)
    x[9] ^= rotl(x[8]+x[11], 13)
    x[10] ^= rotl(x[9]+x[8], 18)
    x[12] ^= rotl(x[15]+x[14], 7)
    x[13] ^= rotl(x[12]+x[15], 9)
    x[14] ^= rotl(x[13]+x[12], 13)
    x[15] ^= rotl(x[14]+x[13], 18)


def salsa20_8_core(x):
    z = list(x)
    for i in range(4):
        doubleround(z)
    for i in range(16):
        z[i] = (z[i] + x[i]) & MASK32
    return z


def blockmix_salsa20_8(b, r=8):
    y = [None]*(2 * r * BLOCK_WORDS)
    even = 0
    odd = r * BLOCK_WORDS
    t = b[(2 * r - 1) * BLOCK_WORDS:]

    for i in range(0, 2 * r * BLOCK_WORDS, 2 * BLOCK_WORDS):
        for j in range(BLOCK_WORDS):
            t[j] ^= b[i + j]
        y[even:even+BLOCK_WORDS] = t = salsa20_8_core(t)
        even += BLOCK_WORDS

        for j in range(BLOCK_WORDS):
            t[j] ^= b[i + BLOCK_WORDS + j]
        y[odd:odd+BLOCK_WORDS] = t = salsa20_8_core(t)
        odd += BLOCK_WORDS
    return y


def from_littleendian(b):
    return ord(b[0]) | (ord(b[1]) << 8) | (ord(b[2]) << 16) | (ord(b[3]) << 24)


def to_littleendian(w):
    return [chr(w & 0xff),
            chr((w >> 8) & 0xff),
            chr((w >> 16) & 0xff),
            chr((w >> 24) & 0xff)]


def smix(b, n, r=8):
    x = [from_littleendian(b[i:i+4]) for i in range(0, len(b), 4)]
    v = []
    for i in range(n):
        v.append(x)
        x = blockmix_salsa20_8(x, r=r)
    for i in range(n):
        j = x[-BLOCK_WORDS] % n

        t = []
        for xk, vjk in izip(x, v[j]):
            t.append(xk ^ vjk)
        x = blockmix_salsa20_8(t, r=r)
    out = []
    for x in x:
        out.extend(to_littleendian(x))
    return ''.join(out)


def scrypt(password, salt, n, r, p, buflen=64):
    mflen = 2 * r * 4 * BLOCK_WORDS
    t = pbkdf(password, salt, 1, p * mflen, digestmod=hashlib.sha256)
    b = []

    while t:
        b.append(t[:mflen])
        t = t[mflen:]

    for i in range(p):
        print('Stage ' + str(i+1) + ' of ' + str(p))
        b[i] = smix(b[i], n, r=r)
    return pbkdf(password, ''.join(b), 1, buflen, digestmod=hashlib.sha256)

