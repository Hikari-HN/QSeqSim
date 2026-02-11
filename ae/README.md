# QSeqSim Artifact (FM 2026 AE)

**Paper title:** *QSeqSim: A Symbolic Simulator for Qiskit While Loops using Sequential Quantum Circuits*

**Artifact type:** Tool + benchmarks + scripts to reproduce experimental tables

**Target badges:** **Available** and **Reusable** (per FM 2026 / EAPLS guidelines)

This README gives **step-by-step instructions** to (1) install/run the artifact, (2) perform a **smoke test** (“kick-the-tires”), and (3) reproduce the experimental results **up to Table 5** in the paper. It also explains how to **extend** the artifact with new benchmarks and how we ensure **reproducibility** for randomized experiments (Table 3). The focus is on being executable by reviewers with minimal assumptions.

---

## 1. What this artifact contains

### 1.1 Tool

QSeqSim is a symbolic simulator backend for Qiskit classical control (especially **while loops**) based on BDD encodings and sequential-circuit semantics.

Core capabilities exercised by this artifact:

* **While-loop semantics**: loops are executed with explicit loop conditions, state retention, and bounded iteration checks.
* **Symbolic BDD execution**: amplitudes and probabilities are computed using BDDs with exact-zero checks to avoid floating-point noise.
* **Mid vs final measurement semantics**: mid-circuit measurements collapse state and update path probability; final measurements are readout-only.
* **Sampling vs preset modes**: sampling draws from exact probabilities; preset mode enforces a specific measurement path (used in reachability queries).

### 1.2 Experiments reproduced by this artifact

This artifact provides scripts to reproduce the paper’s experimental tables:

* **Table 1** : Qiskit RUS while-loops (preset mode)
* **Table 2a** : QRW sequential circuits (BDDSeqSim)
* **Table 2b** : Grover sequential circuits (BDDSeqSim)
* **Table 3** : Random quantum while-loops (sample mode) with **frozen** circuit instances + SHA256 manifest
* **Table 4** : Quantum state reachability (QRW reachability probability over iterations)
* **Table 5** : Measurement-outcome reachability (RUS termination-pattern probabilities)

All experiment scripts write machine-readable `.csv` files under `ae/results/`. Each CSV is produced by a single tool runner and is safe to compare directly to the paper’s tables.

---

## 2. System requirements

### 2.1 Recommended execution environment

The artifact is intended to run inside the provided Docker image (recommended by FM 2026 AE).

If you run it natively, the required environment is:

* Python **3.12**
* macOS or Linux recommended (some drivers use `signal.alarm`)
* Sufficient RAM for large BDD workloads (Table 2 full runs can be heavy)

### 2.2 Expected runtime (very important for AE)

Expected running time (on a laptop-class machine, e.g., Apple M2 / 16GB RAM; times may vary across hardware and virtualization):

* (One-time) Load Docker image archive (`docker load`): ~1–3 minutes (disk-speed dependent).
* Smoke test (`./ae/scripts/run_smoke.sh`, runs small subsets for Tables 1–5): < 1 minute (measured ~23 s).
* Table 1 (full) (`./ae/scripts/run_table1.sh`): ~5 minutes (measured 4m48s; may take longer on slower CPUs).
* Table 2a (full) (`./ae/scripts/run_table2a.sh`): ~90 minutes (3 sub-experiments, each with a per-run timeout of 1800 s; actual time depends on whether runs hit the timeout).
* Table 2b (full) (`./ae/scripts/run_table2b.sh`): ~90 minutes (3 sub-experiments, each with a per-run timeout of 1800 s; actual time depends on whether runs hit the timeout).
* Table 3 (full) (`./ae/scripts/run_table3.sh`): ~40–60 minutes (measured 39m07s; runtime dominated by 9 benchmarks × 50 repeats).
* Table 4 (full) (`./ae/scripts/run_table4.sh`): ~2 minutes (measured 1m22s).
* Table 5 (full) (`./ae/scripts/run_table5.sh`): < 1 minute (measured ~7 s).
* Total (Tables 1–5, full): ~3.5–4 hours (dominated by Table 2a/2b timeouts; plus the one-time Docker image load).

This artifact includes `--smoke` modes for all heavy tables to provide a fast sanity check.

---

## 3. Directory structure (key files)

### 3.1 AE scripts (entry points)

* `ae/scripts/run_smoke.sh` — **smoke test** for Tables 1–5
* `ae/scripts/run_table1.sh` — Table 1 only
* `ae/scripts/run_table2a.sh` — Table 2a only
* `ae/scripts/run_table2b.sh` — Table 2b only
* `ae/scripts/run_table3.sh` — Table 3 full
* `ae/scripts/run_table4.sh` — Table 4 full
* `ae/scripts/run_table5.sh` — Table 5 full
* `ae/scripts/run_all_tables.sh` — Tables 1–5 full (long)

### 3.2 AE tools (Python runners)

* `ae/tools/table1.py` — generates `ae/results/table1.csv` (RUS)
* `ae/tools/table2a.py` — generates `ae/results/table2a.csv` (QRW)
* `ae/tools/table2b.py` — generates `ae/results/table2b.csv` (Grover)
* `ae/tools/table3.py` — generates `ae/results/table3_raw.csv` and `ae/results/table3.csv`
* `ae/tools/table3_generate_frozen.py` — regenerates frozen Table 3 circuits using fixed seeds (optional)
* `ae/tools/table3_gen_manifest.py` — writes `ae/benchmarks/table3/manifest.json` (SHA256)
* `ae/tools/table3_verify_manifest.py` — verifies frozen circuits against the manifest (SHA256)
* `ae/tools/table4.py` — generates `ae/results/table4.csv` (supports `--smoke`)
* `ae/tools/table5.py` — generates `ae/results/table5.csv` (supports `--smoke`)

### 3.3 AE tools usage (parameters)

All commands are run from the repository root. Each tool generates one CSV and prints a short status summary.

* Table 1 (RUS):
  * `python ae/tools/table1.py [--smoke]`
  * `--smoke`: run only RUS-1 with 10/100 iterations
  * Output: `ae/results/table1.csv`
* Table 2a (QRW):
  * `python ae/tools/table2a.py [--smoke] [--timeout SECONDS]`
  * `--smoke`: small subset (n=16, iters 3/10)
  * `--timeout`: per-run timeout seconds (overrides default 300/1800)
  * Output: `ae/results/table2a.csv` (and logs under `ae/results/logs/` on failure)
* Table 2b (Grover):
  * `python ae/tools/table2b.py [--smoke] [--timeout SECONDS]`
  * `--smoke`: small subset (n=16, iters 3/10)
  * `--timeout`: per-run timeout seconds (overrides default 300/1800)
  * Output: `ae/results/table2b.csv` (and logs under `ae/results/logs/` on failure)
* Table 3 runner (RQC):
  * `python ae/tools/table3.py [--smoke] [--repeats N] [--timeout SECONDS] [--base-seed SEED] [--no-seed] [--only g50m5,g200m20]`
  * `--smoke`: subset (g50m5,g50m10) and repeats capped at 5
  * `--repeats`: runs per configuration (default 50)
  * `--timeout`: per-run timeout seconds (default 600)
  * `--base-seed`: base seed for deterministic sampling
  * `--no-seed`: disable deterministic seeding
  * `--only`: restrict to specific g/m pairs (e.g., g50m5)
  * Output: `ae/results/table3_raw.csv` and `ae/results/table3.csv`
  * Logs: `ae/results/logs/table3/` for TIMEOUT/LOOPOUT/ERROR runs
* Table 3 manifest generator:
  * `python ae/tools/table3_gen_manifest.py [--circuits-dir PATH] [--out PATH] [--note TEXT]`
  * `--circuits-dir`: folder containing frozen circuits
  * `--out`: output manifest path
  * `--note`: free-form note stored in manifest
  * Output: JSON manifest with per-circuit SHA256
* Table 3 frozen circuit generator:
  * `python ae/tools/table3_generate_frozen.py [--q N] [--force] [--skip-verify]`
  * `--q`: number of qubits (default 100)
  * `--force`: overwrite existing frozen circuits
  * `--skip-verify`: skip manifest verification step
  * Output: frozen circuits under `ae/benchmarks/table3/circuits_py/`
* Table 3 manifest verifier:
  * `python ae/tools/table3_verify_manifest.py [--manifest PATH] [--circuits-dir PATH]`
  * `--manifest`: manifest path (default ae/benchmarks/table3/manifest.json)
  * `--circuits-dir`: circuits folder (default ae/benchmarks/table3/circuits_py)
  * Output: verification report (OK or mismatch)
* Table 4 (reachability):
  * `python ae/tools/table4.py [--smoke] [--n N] [--k 1,3,7]`
  * `--smoke`: use k=1,2 unless `--k` is provided
  * `--n`: qubit count (default 256)
  * `--k`: comma-separated k list (overrides default 1..10)
  * Output: `ae/results/table4.csv`
* Table 5 (termination patterns):
  * `python ae/tools/table5.py [--smoke] [--k-max N] [--repeat-runs N]`
  * `--smoke`: set k-max=2 and repeat-runs=3 unless overridden
  * `--k-max`: max k value (default 8, runs k=0..k-max)
  * `--repeat-runs`: repeats per k for averaging (default 5)
  * Output: `ae/results/table5.csv`

### 3.4 Frozen benchmarks for Table 3

* `ae/benchmarks/table3/circuits_py/` — frozen random circuits used for Table 3
* `ae/benchmarks/table3/manifest.json` — SHA256 checksums for frozen circuits

### 3.5 Project data layout (AE-relevant)

* `ae/benchmarks/` — benchmark inputs used by the AE tools (Table 3 circuits live here)
* `ae/expected/` — reference tables produced on a laptop-class Apple Silicon machine (e.g., Apple M2 / 16GB RAM)
* `ae/precomputed/` — raw data as reported in the paper (archived for comparison)

---

## 4. Installation

### 4.1 Using Docker (recommended for AE)

1. Install Docker.
2. Load the provided Docker image (from the artifact bundle), e.g.:
   * If you have a `.tar.gz` image:
     ```bash
     gunzip -c qseqsim-ae-image.tar.gz | docker load
     ```
   * If you have a `.tar.xz` image:
     ```bash
     xz -dc qseqsim-ae-image.tar.xz | docker load
     ```
3. Run a container:
   ```bash
   docker run --rm -it qseqsim-ae:latest bash
   ```
4. Inside the container, go to the repo root (if not already), and run the smoke test:
   ```bash
   ./ae/scripts/run_smoke.sh
   ```

> If your artifact distribution uses a different image tag/name, replace `qseqsim-ae:latest` accordingly.
>
> If you only have the source bundle and need to build the image:
>
> ```bash
> docker build -t qseqsim-ae .
> ```

### 4.2 Native run (not recommended, but possible)

Ensure Python 3.12 and all dependencies are installed, then run the scripts from the repository root.

Recommended native setup:

```bash
chmod +x ae/scripts/install_dd_cudd.sh
./ae/scripts/install_dd_cudd.sh
pip install -r requirements.txt
pip install dd
```

If `dd` was installed before CUDD, reinstall it:

```bash
pip uninstall -y dd
pip install dd
```

---

## 5. Smoke test (Kick-the-tires paragraph)

**Goal:** Within 1 minute, reviewers should verify the artifact:

- runs end-to-end,
- generates outputs in the expected formats,
- exercises core while-loop support and the AE runners.

**Command:**

```bash
chmod +x ae/scripts/run_smoke.sh
./ae/scripts/run_smoke.sh
```

**What it does:**

* Runs **Table 1** (RUS) in `--smoke` mode:
  * only `RUS-1` with 10 and 100 iterations
  * writes `ae/results/table1.csv`
* Runs **Table 2a** (QRW) in `--smoke` mode:
  * small subset (e.g., `n=16`, report iters `3,10`)
  * writes `ae/results/table2a.csv`
* Runs **Table 2b** (Grover) in `--smoke` mode:
  * small subset (e.g., `n=16`, report iters `3,10`)
  * writes `ae/results/table2b.csv`
* Runs **Table 3** in `--smoke` mode:
  * subset circuits and capped repeats
  * writes `ae/results/table3_raw.csv` and `ae/results/table3.csv`
* Runs **Table 4** in `--smoke` mode:
  * writes `ae/results/table4.csv`
* Runs **Table 5** in `--smoke` mode:
  * writes `ae/results/table5.csv`

**Expected outputs (created/updated):**

* `ae/results/table1.csv`
* `ae/results/table2a.csv`
* `ae/results/table2b.csv`
* `ae/results/table3_raw.csv`
* `ae/results/table3.csv`
* `ae/results/table4.csv`
* `ae/results/table5.csv`

**If something fails:**

Each invocation of the AE runner creates a  **timestamped log directory** :

* `ae/results/logs/<YYYYMMDD-HHMMSS>/`

Check the newest such directory for:

* `run_table*.log` (captured stdout/stderr for each table),
* Table 2 debug/per-iter logs (see §6.2–§6.3),
* Table 3 failure logs under `table3/`.

---

## 6. Reproducing paper results (Tables 1–5)

All runs below should be executed from the  **repository root** .

### 6.1 Table 1 — RUS while-loops

Table 1 is exercised by the smoke test. To rerun:

```bash
./ae/scripts/run_table1.sh
```

Or run the commands directly:

```bash
ITER_TIME=10  python exp/simulation/exp_engine.py rus/rus_1
ITER_TIME=100 python exp/simulation/exp_engine.py rus/rus_1
```

