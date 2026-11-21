"""Unmatched-vertex extension test: twin-free connected 2-degenerate graphs without a perfect matching.

For a maximum matching M (U_M empty), an aligned transversal T (adjacent corners on every link)
and its complement T*, we look for a split X = XA u XB of the unmatched vertices with
   DA = T u XA   and   DB = T* u XB   both locating-dominating      (an LD-partition), and,
more weakly, for XA with |XA| <= |X|/2 such that T u XA is LD (gives gamma_L <= n/2).
Reports, per graph, whether some (M, T) admits an LD-partition / the weak extension."""
import sys
from itertools import product
from collections import Counter
from ldlib import g6_to_nb, is_twin_free, is_ld
from transversal import max_matchings
from thm1check import link_list
import networkx as nx


def aligned_transversals(M, L):
    k = len(M)
    Hg = nx.Graph()
    Hg.add_nodes_from(range(k))
    for i, j, s in L:
        Hg.add_edge(i, j, s=s)
    comps = list(nx.connected_components(Hg))
    base = [None] * k
    for comp in comps:
        r = min(comp)
        base[r] = 0
        for u, w in nx.bfs_edges(Hg, r):
            base[w] = base[u] ^ Hg[u][w]["s"]
    for flips in product((0, 1), repeat=len(comps)):
        x = list(base)
        for f, comp in zip(flips, comps):
            if f:
                for i in comp:
                    x[i] ^= 1
        yield x


def degen2(n, nb):
    alive = (1 << n) - 1
    changed = True
    while alive and changed:
        changed = False
        for v in range(n):
            if alive >> v & 1 and bin(nb[v] & alive).count("1") <= 2:
                alive &= ~(1 << v)
                changed = True
    return alive == 0


if __name__ == "__main__":
    use_UM = len(sys.argv) < 2 or sys.argv[1] != "anyM"
    T = Counter()
    ex = []
    for line in sys.stdin:
        n, nb, G = g6_to_nb(line)
        if not is_twin_free(n, nb) or any(v == 0 for v in nb):
            continue
        if not degen2(n, nb):
            continue
        a, Ms = max_matchings(n, nb)
        if 2 * a == n:
            continue
        T["graphs (no perfect matching)"] += 1
        part_ok = weak_ok = False
        part_allM = True
        for M in Ms:
            matched = 0
            for u, v in M:
                matched |= (1 << u) | (1 << v)
            X = [x for x in range(n) if not matched >> x & 1]
            if use_UM and any(nb[x] & ~((1 << u) | (1 << v)) == 0 for x in X for u, v in M):
                continue
            L = link_list(nb, M)
            M_part = False
            for xs in aligned_transversals(M, L):
                Tm = sum(1 << M[i][xs[i]] for i in range(len(M)))
                Ts = sum(1 << M[i][1 - xs[i]] for i in range(len(M)))
                for split in product((0, 1), repeat=len(X)):
                    XA = sum(1 << X[i] for i in range(len(X)) if split[i] == 0)
                    XB = sum(1 << X[i] for i in range(len(X)) if split[i] == 1)
                    a_ok = is_ld(n, nb, Tm | XA)
                    if a_ok and 2 * bin(XA).count("1") <= len(X):
                        weak_ok = True
                    if a_ok and is_ld(n, nb, Ts | XB):
                        M_part = True
                        break
                if M_part:
                    break
            part_ok |= M_part
            part_allM &= M_part
        T["LD-partition via some (M,T,split)"] += part_ok
        T["LD-partition for EVERY matching"] += part_allM
        T["weak n/2 extension exists"] += weak_ok
        if not part_ok and len(ex) < 8:
            ex.append(line.strip())
    print(dict(T))
    print("graphs with no LD-partition of this form:", ex)
