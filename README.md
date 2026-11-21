# Locating-dominating partitions of 2-degenerate graphs with a perfect matching

Verification code for the working paper

> Boon Chuan Lim, *Partitioning 2-degenerate graphs with a perfect matching into two locating-dominating sets*, working paper, 22 November 2026.

**Main result.** Every 2-degenerate graph with a perfect matching M (for example, every outerplanar or series–parallel graph with a perfect matching, twins allowed) has a partition of its vertex set into two locating-dominating sets, each containing exactly one end of every edge of M. So its location-domination number is at most half its order.

The theorem rests on the proofs in the paper. The programs here test those statements, and the author's implementation of them, on many graphs. They are evidence and a check, not part of the proof.

## Requirements

- [nauty](https://pallini.di.uniroma1.it/) for `geng` (on Debian/Ubuntu: `apt install nauty`, where the command is `nauty-geng`). Runs used nauty 2.8.8.
- Python 3 (runs used 3.13). `check_ld.py` needs nothing else; the other Python scripts need `networkx` (runs used 3.7).
- A C compiler for the `.c` programs: `gcc -O2 -o NAME NAME.c`.

Below, `geng` stands for `nauty-geng` where that is the name on your system.

## Reproducing the results in the paper

| What | Command | Expected output |
|---|---|---|
| Lemma 4 and Theorem 2, exhaustive, order 10 (Appendix A) | `geng -c 10 9:17 \| python3 check_ld.py` | `298902 graphs and 1267669 perfect matchings checked; no failure` (about 30 s) |
| Same, order 8 | `geng -c 8 7:13 \| python3 check_ld.py` | `2276 graphs and 6509 perfect matchings checked; no failure` |
| Same, order 6 | `geng -c 6 5:9 \| python3 check_ld.py` | `52 graphs and 102 perfect matchings checked; no failure` |
| Theorem 2 via the C filter (second route) | `geng -cq 10 \| ./filter \| python3 thm1check.py` | `{'graphs': 298902, 'perfect matchings': 1267669, 'LD-partition found': 1267669}` |
| Random outerplanar graphs, orders 10–80 | `python3 randtest.py thm1 3000 7` and `python3 randtest.py thm1 4000 99` | 833 + 1,263 graphs, 2,607 + 4,098 perfect matchings, 0 failures |
| γ_L ≤ α′ for all twin-free connected graphs of order 10 | `geng -cq 10 \| ./ldscan` | `twinfree=8264613`, no violations; deficient (α′ ≤ 4) graphs 228 + 3305 + 14409 = 17,942 |
| Twin-free cubic graphs of order ≤ 20 have a perfect matching | `geng -cq -d3 -D3 20 \| ./cubicscan` (and orders 4–18) | `no_perfect_matching=0` at every order |
| Question 6 (no perfect matching), exhaustive, orders 5–9 | `geng -cq 9 \| python3 extend.py` (and orders 5–8) | every graph has an LD-partition of the stated form: 5, 0, 158, 39, 15,861 graphs at orders 5–9 (16,063 in all) |
| Question 6, matching rule | `geng -cq 9 \| python3 choose.py` | no `sumdeg FAILS` entry at any order 5–9 |
| Question 6, random outerplanar graphs, orders 11–17 | `python3 randtest.py full 1500 11` and `python3 randtest.py full 6000 23` | 268 + 1,062 graphs, 0 failures |

Edge ranges such as `9:17` are safe: a 2-degenerate graph of order n has at most 2n − 3 edges. The random tests depend on Python's `random` module and on `networkx`; other versions may draw different graphs.

## Files

| File | Purpose |
|---|---|
| `check_ld.py` | Self-contained exhaustive check of Lemma 4 and Theorem 2 (printed in Appendix A of the paper) |
| `filter.c`, `thm1check.py` | Second route to the same check: C filter for 2-degenerate graphs with a perfect matching, then a Python checker |
| `randtest.py` | Random stress tests (`thm1`: Theorem 2; `full`: Question 6) |
| `ldscan.c` | γ_L ≤ α′ and the n/2 bound for all twin-free connected graphs of a given order |
| `cubicscan.c` | Twin-free cubic graphs without a perfect matching (question of Foucaud and Henning) |
| `extend.py`, `choose.py` | Question 6: LD-partitions extending a matching transversal, and the rule for choosing the matching |
| `ldlib.py`, `transversal.py` | Shared helpers |

## AI use

The author used Anthropic's Claude to search the literature, to develop the proofs, to write and run these programs and to draft the paper. The author directed the work and takes full responsibility for it.

## Licence

MIT (see `LICENSE`).
