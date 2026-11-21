"""Which maximum matching should the proof pick?  For twin-free connected 2-degenerate graphs without a
perfect matching, evaluate criteria for choosing M (among maximum matchings with U_M empty):
  sumdeg  : maximise sum of degrees of unmatched vertices
  spread  : maximise sum over unmatched x of #M-edges meeting N(x)
  minspread: maximise the minimum spread
For each criterion: does EVERY optimal matching admit an LD-partition extension (some aligned T and
split of X)?  Count graphs where the criterion fails."""
import sys
from itertools import product
from collections import Counter
from ldlib import g6_to_nb, is_twin_free, is_ld
from transversal import max_matchings
from thm1check import link_list
from extend import aligned_transversals, degen2


def extends(n, nb, M, X):
    L = link_list(nb, M)
    for xs in aligned_transversals(M, L):
        Tm = sum(1 << M[i][xs[i]] for i in range(len(M)))
        Ts = sum(1 << M[i][1 - xs[i]] for i in range(len(M)))
        for split in product((0, 1), repeat=len(X)):
            XA = sum(1 << X[i] for i in range(len(X)) if split[i] == 0)
            XB = sum(1 << X[i] for i in range(len(X)) if split[i] == 1)
            if is_ld(n, nb, Tm | XA) and is_ld(n, nb, Ts | XB):
                return True
    return False


if __name__ == "__main__":
    R = Counter()
    ex = {}
    for line in sys.stdin:
        n, nb, G = g6_to_nb(line)
        if not is_twin_free(n, nb) or any(v == 0 for v in nb):
            continue
        if not degen2(n, nb):
            continue
        a, Ms = max_matchings(n, nb)
        if 2 * a == n:
            continue
        R["graphs"] += 1
        rows = []
        for M in Ms:
            matched = 0
            for u, v in M:
                matched |= (1 << u) | (1 << v)
            X = [x for x in range(n) if not matched >> x & 1]
            if any(nb[x] & ~((1 << u) | (1 << v)) == 0 for x in X for u, v in M):
                continue
            spreads = [sum(1 for u, v in M if nb[x] & ((1 << u) | (1 << v))) for x in X]
            rows.append((M, X, sum(bin(nb[x]).count("1") for x in X), sum(spreads), min(spreads), extends(n, nb, M, X)))
        crit = {"sumdeg": lambda r: r[2], "spread": lambda r: r[3], "minspread": lambda r: (r[4], r[3])}
        for name, f in crit.items():
            best = max(f(r) for r in rows)
            if not all(r[5] for r in rows if f(r) == best):
                R[name + " FAILS"] += 1
                ex.setdefault(name, line.strip())
    print(dict(R))
    print(ex)