The runtime is printed by `exp_engine.py` as:

`Total Runtime : <number> s` (with an emoji in the line).

---

### 6.2 Table 2a — QRW benchmark

Generate the CSV for Table 2a:

```bash
./ae/scripts/run_table2a.sh
```

Output:

* `ae/results/table2a.csv`

Smoke subset only:

```bash
python ae/tools/table2a.py --smoke
```

#### 6.2.1 Notes on timeouts and “last reported iteration” (important for AE)

Table 2a runs each QRW configuration witha **per-run timeout** (default: **1800 seconds** in full mode).
The runner reports timings only ata small setof **report iterations** (the same asinthe paper).

The tools for AE sets `--max-iters` to the maximum value in `--report-iters`.

Because Docker / virtualization can be slower than a native run ontheauthors’ machine, itispossiblethat:

- an experiment that finished just under 1800s inthe paper
- may hit the 1800s timeout during AE reproduction

In such cases, the CSV will contain `status=timeout_missing_iter` forthe missing report iteration(s). This is expected behavior and does not necessarily indicate a functional issue.

**How to judge whether the reproduction is still reasonable:**

For each `n`, the underlying experiment script (`exp/simulation/qrw.py`) writes a per-iteration log under:

- `exp/simulation/data/qrw_<n>.log`

During AE runs, the Table 2a tool archives this per-iteration logintothe timestamped results directory:

- `ae/results/logs/<timestamp>/table2a_qrw_n<n>_per_iter.log`

This per-iteration logcontains **cumulative time** aftereach iteration, so you can compare:

- the largest iteration reached before timeout, and
- the growth trend of runtime vs iterations,

against the paper’s reported last report iteration.

If the AE run times out earlier, but reaches an iteration count that is **reasonably close** (same order of magnitude, and consistent slowdown factor), the reproduction should be considered consistent given hardware differences.

---

### 6.3 Table 2b — Grover benchmark

Generate the CSV for Table 2b:

```bash
./ae/scripts/run_table2b.sh
```

Output:

* `ae/results/table2b.csv`

Smoke subset only:

```bash
python ae/tools/table2b.py --smoke
```

#### 6.3.1 Notes on timeouts and “last reported iteration” (important for AE)

Table 2b uses the same reporting strategy as Table 2a: each run has a per-run timeout (default **1800s** in full mode) and prints machine-readable `[REPORT]` lines only for selected report iterations.

On slower environments (e.g., Docker on shared/virtualized hardware), runs may hit the timeout earlier than in the authors’ environment. In that case, the CSV may mark the final report iteration as missing with `timeout_missing_iter`.

**How to inspect progress and compare to the paper:**

The experiment script writes per-iteration cumulative times to:

- `exp/simulation/data/grover_<n>.log`

During AE runs, the Table 2b tool archives it to:

- `ae/results/logs/<timestamp>/table2b_grover_n<n>_per_iter.log`

Use this file to check:

- how many iterations completed before timeout,
- whether the runtime growth vs iterations matches the expected trend.

---

### 6.4 Table 3 — Random quantum while-loops (RQC)

#### 6.4.1 Reproducibility strategy for random experiments

Table 3 is based on random circuits, but  **AE requires reproducibility** . Therefore:

* We provide **frozen** random circuits under:
  * `ae/benchmarks/table3/circuits_py/`
* We provide a  **SHA256 manifest** :
  * `ae/benchmarks/table3/manifest.json`
* The Table 3 runner verifies the manifest before running (if enabled).
* (Optional) we support **deterministic sampling seeds** for the sample-mode branching via environment variable `QSEQSIM_RNG_SEED`.

#### 6.4.2 Verify frozen circuits (recommended)

```bash
python ae/tools/table3_verify_manifest.py
```

#### 6.4.3 Run Table 3 (smoke)

```bash
python ae/tools/table3.py --smoke
```

#### 6.4.4 Run Table 3 (full)

```bash
./ae/scripts/run_table3.sh
```

Outputs:

* `ae/results/table3_raw.csv` (one row per run)
* `ae/results/table3.csv` (median/Q1/Q3 summary)

#### 6.4.5 (Optional) Regenerate frozen circuits with fixed seeds

If you want to **rebuild** the 9 frozen circuits from the generator using a fixed seed formula

`seed = 100000 + g*100 + m`:

```bash
python ae/tools/table3_generate_frozen.py --force
python ae/tools/table3_verify_manifest.py
```

This regenerates the frozen circuits and updates the manifest.

---

### 6.5 Table 4 — Quantum state reachability

Run Table 4 full:

```bash
./ae/scripts/run_table4.sh
```

