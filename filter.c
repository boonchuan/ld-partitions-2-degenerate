// filter: pass through graph6 lines (stdin->stdout) that are 2-degenerate and have a
// perfect matching. Flags: argv[1] = "tf" additionally requires twin-free & isolate-free.
#include <stdio.h>
#include <string.h>
static int n; static unsigned nb[32];
static int parse_g6(const char *s) { n = s[0] - 63; if (n < 1 || n > 20) return -1; memset(nb, 0, sizeof nb);
    const char *p = s + 1; int val = 0, left = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) { if (!left) { val = (*p++) - 63; left = 6; }
        left--; if ((val >> left) & 1) { nb[i] |= 1u << j; nb[j] |= 1u << i; } }
    return n; }
static int k23free(void) { for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if (__builtin_popcount(nb[u] & nb[v]) >= 3) return 0; return 1; }
static int degen2(void) { unsigned alive = (1u << n) - 1; int changed = 1;
    while (alive && changed) { changed = 0;
        for (int v = 0; v < n; v++) if ((alive >> v & 1) && __builtin_popcount(nb[v] & alive) <= 2) { alive &= ~(1u << v); changed = 1; } }
    return alive == 0; }
static int twin_free(void) { for (int u = 0; u < n; u++) { if (!nb[u]) return 0; for (int v = u + 1; v < n; v++) {
        if (nb[u] == nb[v]) return 0; if ((nb[u] | 1u << u) == (nb[v] | 1u << v)) return 0; } } return 1; }
static signed char memo[1 << 20];
static int pm(unsigned S) { // has perfect matching on S?
    if (!S) return 1; if (memo[S] >= 0) return memo[S];
    int v = __builtin_ctz(S); unsigned R = S & ~(1u << v), c = nb[v] & R; int r = 0;
    while (c && !r) { int u = __builtin_ctz(c); c &= c - 1; r = pm(R & ~(1u << u)); }
    return memo[S] = r; }
int main(int argc, char **argv) { char line[256]; int tf = argc > 1 && !strcmp(argv[1], "tf");
    while (fgets(line, sizeof line, stdin)) { char g[256]; strcpy(g, line); g[strcspn(g, "\r\n")] = 0;
        if (parse_g6(g) < 0 || (n & 1)) continue;
        if (tf && !twin_free()) continue;
        if (!degen2()) continue;
        memset(memo, -1, 1u << n); if (!pm((1u << n) - 1)) continue;
        puts(g); }
    return 0; }
