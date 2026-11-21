"""For twin-free connected graphs (graph6 on stdin), test the matching-transversal property:

  (T) there is a maximum matching M and a set D containing exactly one endpoint of every
      edge of M such that D is locating-dominating.

(T) implies gamma_L <= alpha' <= n/2.  Garijo-Gonzalez-Marquez proved (T) for C4-free graphs.
We record, per class (C4-free / K23-free with C4 / has K23), how many graphs fail (T).
"""
import sys
from itertools import product
from collections import Counter
from ldlib import g6_to_nb, is_twin_free, is_ld


def max_matchings(n, nb):
    """Yield all maximum matchings as lists of (u, v) edges."""
    best = [0]
    res = []

    def rec(S, cur):
        if S == 0:
            if len(cur) > best[0]:
                best[0] = len(cur)
                res.clear()
            if len(cur) == best[0]:
                res.append(list(cur))
            return
        # bound: remaining vertices can add at most popcount(S)//2 edges
        if len(cur) + bin(S).count("1") // 2 < best[0]:
            return
        v = (S & -S).bit_length() - 1
        R = S & ~(1 << v)
        c = nb[v] & R
        while c:
            u = (c & -c).bit_length() - 1
            c &= c - 1
            cur.append((v, u))
            rec(R & ~(1 << u), cur)
            cur.pop()
        rec(R, cur)  # leave v unmatched

    rec((1 << n) - 1, [])
    return best[0], res


def has_ld_transversal(n, nb):
    a, Ms = max_matchings(n, nb)
    for M in Ms:
        for choice in product((0, 1), repeat=len(M)):
            D = 0
            for (u, v), c in zip(M, choice):
                D |= 1 << (u if c == 0 else v)
            if is_ld(n, nb, D):
                return a, True, D
    return a, False, None


def cls(n, nb):
    mc = 0
    for u in range(n):
        for v in range(u + 1, n):
            mc = max(mc, bin(nb[u] & nb[v]).count("1"))
    return "C4-free" if mc <= 1 else ("K23-free+C4" if mc == 2 else "hasK23")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    tally = Counter()
    fails = {}
    for line in sys.stdin:
        n, nb, G = g6_to_nb(line)
        if not is_twin_free(n, nb) or any(x == 0 for x in nb):
            continue
        c = cls(n, nb)
        if only and c != only:
            continue
        tally[c] += 1
        a, ok, D = has_ld_transversal(n, nb)
        if not ok:
            tally[c + " FAIL"] += 1
            fails.setdefault(c, []).append(line.strip())
    print(dict(tally))
    for c, L in fails.items():
        print(c, "fail examples:", L[:10])
