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
circ.cz(q[59], q[16])
circ.t(q[14])
circ.cz(q[12], q[29])
circ.h(q[31])
circ.h(q[10])
circ.t(q[61])
circ.h(q[14])
circ.cz(q[7], q[88])
circ.h(q[95])
circ.cz(q[48], q[72])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.t(q[34])
    circ.rz(math.pi/2, q[79])
    circ.cx(q[86], q[91])
    circ.x(q[3])
    circ.t(q[17])
    circ.cx(q[47], q[32])
    circ.x(q[40])
    circ.x(q[16])
    circ.x(q[5])
    circ.h(q[89])
    circ.s(q[74])
    circ.rz(math.pi/2, q[42])
    circ.h(q[64])
    circ.h(q[73])
    circ.h(q[90])
    circ.cx(q[92], q[38])
    circ.s(q[28])
    # DQC: Mid-circuit measurement
    circ.measure(q[21], c[1])
    with circ.if_test((c[1], 1)):
        circ.h(q[63])
        circ.t(q[82])
    circ.h(q[16])
    circ.x(q[53])
    circ.t(q[51])
    circ.t(q[87])
    circ.cx(q[57], q[64])
    circ.cz(q[45], q[18])
    circ.rz(math.pi/2, q[94])
    circ.h(q[53])
    circ.h(q[93])
    circ.t(q[43])
    circ.h(q[65])
    circ.h(q[38])
    circ.s(q[47])
    circ.cz(q[32], q[50])
    circ.cx(q[22], q[24])
    circ.cz(q[17], q[25])
    circ.h(q[22])
    # DQC: Mid-circuit measurement
    circ.measure(q[41], c[2])
    with circ.if_test((c[2], 1)):
        circ.x(q[78])
        circ.h(q[18])
    circ.x(q[87])
    circ.h(q[1])
    circ.s(q[62])
    circ.h(q[93])
    circ.cz(q[19], q[99])
    circ.cz(q[61], q[64])
    circ.cx(q[21], q[47])
    circ.t(q[32])
    circ.s(q[85])
    circ.s(q[65])
    circ.s(q[24])
    circ.t(q[85])
    circ.rz(math.pi/2, q[61])
    circ.cz(q[58], q[68])
    circ.t(q[77])
    circ.t(q[86])
    circ.rz(math.pi/2, q[15])
    # DQC: Mid-circuit measurement
    circ.measure(q[25], c[3])
    with circ.if_test((c[3], 1)):
        circ.rz(math.pi/2, q[32])
        circ.x(q[80])
    circ.h(q[56])
    circ.cz(q[65], q[31])
    circ.s(q[51])
    circ.h(q[19])
    circ.x(q[1])
    circ.t(q[1])
    circ.rz(math.pi/2, q[44])
    circ.h(q[86])
    circ.h(q[87])
    circ.x(q[82])
    circ.cx(q[28], q[74])
    circ.h(q[88])
    circ.cx(q[96], q[50])
    circ.h(q[17])
    circ.x(q[30])
    circ.t(q[72])
    circ.rz(math.pi/2, q[61])
    # DQC: Mid-circuit measurement
    circ.measure(q[43], c[4])
    with circ.if_test((c[4], 1)):
        circ.cx(q[84], q[14])
        circ.cz(q[70], q[1])
    circ.cx(q[81], q[17])
    circ.s(q[74])
    circ.cx(q[85], q[27])
    circ.rz(math.pi/2, q[60])
    circ.cz(q[69], q[13])
    circ.x(q[86])
    circ.s(q[77])
    circ.t(q[39])
    circ.h(q[51])
    circ.rz(math.pi/2, q[58])
    circ.rz(math.pi/2, q[22])
    circ.rz(math.pi/2, q[10])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode