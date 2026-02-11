# Generator seed: 105010
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 50
# Target Mid-Circuit Measurements: 10

q = QuantumRegister(100, 'q')
c = ClassicalRegister(10, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.t(q[93])
circ.rz(math.pi/2, q[28])
circ.rz(math.pi/2, q[58])
circ.cz(q[72], q[2])
circ.rz(math.pi/2, q[79])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.rz(math.pi/2, q[80])
    circ.s(q[18])
    circ.rz(math.pi/2, q[10])
    circ.cz(q[31], q[56])
    # DQC: Mid-circuit measurement
    circ.measure(q[72], c[1])
    with circ.if_test((c[1], 1)):
        circ.t(q[74])
        circ.h(q[31])
    circ.h(q[65])
    circ.cz(q[32], q[7])
    circ.cz(q[58], q[17])
    circ.cx(q[80], q[86])
    # DQC: Mid-circuit measurement
    circ.measure(q[81], c[2])
    with circ.if_test((c[2], 1)):
        circ.t(q[83])
        circ.s(q[3])
    circ.rz(math.pi/2, q[73])
    circ.s(q[80])
    circ.cz(q[25], q[37])
    circ.x(q[23])
    # DQC: Mid-circuit measurement
    circ.measure(q[55], c[3])
    with circ.if_test((c[3], 1)):
        circ.s(q[51])
        circ.rz(math.pi/2, q[30])
    circ.h(q[21])
    circ.cz(q[52], q[4])
    circ.s(q[61])
    circ.h(q[96])
    # DQC: Mid-circuit measurement
    circ.measure(q[81], c[4])
    with circ.if_test((c[4], 1)):
        circ.rz(math.pi/2, q[8])
        circ.cx(q[79], q[56])
    circ.t(q[96])
    circ.cz(q[35], q[92])
    circ.x(q[52])
    circ.rz(math.pi/2, q[75])
    # DQC: Mid-circuit measurement
    circ.measure(q[1], c[5])
    with circ.if_test((c[5], 1)):
        circ.rz(math.pi/2, q[69])
        circ.rz(math.pi/2, q[61])
    circ.h(q[68])
    circ.h(q[67])
    circ.s(q[9])
    circ.rz(math.pi/2, q[58])
    # DQC: Mid-circuit measurement
    circ.measure(q[29], c[6])
    with circ.if_test((c[6], 1)):
        circ.t(q[79])
        circ.s(q[51])
    circ.s(q[33])
    circ.rz(math.pi/2, q[59])
    circ.h(q[3])
    circ.cz(q[24], q[36])
    # DQC: Mid-circuit measurement
    circ.measure(q[38], c[7])
    with circ.if_test((c[7], 1)):
        circ.x(q[73])
        circ.rz(math.pi/2, q[52])
    circ.rz(math.pi/2, q[3])
    circ.h(q[25])
    circ.s(q[73])
    circ.cz(q[14], q[13])
    # DQC: Mid-circuit measurement
    circ.measure(q[98], c[8])
    with circ.if_test((c[8], 1)):
        circ.h(q[63])
        circ.h(q[86])
    circ.cz(q[30], q[79])
    circ.x(q[39])
    circ.x(q[68])
    circ.x(q[9])
    # DQC: Mid-circuit measurement
    circ.measure(q[27], c[9])
    with circ.if_test((c[9], 1)):
        circ.s(q[86])
        circ.t(q[74])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode