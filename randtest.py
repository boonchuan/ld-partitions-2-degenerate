"""Random stress tests.
mode 'thm1': random outerplanar graphs (twins allowed) with a perfect matching, n up to 80:
             verify the parity transversal and its complement are LD (Theorem 1).
mode 'full': random twin-free outerplanar graphs WITHOUT a perfect matching, n 11..17:
             look for an LD-partition of the form (T u XA, T* u XB) using a maximum matching that
             maximises the total degree of unmatched vertices (searching a sample of max matchings).
"""
import sys
import random
from itertools import product
import networkx as nx
from thm1check import link_list, parity_solution
from extend import aligned_transversals


def is_ld_set(G, D):
    seen = set()
    for v in G.nodes():
        if v in D:
            continue
        t = frozenset(w for w in G[v] if w in D)
        if not t or t in seen:
            return False
        seen.add(t)
    return True


def random_outerplanar(n, keep):
    # random triangulation of polygon 0..n-1 via random ear-clipping, then random deletions
    poly = list(range(n))
    E = {(i, (i + 1) % n) for i in range(n)}
    while len(poly) > 3:
        i = random.randrange(len(poly))
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % len(poly)]
        E.add((a, c))
        poly.pop(i)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u, v in E:
        if random.random() < keep:
            G.add_edge(u, v)
    perm = list(range(n))
    random.shuffle(perm)
    return nx.relabel_nodes(G, dict(enumerate(perm)))


def nbmask(G):
    n = G.number_of_nodes()
    nb = [0] * n
    for u, v in G.edges():
        nb[u] |= 1 << v
        nb[v] |= 1 << u
    return n, nb


def random_perfect_matchings(G, k):
    """Sample up to k perfect matchings by randomised max matching with random weights."""
    out = set()
    for _ in range(k):
        for u, v in G.edges():
            G[u][v]["w"] = random.random()
        M = nx.max_weight_matching(G, maxcardinality=True, weight="w")
        out.add(tuple(sorted(tuple(sorted(e)) for e in M)))
    return [list(m) for m in out]


def twin_free(G):
    so, sc = set(), set()
    for v in G.nodes():
        o = frozenset(G[v])
        c = o | {v}
        if not o or o in so or c in sc:
            return False
        so.add(o)
        sc.add(c)
    return True


def thm1(trials):
    graphs = matchings = fails = 0
    for _ in range(trials):
        n = random.choice(range(10, 81, 2))
        G = random_outerplanar(n, random.uniform(0.55, 1.0))
        if any(d == 0 for _, d in G.degree()):
            continue
        M0 = nx.max_weight_matching(G, maxcardinality=True)
        if 2 * len(M0) != n:
            continue
        graphs += 1
        n_, nb = nbmask(G)
        for M in random_perfect_matchings(G, 4):
            matchings += 1
            L = link_list(nb, M)
            assert all(s is not None for _, _, s in L), "double link in outerplanar graph?!"
            x = parity_solution(len(M), L)
            assert x is not None, "link graph not a forest?!"
            T = {M[i][x[i]] for i in range(len(M))}
            Tc = set(G.nodes()) - T
            if not (is_ld_set(G, T) and is_ld_set(G, Tc)):
                fails += 1
                print("FAIL", nx.to_graph6_bytes(G, header=False).decode().strip(), M)
    print(f"thm1: graphs={graphs} matchings={matchings} failures={fails}")


def full(trials):
    graphs = ok = 0
    bad = []
    for _ in range(trials):
        n = random.choice(range(11, 18))
        G = random_outerplanar(n, random.uniform(0.5, 0.9))
        if not nx.is_connected(G) or not twin_free(G):
            continue
        M0 = nx.max_weight_matching(G, maxcardinality=True)
        if 2 * len(M0) >= n - 0:
            if 2 * len(M0) == n:
                continue
        n_, nb = nbmask(G)
        cands = []
        for _ in range(30):
            for u, v in G.edges():
                G[u][v]["w"] = random.random()
            M = nx.max_weight_matching(G, maxcardinality=True, weight="w")
            if len(M) != len(M0):
                continue
            M = sorted(tuple(sorted(e)) for e in M)
            X = sorted(set(G.nodes()) - {w for e in M for w in e})
            cands.append((sum(G.degree(x) for x in X), tuple(M), tuple(X)))
        cands = sorted(set(cands), reverse=True)
        if not cands:
            continue
        graphs += 1
        best = cands[0][0]
        found = False
        for sd, M, X in cands:
            if sd != best:
                break
            M = list(M)
            L = link_list(nb, M)
            for xs in aligned_transversals(M, L):
                T = {M[i][xs[i]] for i in range(len(M))}
                Ts = {M[i][1 - xs[i]] for i in range(len(M))}
                for split in product((0, 1), repeat=len(X)):
                    XA = {X[i] for i in range(len(X)) if split[i] == 0}
                    XB = set(X) - XA
                    if is_ld_set(G, T | XA) and is_ld_set(G, Ts | XB):
                        found = True
                        break
                if found:
                    break
            if found:
                break
        ok += found
        if not found:
            bad.append(nx.to_graph6_bytes(G, header=False).decode().strip())
    print(f"full: graphs={graphs} with LD-partition from a max-sumdeg matching={ok} failures={len(bad)}", bad[:5])


if __name__ == "__main__":
    random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    {"thm1": thm1, "full": full}[sys.argv[1]](int(sys.argv[2]))