Output:

* `ae/results/table4.csv`

Smoke subset (faster):

```bash
python ae/tools/table4.py --smoke
```

---

### 6.6 Table 5 — Measurement-outcome reachability

Run Table 5 full:

```bash
./ae/scripts/run_table5.sh
```

Output:

* `ae/results/table5.csv`

Smoke subset (faster):

```bash
python ae/tools/table5.py --smoke
```

---

## 7. Output summary

All outputs are written under:

* `ae/results/`

Main result files:

* `table1.csv`
* `table2a.csv`
* `table2b.csv`
* `table3_raw.csv`
* `table3.csv`
* `table4.csv`
* `table5.csv`

Logs:

- Each invocation of `run_all_tables.sh` (and therefore `run_smoke.sh`) creates a **timestamped** directory:
  - `ae/results/logs/<YYYYMMDD-HHMMSS>/`

  Inside it you will typically find:

- Runner logs (captured via `tee`):
  - `run_table1.log`, `run_table2a.log`, ..., `run_table5.log`
- Table 2 debug logs (only on failure or missing report iterations):
  - `table2a_qrw_n*.txt`, `table2b_grover_n*.txt`
- Table 2 per-iteration logs (archived for inspection on timeout):
  - `table2a_qrw_n*_per_iter.log`
  - `table2b_grover_n*_per_iter.log`
- Table 3 per-run failure logs:
  - `table3/*.txt`

---

## 8. Troubleshooting

### 8.1 Table 3: manifest mismatch

If `table3.py` reports SHA256 mismatch, it means frozen circuits changed but the manifest was not updated.

Fix:

```bash
python ae/tools/table3_gen_manifest.py
python ae/tools/table3_verify_manifest.py
```

Or regenerate frozen circuits:

```bash
python ae/tools/table3_generate_frozen.py --force
```

### 8.2 Table 3: smoke too slow

Use smoke mode (already default in `run_smoke.sh`) or reduce repeats/timeouts in:

* `ae/tools/table3.py --smoke`
* or run a smaller subset via `--only g50m5`

Example:

```bash
python ae/tools/table3.py --only g50m5 --repeats 3 --timeout 120
```

### 8.3 Loopout (`Max iterations (=1000) reached in SQC.`)

Some random circuits can cause long-running loops. The runner records such runs as `LOOPOUT` in `table3_raw.csv`.

### 8.4 Module import errors (`No module named 'src'`)

Run scripts from the repo root, or ensure tools add the project root to `sys.path` (the provided AE tools already do).

---

## 9. Reuse / Extension guide (for the Reusable badge)

This artifact is designed so that users can **add new benchmarks** and **rerun** experiments with minimal effort.

Additional notes for reuse:

* [docs/REUSE.md](../docs/REUSE.md) — extension guide (add gates / add benchmarks / testing)
* [docs/USER_GUIDE.md](../docs/USER_GUIDE.md) — library usage and semantics
* [docs/ENVIRONMENT.md](../docs/ENVIRONMENT.md) — environment setup (native / Docker)
* [docs/RESULTS_FORMAT.md](../docs/RESULTS_FORMAT.md) — output CSV formats

### 9.1 Run the tool on a new Qiskit circuit

To add a new Qiskit circuit benchmark file:

1. Create a file under `exp/simulation/<group>/<name>.py` that defines:
   * `circ`: a `qiskit.QuantumCircuit`
   * `sim_mode`: `"sample"` or `"preset"`
   * if preset: `preset_values` dictionary
2. Run:
   ```bash
   python exp/simulation/exp_engine.py <group>/<name>
   ```

This will:

* parse the circuit using `src.parser.QiskitParser`,
* execute using `src.simulator.BDDSimulator`,
* print timing stats including total runtime.

### 9.2 Add new Table 3-style random circuits

You can generate new random circuits using:

```bash
python exp/simulation/gen_rqc.py 100 200 5 --seed 12345
```

Then:

* copy the generated file from `exp/simulation/rqc/` into a new frozen dataset directory, and
* run `ae/tools/table3_gen_manifest.py` to create a checksum manifest.

### 9.3 Re-run Table 3 on a subset

Use:

```bash
python ae/tools/table3.py --only g50m5,g100m10 --repeats 10
```

---

## 10. License

See [License.txt](../License.txt) included in the artifact bundle.

---

## 11. Artifact packaging (Available badge)

For the FM 2026 AE submission, this artifact is intended to be released as a permanent archive (e.g., Zenodo) with a DOI.

The final submission should also provide the **SHA256 checksum** of the artifact ZIP file, as required by the FM 2026 AE instructions.

---
