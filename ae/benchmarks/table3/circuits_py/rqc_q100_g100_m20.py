# Generator seed: 110020
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 100
# Target Mid-Circuit Measurements: 20

q = QuantumRegister(100, 'q')
c = ClassicalRegister(20, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.cx(q[30], q[37])
circ.h(q[56])
circ.cz(q[2], q[69])
circ.rz(math.pi/2, q[10])
circ.cz(q[53], q[85])
circ.x(q[77])
circ.cz(q[75], q[65])
circ.cx(q[23], q[24])
circ.x(q[95])
circ.s(q[5])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.cx(q[61], q[13])
    circ.s(q[40])
    circ.t(q[61])
    circ.s(q[18])
    # DQC: Mid-circuit measurement
    circ.measure(q[8], c[1])
    with circ.if_test((c[1], 1)):
        circ.t(q[35])
        circ.rz(math.pi/2, q[37])
    circ.h(q[45])
    circ.s(q[4])
    circ.x(q[58])
    circ.h(q[77])
    # DQC: Mid-circuit measurement
    circ.measure(q[78], c[2])
    with circ.if_test((c[2], 1)):
        circ.cz(q[41], q[3])
        circ.s(q[39])
    circ.cx(q[45], q[60])
    circ.x(q[33])
    circ.rz(math.pi/2, q[6])
    circ.cx(q[61], q[8])
    # DQC: Mid-circuit measurement
    circ.measure(q[82], c[3])
    with circ.if_test((c[3], 1)):
        circ.x(q[36])
        circ.cx(q[5], q[52])
    circ.x(q[61])
    circ.t(q[23])
    circ.x(q[15])
    circ.cz(q[22], q[93])
    # DQC: Mid-circuit measurement
    circ.measure(q[51], c[4])
    with circ.if_test((c[4], 1)):
        circ.s(q[42])
        circ.x(q[73])
    circ.h(q[55])
    circ.cx(q[99], q[15])
    circ.x(q[79])
    circ.cz(q[58], q[14])
    # DQC: Mid-circuit measurement
    circ.measure(q[98], c[5])
    with circ.if_test((c[5], 1)):
        circ.rz(math.pi/2, q[75])
        circ.rz(math.pi/2, q[9])
    circ.t(q[76])
    circ.h(q[25])
    circ.s(q[57])
    circ.cx(q[72], q[28])
    # DQC: Mid-circuit measurement
    circ.measure(q[77], c[6])
    with circ.if_test((c[6], 1)):
        circ.x(q[73])
        circ.h(q[93])
    circ.h(q[89])
    circ.cz(q[91], q[83])
    circ.cz(q[45], q[21])
    circ.h(q[71])
    # DQC: Mid-circuit measurement
    circ.measure(q[96], c[7])
    with circ.if_test((c[7], 1)):
        circ.x(q[54])
        circ.x(q[27])
    circ.cx(q[85], q[82])
    circ.x(q[56])
    circ.t(q[44])
    circ.h(q[27])
    # DQC: Mid-circuit measurement
    circ.measure(q[52], c[8])
    with circ.if_test((c[8], 1)):
        circ.cx(q[10], q[30])
        circ.cz(q[41], q[2])
    circ.rz(math.pi/2, q[18])
    circ.t(q[85])
    circ.x(q[37])
    circ.t(q[13])
    # DQC: Mid-circuit measurement
    circ.measure(q[80], c[9])
    with circ.if_test((c[9], 1)):
        circ.cx(q[84], q[77])
        circ.x(q[68])
    circ.h(q[77])
    circ.x(q[73])
    circ.cx(q[7], q[58])
    circ.rz(math.pi/2, q[62])
    # DQC: Mid-circuit measurement
    circ.measure(q[39], c[10])
    with circ.if_test((c[10], 1)):
        circ.rz(math.pi/2, q[37])
        circ.rz(math.pi/2, q[89])
    circ.cz(q[95], q[14])
    circ.x(q[37])
    circ.x(q[64])
    circ.cx(q[28], q[4])
    # DQC: Mid-circuit measurement
    circ.measure(q[21], c[11])
    with circ.if_test((c[11], 1)):
        circ.h(q[26])
        circ.h(q[63])
    circ.s(q[47])
    circ.rz(math.pi/2, q[62])
    circ.cx(q[52], q[84])
    circ.x(q[69])
    # DQC: Mid-circuit measurement
    circ.measure(q[13], c[12])
    with circ.if_test((c[12], 1)):
        circ.cz(q[99], q[91])
        circ.s(q[47])
    circ.h(q[41])
    circ.cx(q[41], q[88])
    circ.t(q[50])
    circ.t(q[33])
    # DQC: Mid-circuit measurement
    circ.measure(q[25], c[13])
    with circ.if_test((c[13], 1)):
        circ.t(q[3])
        circ.cz(q[72], q[27])
    circ.cz(q[72], q[51])
    circ.cx(q[87], q[14])
    circ.x(q[57])
    circ.cz(q[24], q[79])
    # DQC: Mid-circuit measurement
    circ.measure(q[31], c[14])
    with circ.if_test((c[14], 1)):
        circ.cx(q[62], q[26])
        circ.cx(q[35], q[79])
    circ.s(q[63])
    circ.cx(q[30], q[60])
    circ.x(q[53])
    circ.x(q[67])
    # DQC: Mid-circuit measurement
    circ.measure(q[71], c[15])
    with circ.if_test((c[15], 1)):
        circ.cx(q[36], q[81])
        circ.t(q[33])
    circ.s(q[87])
    circ.cx(q[21], q[56])
    circ.cx(q[64], q[26])
    circ.t(q[34])
    # DQC: Mid-circuit measurement
    circ.measure(q[57], c[16])
    with circ.if_test((c[16], 1)):
        circ.t(q[67])
        circ.cz(q[46], q[96])
    circ.t(q[77])
    circ.cz(q[31], q[2])
    circ.x(q[57])
    circ.x(q[74])
    # DQC: Mid-circuit measurement
    circ.measure(q[73], c[17])
    with circ.if_test((c[17], 1)):
        circ.s(q[41])
        circ.h(q[28])
    circ.rz(math.pi/2, q[30])
    circ.rz(math.pi/2, q[53])
    circ.h(q[27])
    circ.rz(math.pi/2, q[9])
    # DQC: Mid-circuit measurement
    circ.measure(q[38], c[18])
    with circ.if_test((c[18], 1)):
        circ.t(q[7])
        circ.h(q[31])
    circ.rz(math.pi/2, q[83])
    circ.rz(math.pi/2, q[71])
    circ.h(q[34])
    circ.x(q[40])
    # DQC: Mid-circuit measurement
    circ.measure(q[64], c[19])
    with circ.if_test((c[19], 1)):
        circ.rz(math.pi/2, q[34])
        circ.cx(q[35], q[63])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode