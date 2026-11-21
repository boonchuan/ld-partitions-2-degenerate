// cubicscan: graph6 graphs (n <= 24) on stdin. For twin-free graphs without a perfect matching
// (alpha' < n/2), test whether gamma_L <= alpha'. Max matching via bitmask DP with hash-free memo
// only for graphs that have a bridge (cubic graphs without bridges have perfect matchings).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n;
static unsigned nb[32];
static int parse_g6(const char *s) {
    n = s[0] - 63; if (n < 1 || n > 24) return -1;
    memset(nb, 0, sizeof nb);
    const char *p = s + 1; int val = 0, left = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
        if (!left) { val = (*p++) - 63; left = 6; }
        left--; if ((val >> left) & 1) { nb[i] |= 1u << j; nb[j] |= 1u << i; }
    }
    return n;
}
static int twin_free(void) {
    for (int u = 0; u < n; u++) { if (!nb[u]) return 0;
        for (int v = u + 1; v < n; v++) {
            if (nb[u] == nb[v]) return 0;
            if ((nb[u] | 1u << u) == (nb[v] | 1u << v)) return 0; } }
    return 1;
}
// connectivity of graph with one edge removed
static int connected_without(int a, int b) {
    unsigned seen = 1u, frontier = 1u, all = (n == 32) ? ~0u : ((1u << n) - 1);
    while (frontier) {
        int v = __builtin_ctz(frontier); frontier &= frontier - 1;
        unsigned nbv = nb[v];
        if (v == a) nbv &= ~(1u << b);
        if (v == b) nbv &= ~(1u << a);
        unsigned nw = nbv & ~seen; seen |= nw; frontier |= nw;
    }
    return seen == all;
}
static int has_bridge(void) {
    for (int u = 0; u < n; u++) { unsigned c = nb[u] & ~((1u << (u + 1)) - 1);
        while (c) { int v = __builtin_ctz(c); c &= c - 1; if (!connected_without(u, v)) return 1; } }
    return 0;
}
static signed char *memo;
static int mm(unsigned S) { if (!S) return 0; if (memo[S] >= 0) return memo[S];
    int v = __builtin_ctz(S); unsigned R = S & ~(1u << v); int b = mm(R); unsigned c = nb[v] & R;
    while (c) { int u = __builtin_ctz(c); c &= c - 1; int t = 1 + mm(R & ~(1u << u)); if (t > b) b = t; }
    return memo[S] = (signed char)b; }
static int is_ld(unsigned D) {
    unsigned tr[32]; int k = 0;
    for (int v = 0; v < n; v++) { if (D >> v & 1) continue; unsigned t = nb[v] & D; if (!t) return 0;
        for (int i = 0; i < k; i++) if (tr[i] == t) return 0; tr[k++] = t; }
    return 1;
}
static int exists_ld_of_size(int k) {
    unsigned full = (1u << n) - 1, D = (1u << k) - 1;
    while (D <= full) { if (is_ld(D)) return 1; unsigned c = D & -D, r = D + c; D = (((r ^ D) >> 2) / c) | r; }
    return 0;
}
int main(void) {
    char line[512]; long total = 0, tf = 0, bridged = 0, deficient = 0, viol = 0;
    memo = malloc(1u << 24);
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        if (parse_g6(line) < 0) continue; total++;
        if (!twin_free()) continue; tf++;
        if (!has_bridge()) continue; bridged++;
        memset(memo, -1, 1u << n);
        int a = mm((1u << n) - 1);
        if (2 * a == n) continue;
        deficient++;
        int ok = 0;
        for (int k = 1; k <= a && !ok; k++) ok = exists_ld_of_size(k);
        if (!ok) { viol++; printf("gamma_L > alpha' : %s (alpha'=%d)\n", line, a); }
    }
    printf("graphs=%ld twinfree=%ld with_bridge=%ld no_perfect_matching=%ld violations(gamma_L>alpha')=%ld\n",
           total, tf, bridged, deficient, viol);
    return 0;
}
