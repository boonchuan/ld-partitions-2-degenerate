"""Check Theorem 1 on every graph supplied (graph6, already filtered: K23-free, 2-degenerate, has a
perfect matching; twins allowed).  For EVERY perfect matching M:
  1. build the link graph H(G,M); check it is a forest with no double links (Lemma 2);
  2. solve the parity system 'adjacent corners on every link' by BFS over H;
  3. check that the solution T and its complement are both locating-dominating (Theorem 1).
Any failure is printed."""
import sys
from collections import Counter, deque
from ldlib import g6_to_nb, is_ld
from transversal import max_matchings


def link_list(nb, M):
    L = []
    for i in range(len(M)):
        a, p = M[i]
        for j in range(i + 1, len(M)):
            b, q = M[j]
            c1 = (nb[a] >> q & 1) and (nb[p] >> b & 1)  # cross edges a-q, p-b
            c2 = (nb[a] >> b & 1) and (nb[p] >> q & 1)  # cross edges a-b, p-q
            if c1 and c2:
                L.append((i, j, None))  # double link (K4)
            elif c1:
                # choose a (index 0) & q (index 1) or p (1) & b (0): x_i xor x_j == 1
                L.append((i, j, 1))
            elif c2:
                # choose a(0)&b(0) or p(1)&q(1): x_i xor x_j == 0
                L.append((i, j, 0))
    return L


def parity_solution(k, L):
    adj = [[] for _ in range(k)]
    for i, j, s in L:
        adj[i].append((j, s))
        adj[j].append((i, s))
    x = [None] * k
    for r in range(k):
        if x[r] is not None:
            continue
        x[r] = 0
        dq = deque([r])
        while dq:
            u = dq.popleft()
            for w, s in adj[u]:
                want = x[u] ^ s
                if x[w] is None:
                    x[w] = want
                    dq.append(w)
                elif x[w] != want:
                    return None
    return x


if __name__ == "__main__":
    T = Counter()
    for line in sys.stdin:
        n, nb, G = g6_to_nb(line)
        a, Ms = max_matchings(n, nb)
        assert 2 * a == n
        T["graphs"] += 1
        for M in Ms:
            T["perfect matchings"] += 1
            L = link_list(nb, M)
            if any(s is None for _, _, s in L):
                T["DOUBLE LINK (Lemma 2 fails)"] += 1
                print("double link", line.strip(), M)
                continue
            x = parity_solution(len(M), L)
            if x is None:
                T["PARITY UNSAT / H has bad cycle (Lemma 2 fails)"] += 1
                print("unsat", line.strip(), M)
                continue
            D1 = sum(1 << M[i][x[i]] for i in range(len(M)))
            D2 = sum(1 << M[i][1 - x[i]] for i in range(len(M)))
            ok1, ok2 = is_ld(n, nb, D1), is_ld(n, nb, D2)
            if not (ok1 and ok2):
                T["THEOREM 1 FAILS"] += 1
                print("FAIL", line.strip(), M, x, ok1, ok2)
            else:
                T["LD-partition found"] += 1
    print(dict(T))
