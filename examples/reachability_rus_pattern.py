import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.parser import QiskitParser
from src.simulator import BDDSimulator


def build_loop():
    q = QuantumRegister(1, "q")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(q, c)

    # Prepare a biased measurement (not uniform):
    # H then S then H gives a different distribution than plain H in some kernels;
    # even if distribution ends up close to 0.5, the example still demonstrates the API.
    qc.h(q[0])

    # while (c[0] == 1) { measure }
    # We will preset a pattern that ends with 0 to terminate.
    qc.measure(q[0], c[0])
    with qc.while_loop((c[0], 1)):
        qc.h(q[0])
        qc.measure(q[0], c[0])

    return qc


if __name__ == "__main__":
    qc = build_loop()
    print(qc)

    parser = QiskitParser(qc)
    blocks = parser.parse()

    # We want outcomes: 1,1,1,0
    presets = {0: [1, 1, 1, 0]}

    sim = BDDSimulator(blocks)
    cl = sim.run(mode="preset", presets=presets)

    print("\nObserved clbits:", cl)
    print("Path probability (global_probability):", sim.global_probability)
    print("\nInterpretation: in preset mode, global_probability equals the probability of the fixed outcome pattern.")
