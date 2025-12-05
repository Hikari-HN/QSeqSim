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
circ.t(q[48])
circ.s(q[0])
circ.cz(q[38], q[79])
circ.h(q[30])
circ.s(q[99])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.cx(q[26], q[18])
    circ.t(q[65])
    circ.h(q[71])
    circ.rz(math.pi/2, q[46])
    # DQC: Mid-circuit measurement
    circ.measure(q[98], c[1])
    with circ.if_test((c[1], 1)):
        circ.cx(q[66], q[94])
        circ.cx(q[39], q[21])
    circ.h(q[85])
    circ.cz(q[8], q[56])
    circ.cx(q[94], q[4])
    circ.x(q[12])
    # DQC: Mid-circuit measurement
    circ.measure(q[68], c[2])
    with circ.if_test((c[2], 1)):
        circ.x(q[33])
        circ.t(q[63])
    circ.rz(math.pi/2, q[19])
    circ.t(q[48])
    circ.t(q[38])
    circ.cz(q[1], q[79])
    # DQC: Mid-circuit measurement
    circ.measure(q[33], c[3])
    with circ.if_test((c[3], 1)):
        circ.rz(math.pi/2, q[95])
        circ.cx(q[54], q[13])
    circ.h(q[80])
    circ.cx(q[23], q[84])
    circ.cz(q[34], q[21])
    circ.s(q[5])
    # DQC: Mid-circuit measurement
    circ.measure(q[77], c[4])
    with circ.if_test((c[4], 1)):
        circ.s(q[5])
        circ.t(q[20])
    circ.s(q[56])
    circ.s(q[48])
    circ.rz(math.pi/2, q[94])
    circ.cx(q[38], q[18])
    # DQC: Mid-circuit measurement
    circ.measure(q[10], c[5])
    with circ.if_test((c[5], 1)):
        circ.cx(q[8], q[90])
        circ.cx(q[1], q[13])
    circ.h(q[36])
    circ.rz(math.pi/2, q[99])
    circ.h(q[26])
    circ.h(q[57])
    # DQC: Mid-circuit measurement
    circ.measure(q[57], c[6])
    with circ.if_test((c[6], 1)):
        circ.cx(q[35], q[30])
        circ.x(q[95])
    circ.t(q[50])
    circ.rz(math.pi/2, q[12])
    circ.t(q[93])
    circ.cx(q[59], q[80])
    # DQC: Mid-circuit measurement
    circ.measure(q[71], c[7])
    with circ.if_test((c[7], 1)):
        circ.cx(q[58], q[35])
        circ.t(q[5])
    circ.cz(q[6], q[31])
    circ.cx(q[5], q[16])
    circ.cz(q[30], q[53])
    circ.cz(q[47], q[25])
    # DQC: Mid-circuit measurement
    circ.measure(q[45], c[8])
    with circ.if_test((c[8], 1)):
        circ.h(q[8])
        circ.rz(math.pi/2, q[78])
    circ.cz(q[20], q[85])
    circ.t(q[67])
    circ.t(q[79])
    circ.t(q[40])
    # DQC: Mid-circuit measurement
    circ.measure(q[20], c[9])
    with circ.if_test((c[9], 1)):
        circ.s(q[61])
        circ.cz(q[59], q[63])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode