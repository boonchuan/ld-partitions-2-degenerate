"""Core routines for locating-dominating (LD) sets on small graphs.

Graphs are given as adjacency bitmasks: nb[v] is an int whose bit u is set iff uv is an edge.
"""
from itertools import combinations
import networkx as nx


def g6_to_nb(g6: str):
    G = nx.from_graph6_bytes(g6.strip().encode())
    n = G.number_of_nodes()
    nb = [0] * n
    for u, v in G.edges():
        nb[u] |= 1 << v
        nb[v] |= 1 << u
    return n, nb, G


def is_twin_free(n, nb):
    seen_open = set()
    seen_closed = set()
    for v in range(n):
        o = nb[v]
        c = nb[v] | (1 << v)
        if o in seen_open or c in seen_closed:
            return False
        seen_open.add(o)
        seen_closed.add(c)
    return True


def has_isolated(n, nb):
    return any(nb[v] == 0 for v in range(n))


def is_ld(n, nb, D):
    """D is a bitmask. Return True iff D is locating-dominating."""
    traces = set()
    for v in range(n):
        if D >> v & 1:
            continue
        t = nb[v] & D
        if t == 0 or t in traces:
            return False
        traces.add(t)
    return True


def ld_number(n, nb, cap=None):
    """Minimum size of an LD set (search sizes 1..cap; returns None if none found up to cap)."""
    top = n if cap is None else cap
    for k in range(1, top + 1):
        for S in combinations(range(n), k):
            D = 0
            for v in S:
                D |= 1 << v
            if is_ld(n, nb, D):
                return k
    return None


def k23_free(n, nb):
    """True iff no two vertices have >= 3 common neighbours (no K_{2,3} subgraph)."""
    for u in range(n):
        for v in range(u + 1, n):
            if bin(nb[u] & nb[v]).count("1") >= 3:
                return False
    return True


def is_outerplanar(G):
    H = G.copy()
    apex = max(H.nodes()) + 1 if H.number_of_nodes() else 0
    H.add_node(apex)
    for v in G.nodes():
        H.add_edge(apex, v)
    return nx.check_planarity(H)[0]


def is_cactus(G):
    for comp in nx.biconnected_components(G):
        sub = G.subgraph(comp)
        if sub.number_of_edges() > 1 and sub.number_of_edges() != sub.number_of_nodes():
            return False
    return True


def matching_number(G):
    return len(nx.max_weight_matching(G, maxcardinality=True))
