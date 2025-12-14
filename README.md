# QSeqSim: A Symbolic Simulator for Qiskit While Loops using Sequential Quantum Circuits

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**QSeqSim** is a Qiskit-integrated symbolic backend that fills the current gap of having no Qiskit-native support for simulating `while`-loop quantum programs and their induced sequential quantum circuits (SQCs).

QSeqSim takes Qiskit `QuantumCircuit` objects, translates them into OpenQASM 3 code, and organises the resulting program into a combination of combinational, dynamic, and sequential circuits. It assigns `while`-loops a precise sequential circuit semantics with explicit internal and external qubits.

Building on this semantics, QSeqSim adopts a BDD-based symbolic representation and systematically integrates model counting techniques to optimise probability computation over structured and sparse BDDs. It enables efficient symbolic execution of sequential quantum circuits, scaling to substantial while-induced circuits (e.g., simulating Quantum Random Walks with over 1000 qubits for more than 10 loop iterations).

## Key Features

- **Direct While-Loop Support**: Executes Qiskit programs containing `while`-loops by giving them an executable small-step semantics, unlike standard simulators that often fail or unroll loops.
- **Symbolic Simulation**: Uses Binary Decision Diagrams (BDDs) (based on `dd` package) for efficient state representation.
- **Sequential Circuit Semantics**: Models loops as Sequential Quantum Circuits (SQCs) with state retention and feedback.
- **High Precision & Scalability**:
  - Implements **Exact Zero Check** using integer arithmetic to eliminate floating-point noise.
  - Uses `Decimal` for high-precision probability calculations (supporting probabilities as low as $10^{-78}$).
  - Scales to 1000+ qubits for specific structured circuits like Quantum Random Walks.

## Installation

### Prerequisites

- Python 3.8+
- [CUDD](https://github.com/ivmai/cudd) (Required for the `dd` library)

### Dependencies

Install the required Python packages:

```bash
pip install qiskit openqasm3 dd
```

*Note: The `dd` package requires a C compiler and the CUDD library to be installed and configured properly for the C extensions to work.*

## Usage

QSeqSim integrates with Qiskit. You can define your circuit using Qiskit's standard control flow operations (like `while_loop`, `if_test`, `switch`) and simulate it using `QiskitParser` and `BDDSimulator`.

### Example: Simulating a Simple While Loop

```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.parser import QiskitParser
from src.simulator import BDDSimulator

# 1. Define Qiskit Circuit
q = QuantumRegister(2, 'q')
c = ClassicalRegister(1, 'c')
qc = QuantumCircuit(q, c)

# Initialize qubits
qc.h(q[0])
qc.x(q[1])

# Define a while loop: run until c[0] == 1
# Note: This is a conceptual example. Ensure your loop has a termination condition.
with qc.while_loop((c, 0)):
    qc.h(q[0])
    qc.measure(q[0], c[0])

# Final measurement
qc.measure(q[1], c[0])

# 2. Parse the Circuit
print("Parsing circuit...")
parser = QiskitParser(qc)
structure = parser.parse()

# 3. Simulate
print("Starting simulation...")
sim = BDDSimulator(structure)
final_clbits = sim.run(mode='sample')

# 4. Output Results
print("Final Classical Register:", final_clbits)
sim.print_state_vec()
```

## Project Structure

- **`src/`**: Core source code.
  - `parser.py`: Parses Qiskit circuits and OpenQASM 3 into internal IR (CQC, DQC, SQC).
  - `kernel.py`: Implements the symbolic BDD kernel (`BDDCombSim`, `BDDSeqSim`) and math operations.
  - `simulator.py`: Main simulator class `BDDSimulator` orchestrating the execution flow.
- **`exp/`**: Experiment scripts and benchmarks.
  - `simulation/`: Contains specific experiments for RQC, Grover, and QRW.
    - `exp_engine.py`: Engine for running experiments and collecting metrics.
    - `gen_rqc.py`: Generates Random Quantum Circuit benchmarks.
    - `run_rqc_exp.py`: Runs the RQC benchmark suite.
- **`test/`**: Unit tests for parser and kernel.

## Experiments

The repository contains scripts to reproduce the experiments presented in the paper.

### Random Quantum Circuits (RQC)

To run the RQC benchmark suite which tests performance on combinational, dynamic, and sequential structures:

```bash
python exp/simulation/run_rqc_exp.py
```

This will generate benchmark circuits, run simulations, log results to `exp/simulation/data/rqc.log`, and generate a LaTeX table `rqc_result.tex`.

### Quantum Random Walk (QRW)

To run the Quantum Random Walk experiment (scaling up to 1024 qubits):

```bash
python exp/simulation/qrw.py
```

### Grover's Algorithm

To run the Grover search experiment:

```bash
python exp/simulation/grover.py
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
