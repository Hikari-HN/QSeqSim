# Generator seed: 105005
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 50
# Target Mid-Circuit Measurements: 5

q = QuantumRegister(100, 'q')
c = ClassicalRegister(5, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.rz(math.pi/2, q[93])
circ.cz(q[74], q[63])
circ.cx(q[20], q[38])
circ.cx(q[6], q[19])
circ.rz(math.pi/2, q[3])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.x(q[18])
    circ.x(q[54])
    circ.cx(q[67], q[3])
    circ.h(q[75])
    circ.rz(math.pi/2, q[83])
    circ.rz(math.pi/2, q[62])
    circ.h(q[82])
    circ.h(q[87])
    # DQC: Mid-circuit measurement
    circ.measure(q[67], c[1])
    with circ.if_test((c[1], 1)):
        circ.h(q[1])
        circ.x(q[46])
    circ.x(q[66])
    circ.t(q[21])
    circ.x(q[5])
    circ.s(q[19])
    circ.t(q[2])
    circ.h(q[30])
    circ.rz(math.pi/2, q[6])
    circ.h(q[6])
    # DQC: Mid-circuit measurement
    circ.measure(q[2], c[2])
    with circ.if_test((c[2], 1)):
        circ.h(q[23])
        circ.h(q[56])
    circ.rz(math.pi/2, q[60])
    circ.s(q[64])
    circ.t(q[25])
    circ.cz(q[86], q[77])
    circ.rz(math.pi/2, q[61])
    circ.x(q[81])
    circ.h(q[16])
    circ.x(q[51])
    # DQC: Mid-circuit measurement
    circ.measure(q[43], c[3])
    with circ.if_test((c[3], 1)):
        circ.cz(q[72], q[69])
        circ.h(q[75])
    circ.rz(math.pi/2, q[99])
    circ.cz(q[55], q[54])
    circ.rz(math.pi/2, q[77])
    circ.s(q[58])
    circ.rz(math.pi/2, q[39])
    circ.s(q[7])
    circ.rz(math.pi/2, q[28])
    circ.h(q[59])
    # DQC: Mid-circuit measurement
    circ.measure(q[85], c[4])
    with circ.if_test((c[4], 1)):
        circ.cz(q[13], q[86])
        circ.s(q[54])
    circ.h(q[5])
    circ.h(q[2])
    circ.x(q[20])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode