import os
import sys
import math
import random

# Ensure repo root on path when running from Docker or locally
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.parser import QiskitParser
from src.simulator import BDDSimulator


def build_circuit():
    q = QuantumRegister(1, "q")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(q, c)

    # while (c[0] == 0) { H; measure -> c[0] }
    with qc.while_loop((c[0], 0)):
        qc.h(q[0])
        qc.measure(q[0], c[0])

    return qc


def run_sample(qc):
    print("\n=== SAMPLE MODE ===")
    parser = QiskitParser(qc)
    blocks = parser.parse()

    sim = BDDSimulator(blocks, precision=32)
    cl = sim.run(mode="sample")
    print("clbits:", cl)
    sim.print_state_vec()


def run_preset(qc):
    print("\n=== PRESET MODE ===")
    parser = QiskitParser(qc)
    blocks = parser.parse()

    # Force outcomes for the loop guard measurement:
    # 0, 0, 1  => terminate after 3 iterations
    presets = {0: [0, 0, 1]}

    sim = BDDSimulator(blocks, precision=32)
    cl = sim.run(mode="preset", presets=presets)
    print("clbits:", cl)
    print("global_probability:", sim.global_probability)
    sim.print_state_vec()


if __name__ == "__main__":
    qc = build_circuit()
    print(qc)

    run_sample(qc)
    run_preset(qc)