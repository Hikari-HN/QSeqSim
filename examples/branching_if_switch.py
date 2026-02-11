import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.parser import QiskitParser
from src.simulator import BDDSimulator


def build_circuit():
    q = QuantumRegister(2, "q")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(q, c)

    qc.h(q[0])
    qc.measure(q[0], c[0])   # control flag

    # switch on c[0]
    with qc.switch(c[0]) as case:
        with case(0):
            qc.x(q[1])
        with case(1):
            qc.z(q[1])

    # if/else on the same flag
    with qc.if_test((c[0], 1)) as else_:
        qc.h(q[1])
    with else_:
        qc.s(q[1])

    qc.measure(q[1], c[0])   # final readout candidate
    return qc


if __name__ == "__main__":
    qc = build_circuit()
    print(qc)

    parser = QiskitParser(qc)
    parser.to_qasm3()
    print("\n--- OpenQASM 3 ---")
    print(parser.qasm_str)

    blocks = parser.parse()
    print("\nParsed blocks:")
    for b in blocks:
        print(" ", b)

    sim = BDDSimulator(blocks)
    out = sim.run(mode="sample")
    print("\nclbits:", out)
    sim.print_state_vec()