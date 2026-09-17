# Supplementary Methods — Entropy analysis

## Trajectory sampling

From each GPUMD trajectory (2500 frames, 2 ps spacing, 2–5000 ps), **400 frames** were selected by uniform indexing. Neighbour searches used periodic boundary conditions. Oxygen first-shell neighbours were counted within **2.5 Å**; metal–metal neighbours (Fe, Co, Ni) within **3.0 Å**.

---

## Atomic entropy \(S_\mathrm{atom}\)

**Definition.** Each atom is assigned a discrete local-environment state

\[
\mathbf{s} = (\mathrm{species},\ \mathrm{CN_O},\ \mathrm{CN_M}),
\]

where \(\mathrm{CN_O}\) is the number of O neighbours with \(r < 2.5\) Å and \(\mathrm{CN_M}\) is the number of Fe/Co/Ni neighbours with \(r < 3.0\) Å. All atom types (Fe, Co, Ni, O) are included.

**Statistics.** Let \(N_k\) be the number of atoms in state \(k\) and \(N = \sum_k N_k\). The atomic entropy is the Shannon entropy of this motif distribution:

\[
S_\mathrm{atom} = -\sum_k p_k \ln p_k, \qquad p_k = \frac{N_k}{N},
\]

with the sum over states having \(N_k > 0\). Units: **nats** (natural logarithm). Larger \(S_\mathrm{atom}\) means a broader distribution of local coordination environments.

---

## Cluster configurational entropy \(S_\mathrm{config}\)

**Definition.** Only **Fe, Co, and Ni** atoms are considered. They are grouped into connected clusters: two metal atoms belong to the same cluster if their distance is \(< 3.0\) Å (PBC-aware connectivity). Oxygen is excluded so that evaporated O does not enter the cluster count.

**Statistics.** If cluster \(c\) contains \(n_c\) metal atoms and \(N_\mathrm{metal} = \sum_c n_c\), the configurational entropy is the Shannon entropy of the cluster size distribution:

\[
S_\mathrm{config} = -\sum_c p_c \ln p_c, \qquad p_c = \frac{n_c}{N_\mathrm{metal}}.
\]

Units: **nats**. This measures how metal atoms are partitioned among spatially distinct domains: a single dominant cluster gives low \(S_\mathrm{config}\); many clusters of comparable size give high \(S_\mathrm{config}\).

---

## Relation between the two entropies

- **\(S_\mathrm{atom}\)** — atomistic: diversity of **local chemical/coordination environments** (first-shell motifs).
- **\(S_\mathrm{config}\)** — mesoscopic: diversity of **metal phase/domain sizes** (connected cluster partition).

Both quantities were evaluated independently at each sampled frame and plotted versus time (log-scaled time axis) for temperatures 1500–3000 K.
