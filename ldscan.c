// ldscan: read graph6 graphs (n <= 16) from stdin; for each twin-free graph without isolated
// vertices compute gamma_L (location-domination number) and alpha' (matching number).
// Reports counts and examples where gamma_L > alpha', split by C4-free / K23-free / other,
// and any violation of gamma_L <= n/2.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n;
static unsigned nb[16];

static int parse_g6(const char *s) {
    if (s[0] < 63) return -1;
    n = s[0] - 63;
    if (n > 16) return -1;
    memset(nb, 0, sizeof nb);
    int bit = 0; const char *p = s + 1;
    int val = 0, left = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (left == 0) { val = (*p++) - 63; left = 6; }
            left--;
            if ((val >> left) & 1) { nb[i] |= 1u << j; nb[j] |= 1u << i; }
            bit++;
        }
    return n;
}

static int twin_free(void) {
    for (int u = 0; u < n; u++) {
        if (nb[u] == 0) return 0;  // isolated
        for (int v = u + 1; v < n; v++) {
            if (nb[u] == nb[v]) return 0;
            if ((nb[u] | (1u << u)) == (nb[v] | (1u << v))) return 0;
        }
    }
    return 1;
}

static int max_common(void) {
    int best = 0;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) {
            int c = __builtin_popcount(nb[u] & nb[v]);
            if (c > best) best = c;
        }
    return best;
}

static signed char memo[1 << 16];
static int mm(unsigned S) {
    if (S == 0) return 0;
    if (memo[S] >= 0) return memo[S];
    int v = __builtin_ctz(S);
    unsigned R = S & ~(1u << v);
    int best = mm(R);
    unsigned c = nb[v] & R;
    while (c) {
        int u = __builtin_ctz(c); c &= c - 1;
        int t = 1 + mm(R & ~(1u << u));
        if (t > best) best = t;
    }
    memo[S] = best;
    return best;
}

static int is_ld(unsigned D) {
    unsigned tr[16]; int k = 0;
    for (int v = 0; v < n; v++) {
        if (D >> v & 1) continue;
        unsigned t = nb[v] & D;
        if (!t) return 0;
        for (int i = 0; i < k; i++) if (tr[i] == t) return 0;
        tr[k++] = t;
    }
    return 1;
}

// gamma_L by increasing size using Gosper's hack
static int gammaL(void) {
    unsigned full = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    for (int k = 1; k <= n; k++) {
        unsigned D = (1u << k) - 1;
        while (D <= full) {
            if (is_ld(D)) return k;
            unsigned c = D & -D, r = D + c;
            D = (((r ^ D) >> 2) / c) | r;
        }
    }
    return n;
}

int main(int argc, char **argv) {
    char line[256];
    long total = 0, tf = 0, cnt_gt[3] = {0, 0, 0}, viol_half = 0, deficient[3] = {0,0,0};
    int shown[3] = {0, 0, 0};
    const char *lab[3] = {"C4-free", "K23-free (has C4)", "has K23"};
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        if (parse_g6(line) < 0) continue;
        total++;
        if (!twin_free()) continue;
        tf++;
        memset(memo, -1, sizeof(signed char) * (1u << n));
        int a = mm((1u << n) - 1);
        int g = gammaL();
        int mc = max_common();
        int cls = (mc <= 1) ? 0 : (mc == 2 ? 1 : 2);
        if (2 * a < n - 1) deficient[cls]++;
        if (2 * g > n) { viol_half++; printf("VIOLATES n/2: %s g=%d\n", line, g); }
        if (g > a) {
            cnt_gt[cls]++;
            if (shown[cls] < 8) { shown[cls]++; printf("gL>a' [%s]: %s n=%d gL=%d a'=%d\n", lab[cls], line, n, g, a); }
        }
    }
    printf("graphs=%ld twinfree=%ld violations_n/2=%ld\n", total, tf, viol_half);
    for (int c = 0; c < 3; c++)
        printf("  %-20s deficient(a'<floor(n/2))=%ld  gL>a'=%ld\n", lab[c], deficient[c], cnt_gt[c]);
    return 0;
}
