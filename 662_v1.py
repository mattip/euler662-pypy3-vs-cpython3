# The Expat License
#
# Copyright 2019, Shlomi Fish
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import sys
from collections import defaultdict

# from modsum import np_modsum as mods
from cffi import FFI

# import numpy as np
import _numpypy.multiarray as np
# import sys

from six import print_
from six.moves import range

MOD = 10 ** 9 + 7

ffi = FFI()
ffi.cdef("int my_modsum(uint64_t*cin, size_t len);")
C = ffi.dlopen("./modsum.so")


def mods(a):
    return C.my_modsum(ffi.from_buffer(a), len(a))


fibs = [1, 1]
while fibs[-1] < 20000:
    fibs.append(fibs[-1]+fibs[-2])

fibs.pop(0)
fibs_set = frozenset(fibs)

steps = []
for x in range(10000+1):
    print_('steps', x)
    for z in fibs:
        if z < x:
            continue
        z2 = z*z
        y2 = z2-x*x
        y = int(math.sqrt(y2))
        if y >= x:
            break
        if y*y == y2:
            steps.append((x, y))
            steps.append((y, x))


class BatchStep(object):
    """docstring for BatchStep"""
    def __init__(self, W, H, ww, hh):
        self.W, self.H, self.ww, self.hh = W, H, ww, hh
        vec = [[defaultdict(int, {(x, y): 1}) for y in range(hh)]
               for x in range(ww)]
        out = {}
        for x in range(ww):
            print_('x =', x)
            for y in range(hh):
                v = vec[x][y]
                for dx, dy in steps:
                    tx = x+dx
                    ty = y+dy
                    if tx > W or ty > H:
                        continue
                    if tx < ww and ty < hh:
                        tarvec = vec[tx][ty]
                    else:
                        if tx not in out:
                            out[tx] = {}
                        if ty not in out[tx]:
                            out[tx][ty] = defaultdict(int)
                        tarvec = out[tx][ty]
                    for vv, val in v.items():
                        tarvec[vv] = (tarvec[vv]+val) % MOD
                        if not tarvec[vv]:
                            del tarvec[vv]

        def dict2vec(x):
            ret = np.zeros((ww*hh), dtype='uint64')
            for vv, val in x.items():
                ret[vv[0]*ww+vv[1]] = val
            return ret

        out_l = []
        for x in sorted(out.keys()):
            xval = out[x]
            out_l.append((x, [(y, dict2vec(xval[y]))
                              for y in sorted(xval.keys())]))
        self.op = out_l

    def apply_(self, m, x, y):
        """docstring for apply_"""
        msrc = m[x:(x+self.ww), y:(y+self.hh)].flatten().astype('uint64')
        W = self.W
        H = self.H
        for dx, ys in self.op:
            tx = x + dx
            if tx > W:
                break
            for dy, v in ys:
                ty = y + dy
                if ty > H:
                    break
                res = m[tx, ty] + mods(msrc * v)
                m[tx, ty] = (res - MOD if res >= MOD else res)


'''
                if tx == ty:
                    m[tx, ty] = (m[tx, ty] + delta*2) % MOD
                else:
                    m[ty, tx] = m[tx, ty] = (m[tx, ty] + delta) % MOD
'''


def solve(W, H):
    m = np.zeros((W+1, H+1), dtype='uint32')
    m[0, 0] = 1
    for x in range(W+1):
        print_('x =', x)
        for y in range(H+1):
            v = m[x, y]
            for dx, dy in steps:
                tx = x+dx
                ty = y+dy
                if tx > W or ty > H:
                    continue
                m[tx, ty] = (m[tx, ty]+v) % MOD
    return m[-1, -1]


def solve_using_batch(W, H, ww, hh):
    m = np.zeros((W+1, H+1), dtype='uint32')
    op = BatchStep(W, H, ww, hh)
    m[0, 0] = 1
    x = 0
    while x <= W:
        print_('x =', x)
        y = 0
        deltax = 1
        if x + ww < W:
            deltax = ww
        while y <= H:
            print_('x =', x, 'y =', y)
            deltay = 1
            if deltax > 1 and y + hh < H:
                deltay = hh
                op.apply_(m, x, y)
            else:
                for xx in range(x, x+deltax):
                    v = m[xx, y]
                    for dx, dy in steps:
                        tx = xx+dx
                        ty = y+dy
                        if tx > W or ty > H:
                            continue
                        m[tx, ty] = (m[tx, ty]+v) % MOD
            y += deltay
        x += deltax
    ret = m[-1, -1]
    print_(ret)
    return ret


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        assert solve(3, 4) == 278
        assert solve(10, 10) == 215846462
        assert solve_using_batch(10, 10, 2, 2) == 215846462
        assert solve_using_batch(10, 10, 5, 5) == 215846462
        assert solve_using_batch(10, 10, 4, 4) == 215846462
        assert solve_using_batch(100, 100, 20, 20) == solve(100, 100)
    print_('foo')
    v = solve_using_batch(10000, 10000, 20, 20)
    print_('sol =', v)


if __name__ == "__main__":
    main()
