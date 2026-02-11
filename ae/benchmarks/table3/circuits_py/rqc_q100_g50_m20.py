# Generator seed: 105020
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 50
# Target Mid-Circuit Measurements: 20

q = QuantumRegister(100, 'q')
c = ClassicalRegister(20, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.x(q[85])
circ.h(q[47])
circ.x(q[94])
circ.rz(math.pi/2, q[16])
circ.rz(math.pi/2, q[60])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.cz(q[4], q[41])
    circ.x(q[90])
    # DQC: Mid-circuit measurement
    circ.measure(q[47], c[1])
    with circ.if_test((c[1], 1)):
        circ.cz(q[55], q[65])
        circ.cx(q[65], q[60])
    circ.cz(q[44], q[5])
    circ.x(q[27])
    # DQC: Mid-circuit measurement
    circ.measure(q[76], c[2])
    with circ.if_test((c[2], 1)):
        circ.s(q[90])
        circ.s(q[96])
    circ.t(q[55])
    circ.t(q[89])
    # DQC: Mid-circuit measurement
    circ.measure(q[19], c[3])
    with circ.if_test((c[3], 1)):
        circ.s(q[57])
        circ.rz(math.pi/2, q[4])
    circ.x(q[29])
    circ.rz(math.pi/2, q[75])
    # DQC: Mid-circuit measurement
    circ.measure(q[64], c[4])
    with circ.if_test((c[4], 1)):
        circ.t(q[75])
        circ.cx(q[64], q[50])
    circ.cx(q[23], q[33])
    circ.x(q[75])
    # DQC: Mid-circuit measurement
    circ.measure(q[24], c[5])
    with circ.if_test((c[5], 1)):
        circ.rz(math.pi/2, q[3])
        circ.x(q[54])
    circ.t(q[47])
    circ.cz(q[86], q[22])
    # DQC: Mid-circuit measurement
    circ.measure(q[27], c[6])
    with circ.if_test((c[6], 1)):
        circ.rz(math.pi/2, q[48])
        circ.rz(math.pi/2, q[93])
    circ.cz(q[12], q[38])
    circ.t(q[31])
    # DQC: Mid-circuit measurement
    circ.measure(q[5], c[7])
    with circ.if_test((c[7], 1)):
        circ.cz(q[77], q[58])
        circ.x(q[36])
    circ.s(q[19])
    circ.rz(math.pi/2, q[40])
    # DQC: Mid-circuit measurement
    circ.measure(q[2], c[8])
    with circ.if_test((c[8], 1)):
        circ.cz(q[60], q[92])
        circ.cx(q[56], q[78])
    circ.cz(q[48], q[80])
    circ.cz(q[54], q[9])
    # DQC: Mid-circuit measurement
    circ.measure(q[4], c[9])
    with circ.if_test((c[9], 1)):
        circ.rz(math.pi/2, q[21])
        circ.x(q[42])
    circ.cz(q[62], q[52])
    circ.rz(math.pi/2, q[4])
    # DQC: Mid-circuit measurement
    circ.measure(q[51], c[10])
    with circ.if_test((c[10], 1)):
        circ.rz(math.pi/2, q[87])
        circ.x(q[71])
    circ.x(q[17])
    circ.s(q[42])
    # DQC: Mid-circuit measurement
    circ.measure(q[55], c[11])
    with circ.if_test((c[11], 1)):
        circ.cx(q[78], q[8])
        circ.cx(q[19], q[5])
    circ.cx(q[54], q[82])
    circ.x(q[8])
    # DQC: Mid-circuit measurement
    circ.measure(q[49], c[12])
    with circ.if_test((c[12], 1)):
        circ.cx(q[61], q[96])
        circ.h(q[95])
    circ.cz(q[22], q[38])
    circ.h(q[20])
    # DQC: Mid-circuit measurement
    circ.measure(q[63], c[13])
    with circ.if_test((c[13], 1)):
        circ.cz(q[86], q[78])
        circ.t(q[75])
    circ.h(q[82])
    circ.cz(q[17], q[44])
    # DQC: Mid-circuit measurement
    circ.measure(q[56], c[14])
    with circ.if_test((c[14], 1)):
        circ.rz(math.pi/2, q[7])
        circ.x(q[56])
    circ.s(q[65])
    circ.t(q[96])
    # DQC: Mid-circuit measurement
    circ.measure(q[90], c[15])
    with circ.if_test((c[15], 1)):
        circ.x(q[95])
        circ.t(q[42])
    circ.cz(q[88], q[17])
    circ.cx(q[25], q[64])
    # DQC: Mid-circuit measurement
    circ.measure(q[80], c[16])
    with circ.if_test((c[16], 1)):
        circ.t(q[45])
        circ.rz(math.pi/2, q[99])
    circ.s(q[45])
    circ.cx(q[1], q[63])
    # DQC: Mid-circuit measurement
    circ.measure(q[98], c[17])
    with circ.if_test((c[17], 1)):
        circ.rz(math.pi/2, q[67])
        circ.rz(math.pi/2, q[90])
    circ.cz(q[34], q[1])
    circ.cx(q[47], q[48])
    # DQC: Mid-circuit measurement
    circ.measure(q[41], c[18])
    with circ.if_test((c[18], 1)):
        circ.h(q[15])
        circ.h(q[59])
    circ.t(q[42])
    circ.rz(math.pi/2, q[22])
    # DQC: Mid-circuit measurement
    circ.measure(q[80], c[19])
    with circ.if_test((c[19], 1)):
        circ.t(q[87])
        circ.h(q[79])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode