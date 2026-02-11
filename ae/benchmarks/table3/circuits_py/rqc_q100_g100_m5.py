# Generator seed: 110005
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 100
# Target Mid-Circuit Measurements: 5

q = QuantumRegister(100, 'q')
c = ClassicalRegister(5, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.rz(math.pi/2, q[64])
circ.x(q[74])
circ.rz(math.pi/2, q[23])
circ.cx(q[56], q[95])
circ.s(q[55])
circ.t(q[84])
circ.h(q[26])
circ.cz(q[55], q[14])
circ.h(q[24])
circ.h(q[34])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.x(q[65])
    circ.cx(q[29], q[14])
    circ.s(q[4])
    circ.rz(math.pi/2, q[9])
    circ.cz(q[72], q[64])
    circ.h(q[27])
    circ.cz(q[59], q[23])
    circ.s(q[80])
    circ.rz(math.pi/2, q[2])
    circ.x(q[57])
    circ.t(q[67])
    circ.t(q[62])
    circ.cx(q[62], q[47])
    circ.rz(math.pi/2, q[26])
    circ.h(q[99])
    circ.s(q[10])
    circ.x(q[50])
    # DQC: Mid-circuit measurement
    circ.measure(q[8], c[1])
    with circ.if_test((c[1], 1)):
        circ.s(q[19])
        circ.cz(q[83], q[63])
    circ.s(q[47])
    circ.h(q[9])
    circ.x(q[60])
    circ.cx(q[52], q[41])
    circ.cz(q[88], q[73])
    circ.t(q[99])
    circ.rz(math.pi/2, q[66])
    circ.rz(math.pi/2, q[51])
    circ.h(q[75])
    circ.cz(q[74], q[26])
    circ.t(q[32])
    circ.t(q[69])
    circ.x(q[6])
    circ.t(q[20])
    circ.h(q[44])
    circ.s(q[68])
    circ.x(q[53])
    # DQC: Mid-circuit measurement
    circ.measure(q[93], c[2])
    with circ.if_test((c[2], 1)):
        circ.h(q[51])
        circ.rz(math.pi/2, q[65])
    circ.h(q[37])
    circ.cz(q[10], q[85])
    circ.s(q[83])
    circ.x(q[12])
    circ.rz(math.pi/2, q[76])
    circ.x(q[80])
    circ.x(q[95])
    circ.x(q[28])
    circ.t(q[52])
    circ.s(q[24])
    circ.cz(q[83], q[65])
    circ.x(q[99])
    circ.x(q[80])
    circ.rz(math.pi/2, q[75])
    circ.t(q[24])
    circ.h(q[93])
    circ.h(q[72])
    # DQC: Mid-circuit measurement
    circ.measure(q[86], c[3])
    with circ.if_test((c[3], 1)):
        circ.s(q[25])
        circ.rz(math.pi/2, q[25])
    circ.x(q[33])
    circ.rz(math.pi/2, q[23])
    circ.x(q[59])
    circ.t(q[63])
    circ.cz(q[30], q[95])
    circ.rz(math.pi/2, q[18])
    circ.h(q[11])
    circ.x(q[57])
    circ.rz(math.pi/2, q[31])
    circ.cx(q[64], q[22])
    circ.x(q[25])
    circ.t(q[65])
    circ.s(q[66])
    circ.s(q[35])
    circ.t(q[66])
    circ.x(q[68])
    circ.s(q[91])
    # DQC: Mid-circuit measurement
    circ.measure(q[30], c[4])
    with circ.if_test((c[4], 1)):
        circ.h(q[5])
        circ.rz(math.pi/2, q[61])
    circ.cz(q[35], q[44])
    circ.s(q[18])
    circ.s(q[98])
    circ.t(q[59])
    circ.cx(q[81], q[70])
    circ.cx(q[36], q[47])
    circ.x(q[71])
    circ.cx(q[29], q[80])
    circ.cz(q[78], q[51])
    circ.cz(q[86], q[21])
    circ.t(q[91])
    circ.h(q[28])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode