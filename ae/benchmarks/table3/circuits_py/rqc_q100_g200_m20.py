# Generator seed: 120020
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 200
# Target Mid-Circuit Measurements: 20

q = QuantumRegister(100, 'q')
c = ClassicalRegister(20, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.rz(math.pi/2, q[41])
circ.s(q[34])
circ.cx(q[49], q[85])
circ.t(q[85])
circ.x(q[88])
circ.rz(math.pi/2, q[49])
circ.s(q[37])
circ.rz(math.pi/2, q[83])
circ.cx(q[71], q[5])
circ.h(q[70])
circ.rz(math.pi/2, q[64])
circ.cx(q[96], q[67])
circ.t(q[93])
circ.t(q[41])
circ.t(q[64])
circ.x(q[13])
circ.rz(math.pi/2, q[83])
circ.cz(q[99], q[30])
circ.h(q[69])
circ.cz(q[41], q[36])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.x(q[21])
    circ.h(q[64])
    circ.h(q[51])
    circ.rz(math.pi/2, q[88])
    circ.h(q[82])
    circ.cx(q[58], q[3])
    circ.t(q[13])
    circ.t(q[58])
    # DQC: Mid-circuit measurement
    circ.measure(q[91], c[1])
    with circ.if_test((c[1], 1)):
        circ.cz(q[3], q[54])
        circ.s(q[70])
    circ.s(q[89])
    circ.rz(math.pi/2, q[22])
    circ.x(q[44])
    circ.cz(q[36], q[64])
    circ.x(q[93])
    circ.cz(q[91], q[65])
    circ.x(q[54])
    circ.rz(math.pi/2, q[67])
    # DQC: Mid-circuit measurement
    circ.measure(q[53], c[2])
    with circ.if_test((c[2], 1)):
        circ.t(q[57])
        circ.cx(q[41], q[15])
    circ.rz(math.pi/2, q[1])
    circ.t(q[59])
    circ.x(q[80])
    circ.cz(q[26], q[64])
    circ.rz(math.pi/2, q[25])
    circ.cx(q[32], q[29])
    circ.cx(q[73], q[78])
    circ.rz(math.pi/2, q[75])
    # DQC: Mid-circuit measurement
    circ.measure(q[69], c[3])
    with circ.if_test((c[3], 1)):
        circ.x(q[54])
        circ.cz(q[85], q[28])
    circ.x(q[50])
    circ.rz(math.pi/2, q[6])
    circ.t(q[34])
    circ.h(q[58])
    circ.t(q[37])
    circ.cx(q[80], q[64])
    circ.cz(q[23], q[53])
    circ.h(q[56])
    # DQC: Mid-circuit measurement
    circ.measure(q[48], c[4])
    with circ.if_test((c[4], 1)):
        circ.h(q[31])
        circ.s(q[33])
    circ.x(q[93])
    circ.x(q[59])
    circ.h(q[61])
    circ.cx(q[78], q[60])
    circ.rz(math.pi/2, q[93])
    circ.t(q[10])
    circ.cx(q[81], q[8])
    circ.rz(math.pi/2, q[43])
    # DQC: Mid-circuit measurement
    circ.measure(q[88], c[5])
    with circ.if_test((c[5], 1)):
        circ.cx(q[5], q[81])
        circ.s(q[43])
    circ.t(q[75])
    circ.t(q[6])
    circ.s(q[70])
    circ.h(q[50])
    circ.t(q[79])
    circ.h(q[41])
    circ.cz(q[13], q[44])
    circ.s(q[46])
    # DQC: Mid-circuit measurement
    circ.measure(q[78], c[6])
    with circ.if_test((c[6], 1)):
        circ.t(q[40])
        circ.s(q[28])
    circ.t(q[88])
    circ.cx(q[1], q[11])
    circ.rz(math.pi/2, q[27])
    circ.x(q[15])
    circ.rz(math.pi/2, q[98])
    circ.x(q[71])
    circ.x(q[29])
    circ.rz(math.pi/2, q[63])
    # DQC: Mid-circuit measurement
    circ.measure(q[38], c[7])
    with circ.if_test((c[7], 1)):
        circ.cz(q[38], q[44])
        circ.t(q[41])
    circ.cx(q[92], q[42])
    circ.h(q[14])
    circ.cz(q[96], q[45])
    circ.cz(q[3], q[90])
    circ.s(q[9])
    circ.h(q[28])
    circ.h(q[33])
    circ.rz(math.pi/2, q[68])
    # DQC: Mid-circuit measurement
    circ.measure(q[17], c[8])
    with circ.if_test((c[8], 1)):
        circ.s(q[8])
        circ.rz(math.pi/2, q[90])
    circ.cx(q[36], q[81])
    circ.h(q[60])
    circ.h(q[53])
    circ.rz(math.pi/2, q[81])
    circ.h(q[98])
    circ.cz(q[33], q[63])
    circ.cz(q[28], q[53])
    circ.h(q[62])
    # DQC: Mid-circuit measurement
    circ.measure(q[9], c[9])
    with circ.if_test((c[9], 1)):
        circ.cz(q[14], q[27])
        circ.h(q[12])
    circ.s(q[29])
    circ.x(q[42])
    circ.t(q[74])
    circ.rz(math.pi/2, q[95])
    circ.t(q[47])
    circ.x(q[72])
    circ.x(q[33])
    circ.s(q[29])
    # DQC: Mid-circuit measurement
    circ.measure(q[70], c[10])
    with circ.if_test((c[10], 1)):
        circ.rz(math.pi/2, q[20])
        circ.t(q[98])
    circ.x(q[76])
    circ.x(q[30])
    circ.rz(math.pi/2, q[91])
    circ.t(q[68])
    circ.s(q[23])
    circ.s(q[71])
    circ.cx(q[12], q[25])
    circ.cx(q[47], q[75])
    # DQC: Mid-circuit measurement
    circ.measure(q[81], c[11])
    with circ.if_test((c[11], 1)):
        circ.rz(math.pi/2, q[44])
        circ.cz(q[29], q[13])
    circ.t(q[71])
    circ.t(q[30])
    circ.x(q[96])
    circ.rz(math.pi/2, q[67])
    circ.cx(q[8], q[67])
    circ.cx(q[71], q[56])
    circ.x(q[61])
    circ.h(q[46])
    # DQC: Mid-circuit measurement
    circ.measure(q[6], c[12])
    with circ.if_test((c[12], 1)):
        circ.h(q[21])
        circ.x(q[5])
    circ.s(q[4])
    circ.rz(math.pi/2, q[40])
    circ.x(q[63])
    circ.h(q[10])
    circ.s(q[83])
    circ.rz(math.pi/2, q[15])
    circ.t(q[33])
    circ.cz(q[53], q[32])
    # DQC: Mid-circuit measurement
    circ.measure(q[35], c[13])
    with circ.if_test((c[13], 1)):
        circ.cx(q[52], q[62])
        circ.cz(q[19], q[33])
    circ.rz(math.pi/2, q[99])
    circ.h(q[3])
    circ.h(q[31])
    circ.x(q[35])
    circ.cz(q[88], q[63])
    circ.cz(q[9], q[67])
    circ.rz(math.pi/2, q[34])
    circ.cz(q[96], q[78])
    # DQC: Mid-circuit measurement
    circ.measure(q[69], c[14])
    with circ.if_test((c[14], 1)):
        circ.rz(math.pi/2, q[59])
        circ.h(q[28])
    circ.cz(q[51], q[98])
    circ.x(q[1])
    circ.x(q[12])
    circ.rz(math.pi/2, q[95])
    circ.x(q[69])
    circ.s(q[26])
    circ.t(q[39])
    circ.cx(q[9], q[8])
    # DQC: Mid-circuit measurement
    circ.measure(q[97], c[15])
    with circ.if_test((c[15], 1)):
        circ.t(q[65])
        circ.h(q[59])
    circ.rz(math.pi/2, q[88])
    circ.cx(q[48], q[56])
    circ.t(q[34])
    circ.rz(math.pi/2, q[47])
    circ.h(q[61])
    circ.t(q[84])
    circ.s(q[75])
    circ.h(q[72])
    # DQC: Mid-circuit measurement
    circ.measure(q[48], c[16])
    with circ.if_test((c[16], 1)):
        circ.s(q[1])
        circ.h(q[18])
    circ.cz(q[69], q[57])
    circ.h(q[60])
    circ.s(q[8])
    circ.t(q[2])
    circ.x(q[18])
    circ.h(q[67])
    circ.x(q[15])
    circ.rz(math.pi/2, q[21])
    # DQC: Mid-circuit measurement
    circ.measure(q[42], c[17])
    with circ.if_test((c[17], 1)):
        circ.cz(q[74], q[32])
        circ.h(q[92])
    circ.x(q[65])
    circ.h(q[37])
    circ.t(q[5])
    circ.s(q[16])
    circ.h(q[93])
    circ.h(q[89])
    circ.x(q[98])
    circ.s(q[83])
    # DQC: Mid-circuit measurement
    circ.measure(q[93], c[18])
    with circ.if_test((c[18], 1)):
        circ.t(q[37])
        circ.t(q[63])
    circ.rz(math.pi/2, q[51])
    circ.rz(math.pi/2, q[90])
    circ.cz(q[25], q[86])
    circ.t(q[20])
    circ.cz(q[97], q[21])
    circ.rz(math.pi/2, q[34])
    circ.t(q[29])
    circ.h(q[14])
    # DQC: Mid-circuit measurement
    circ.measure(q[12], c[19])
    with circ.if_test((c[19], 1)):
        circ.cz(q[76], q[6])
        circ.cz(q[63], q[8])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode