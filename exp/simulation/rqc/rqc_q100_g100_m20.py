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
circ.h(q[11])
circ.x(q[73])
circ.rz(math.pi/2, q[49])
circ.rz(math.pi/2, q[5])
circ.cx(q[40], q[55])
circ.rz(math.pi/2, q[12])
circ.s(q[76])
circ.rz(math.pi/2, q[49])
circ.h(q[62])
circ.cx(q[52], q[58])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.t(q[38])
    circ.rz(math.pi/2, q[28])
    circ.rz(math.pi/2, q[65])
    circ.cz(q[53], q[74])
    # DQC: Mid-circuit measurement
    circ.measure(q[38], c[1])
    with circ.if_test((c[1], 1)):
        circ.h(q[56])
        circ.cz(q[72], q[73])
    circ.s(q[3])
    circ.t(q[77])
    circ.x(q[11])
    circ.t(q[32])
    # DQC: Mid-circuit measurement
    circ.measure(q[35], c[2])
    with circ.if_test((c[2], 1)):
        circ.x(q[74])
        circ.rz(math.pi/2, q[67])
    circ.s(q[86])
    circ.h(q[19])
    circ.rz(math.pi/2, q[30])
    circ.cz(q[5], q[62])
    # DQC: Mid-circuit measurement
    circ.measure(q[94], c[3])
    with circ.if_test((c[3], 1)):
        circ.cz(q[17], q[3])
        circ.h(q[1])
    circ.cx(q[15], q[90])
    circ.x(q[31])
    circ.h(q[10])
    circ.t(q[29])
    # DQC: Mid-circuit measurement
    circ.measure(q[45], c[4])
    with circ.if_test((c[4], 1)):
        circ.cx(q[11], q[71])
        circ.cz(q[17], q[84])
    circ.rz(math.pi/2, q[77])
    circ.cx(q[30], q[35])
    circ.t(q[87])
    circ.t(q[14])
    # DQC: Mid-circuit measurement
    circ.measure(q[42], c[5])
    with circ.if_test((c[5], 1)):
        circ.x(q[7])
        circ.cz(q[76], q[19])
    circ.h(q[69])
    circ.t(q[71])
    circ.t(q[41])
    circ.t(q[97])
    # DQC: Mid-circuit measurement
    circ.measure(q[23], c[6])
    with circ.if_test((c[6], 1)):
        circ.cz(q[6], q[83])
        circ.t(q[78])
    circ.cx(q[33], q[4])
    circ.h(q[82])
    circ.rz(math.pi/2, q[48])
    circ.rz(math.pi/2, q[95])
    # DQC: Mid-circuit measurement
    circ.measure(q[82], c[7])
    with circ.if_test((c[7], 1)):
        circ.cz(q[9], q[1])
        circ.s(q[75])
    circ.t(q[79])
    circ.t(q[27])
    circ.rz(math.pi/2, q[11])
    circ.s(q[93])
    # DQC: Mid-circuit measurement
    circ.measure(q[7], c[8])
    with circ.if_test((c[8], 1)):
        circ.rz(math.pi/2, q[13])
        circ.cz(q[40], q[7])
    circ.rz(math.pi/2, q[18])
    circ.x(q[23])
    circ.rz(math.pi/2, q[93])
    circ.s(q[60])
    # DQC: Mid-circuit measurement
    circ.measure(q[48], c[9])
    with circ.if_test((c[9], 1)):
        circ.t(q[90])
        circ.x(q[65])
    circ.x(q[73])
    circ.rz(math.pi/2, q[70])
    circ.h(q[71])
    circ.cx(q[92], q[6])
    # DQC: Mid-circuit measurement
    circ.measure(q[99], c[10])
    with circ.if_test((c[10], 1)):
        circ.h(q[54])
        circ.cz(q[68], q[30])
    circ.s(q[33])
    circ.x(q[70])
    circ.rz(math.pi/2, q[40])
    circ.h(q[54])
    # DQC: Mid-circuit measurement
    circ.measure(q[52], c[11])
    with circ.if_test((c[11], 1)):
        circ.t(q[68])
        circ.cz(q[35], q[52])
    circ.t(q[12])
    circ.cz(q[59], q[15])
    circ.t(q[21])
    circ.rz(math.pi/2, q[85])
    # DQC: Mid-circuit measurement
    circ.measure(q[53], c[12])
    with circ.if_test((c[12], 1)):
        circ.cx(q[40], q[26])
        circ.h(q[96])
    circ.s(q[25])
    circ.t(q[2])
    circ.cx(q[56], q[44])
    circ.cx(q[22], q[69])
    # DQC: Mid-circuit measurement
    circ.measure(q[67], c[13])
    with circ.if_test((c[13], 1)):
        circ.x(q[88])
        circ.rz(math.pi/2, q[12])
    circ.t(q[70])
    circ.s(q[78])
    circ.cz(q[15], q[76])
    circ.cz(q[7], q[50])
    # DQC: Mid-circuit measurement
    circ.measure(q[21], c[14])
    with circ.if_test((c[14], 1)):
        circ.cx(q[87], q[85])
        circ.cz(q[70], q[39])
    circ.h(q[8])
    circ.s(q[74])
    circ.cz(q[7], q[28])
    circ.h(q[83])
    # DQC: Mid-circuit measurement
    circ.measure(q[77], c[15])
    with circ.if_test((c[15], 1)):
        circ.cz(q[96], q[22])
        circ.x(q[69])
    circ.cx(q[54], q[16])
    circ.s(q[14])
    circ.s(q[12])
    circ.rz(math.pi/2, q[64])
    # DQC: Mid-circuit measurement
    circ.measure(q[20], c[16])
    with circ.if_test((c[16], 1)):
        circ.cx(q[22], q[29])
        circ.rz(math.pi/2, q[33])
    circ.cz(q[73], q[15])
    circ.s(q[41])
    circ.t(q[21])
    circ.x(q[61])
    # DQC: Mid-circuit measurement
    circ.measure(q[21], c[17])
    with circ.if_test((c[17], 1)):
        circ.rz(math.pi/2, q[59])
        circ.t(q[5])
    circ.s(q[42])
    circ.s(q[89])
    circ.cz(q[11], q[66])
    circ.x(q[37])
    # DQC: Mid-circuit measurement
    circ.measure(q[71], c[18])
    with circ.if_test((c[18], 1)):
        circ.cz(q[90], q[82])
        circ.x(q[6])
    circ.cx(q[31], q[74])
    circ.x(q[72])
    circ.x(q[66])
    circ.s(q[39])
    # DQC: Mid-circuit measurement
    circ.measure(q[25], c[19])
    with circ.if_test((c[19], 1)):
        circ.t(q[90])
        circ.rz(math.pi/2, q[34])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode