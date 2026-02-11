# Generator seed: 110010
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 100
# Target Mid-Circuit Measurements: 10

q = QuantumRegister(100, 'q')
c = ClassicalRegister(10, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.cx(q[42], q[98])
circ.x(q[53])
circ.h(q[24])
circ.cz(q[44], q[70])
circ.s(q[20])
circ.cx(q[54], q[8])
circ.cx(q[40], q[6])
circ.s(q[49])
circ.s(q[7])
circ.cx(q[86], q[94])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.x(q[51])
    circ.s(q[8])
    circ.rz(math.pi/2, q[98])
    circ.h(q[75])
    circ.cx(q[79], q[25])
    circ.t(q[99])
    circ.t(q[58])
    circ.t(q[79])
    # DQC: Mid-circuit measurement
    circ.measure(q[56], c[1])
    with circ.if_test((c[1], 1)):
        circ.x(q[28])
        circ.x(q[39])
    circ.cz(q[36], q[32])
    circ.rz(math.pi/2, q[59])
    circ.t(q[18])
    circ.x(q[86])
    circ.s(q[86])
    circ.s(q[93])
    circ.rz(math.pi/2, q[35])
    circ.x(q[39])
    # DQC: Mid-circuit measurement
    circ.measure(q[69], c[2])
    with circ.if_test((c[2], 1)):
        circ.rz(math.pi/2, q[39])
        circ.h(q[3])
    circ.rz(math.pi/2, q[15])
    circ.cz(q[43], q[78])
    circ.s(q[38])
    circ.cx(q[9], q[88])
    circ.rz(math.pi/2, q[57])
    circ.h(q[60])
    circ.s(q[96])
    circ.rz(math.pi/2, q[14])
    # DQC: Mid-circuit measurement
    circ.measure(q[13], c[3])
    with circ.if_test((c[3], 1)):
        circ.rz(math.pi/2, q[17])
        circ.cx(q[80], q[12])
    circ.x(q[12])
    circ.cz(q[49], q[46])
    circ.h(q[3])
    circ.t(q[81])
    circ.cx(q[91], q[29])
    circ.cz(q[60], q[72])
    circ.s(q[91])
    circ.h(q[99])
    # DQC: Mid-circuit measurement
    circ.measure(q[58], c[4])
    with circ.if_test((c[4], 1)):
        circ.s(q[67])
        circ.rz(math.pi/2, q[74])
    circ.h(q[64])
    circ.t(q[28])
    circ.x(q[35])
    circ.t(q[79])
    circ.t(q[64])
    circ.s(q[80])
    circ.cz(q[2], q[99])
    circ.s(q[99])
    # DQC: Mid-circuit measurement
    circ.measure(q[66], c[5])
    with circ.if_test((c[5], 1)):
        circ.x(q[89])
        circ.s(q[23])
    circ.cz(q[99], q[83])
    circ.s(q[64])
    circ.x(q[32])
    circ.cz(q[17], q[40])
    circ.cz(q[31], q[47])
    circ.rz(math.pi/2, q[93])
    circ.cx(q[66], q[31])
    circ.x(q[39])
    # DQC: Mid-circuit measurement
    circ.measure(q[73], c[6])
    with circ.if_test((c[6], 1)):
        circ.rz(math.pi/2, q[42])
        circ.cz(q[66], q[23])
    circ.x(q[9])
    circ.t(q[28])
    circ.t(q[16])
    circ.t(q[59])
    circ.s(q[77])
    circ.cx(q[45], q[30])
    circ.rz(math.pi/2, q[61])
    circ.t(q[84])
    # DQC: Mid-circuit measurement
    circ.measure(q[55], c[7])
    with circ.if_test((c[7], 1)):
        circ.t(q[91])
        circ.cz(q[36], q[28])
    circ.x(q[58])
    circ.t(q[67])
    circ.rz(math.pi/2, q[32])
    circ.rz(math.pi/2, q[34])
    circ.rz(math.pi/2, q[17])
    circ.x(q[31])
    circ.x(q[59])
    circ.rz(math.pi/2, q[3])
    # DQC: Mid-circuit measurement
    circ.measure(q[82], c[8])
    with circ.if_test((c[8], 1)):
        circ.s(q[55])
        circ.cz(q[60], q[58])
    circ.x(q[82])
    circ.s(q[70])
    circ.h(q[42])
    circ.cz(q[23], q[30])
    circ.rz(math.pi/2, q[77])
    circ.s(q[49])
    circ.cx(q[21], q[7])
    circ.cx(q[5], q[41])
    # DQC: Mid-circuit measurement
    circ.measure(q[15], c[9])
    with circ.if_test((c[9], 1)):
        circ.cz(q[54], q[69])
        circ.cx(q[79], q[41])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode