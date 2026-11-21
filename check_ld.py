#!/usr/bin/env python3
"""Check Lemma 4 and Theorem 2 on the graph6 graphs read from stdin.

Usage (a 2-degenerate graph of order n has at most 2n - 3 edges):
    geng -c 10 9:17 | python3 check_ld.py

For each 2-degenerate graph with a perfect matching, and for every perfect
matching M of it, the program checks that
  1. no two edges of M are doubly linked and the link graph H(G, M) is a
     forest (Lemma 4), and
  2. the transversal T given by the parity system and its complement are
     both locating-dominating sets (Theorem 2).
Any failure stops the program with an AssertionError.
"""
import sys


def parse(s):
    """graph6 string -> (n, adjacency bitmasks)."""
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    nb, k = [0] * n, 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                nb[i] |= 1 << j
                nb[j] |= 1 << i
            k += 1
    return n, nb


def two_degenerate(n, nb):
    """True if repeatedly deleting a vertex of degree <= 2 empties G."""
    alive = (1 << n) - 1
    while alive:
        low = [v for v in range(n)
               if alive >> v & 1 and bin(nb[v] & alive).count("1") <= 2]
        if not low:
            return False
        alive &= ~(1 << low[0])
    return True


def perfect_matchings(nb, S):
    """Yield the perfect matchings of the vertex set S (a bitmask)."""
    if S == 0:
        yield []
        return
    v = (S & -S).bit_length() - 1
    R = S & ~(1 << v)
    c = nb[v] & R
    while c:
        u = (c & -c).bit_length() - 1
        c &= c - 1
        for rest in perfect_matchings(nb, R & ~(1 << u)):
            yield [(v, u)] + rest


def is_ld(n, nb, D):
    """True if the vertex set D (a bitmask) is locating-dominating."""
    seen = set()
    for v in range(n):
        if D >> v & 1:
            continue
        trace = nb[v] & D
        if trace == 0 or trace in seen:
            return False
        seen.add(trace)
    return True


graphs = matchings = 0
for line in sys.stdin:
    n, nb = parse(line.strip())
    if not two_degenerate(n, nb):
        continue
    Ms = list(perfect_matchings(nb, (1 << n) - 1))
    if not Ms:
        continue
    graphs += 1
    for M in Ms:
        matchings += 1
        k = len(M)
        links = [[] for _ in range(k)]
        edges = 0
        for i in range(k):
            a, a2 = M[i]                          # e(0) = a, e(1) = a'
            for j in range(i + 1, k):
                b, b2 = M[j]                      # f(0) = b, f(1) = b'
                p1 = nb[a] >> b & 1 and nb[a2] >> b2 & 1   # {ab, a'b'}
                p2 = nb[a] >> b2 & 1 and nb[a2] >> b & 1   # {ab', a'b}
                assert not (p1 and p2), "doubly linked pair"
                if p1 or p2:
                    sigma = 0 if p1 else 1
                    links[i].append((j, sigma))
                    links[j].append((i, sigma))
                    edges += 1
        x, trees = [None] * k, 0
        for r in range(k):        # solve x(e) + x(f) = sigma(e, f) mod 2
            if x[r] is not None:
                continue
            trees += 1
            x[r], stack = 0, [r]
            while stack:
                e = stack.pop()
                for f, sigma in links[e]:
                    if x[f] is None:
                        x[f] = x[e] ^ sigma
                        stack.append(f)
                    assert x[f] == x[e] ^ sigma, "no parity solution"
        assert edges == k - trees, "link graph is not a forest"
        T = sum(1 << M[i][x[i]] for i in range(k))
        rest = ((1 << n) - 1) & ~T
        assert is_ld(n, nb, T) and is_ld(n, nb, rest), "Theorem 2 fails"

msg = f"{graphs} graphs and {matchings} perfect matchings checked"
print(msg + "; no failure")
