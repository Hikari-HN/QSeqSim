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
circ.t(q[49])
circ.cx(q[90], q[78])
circ.h(q[73])
circ.h(q[36])
circ.s(q[21])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.s(q[68])
    circ.rz(math.pi/2, q[91])
    # DQC: Mid-circuit measurement
    circ.measure(q[79], c[1])
    with circ.if_test((c[1], 1)):
        circ.x(q[11])
        circ.cx(q[21], q[17])
    circ.cz(q[37], q[41])
    circ.x(q[97])
    # DQC: Mid-circuit measurement
    circ.measure(q[23], c[2])
    with circ.if_test((c[2], 1)):
        circ.t(q[93])
        circ.cz(q[74], q[73])
    circ.cx(q[35], q[56])
    circ.s(q[43])
    # DQC: Mid-circuit measurement
    circ.measure(q[12], c[3])
    with circ.if_test((c[3], 1)):
        circ.h(q[44])
        circ.h(q[58])
    circ.h(q[5])
    circ.h(q[35])
    # DQC: Mid-circuit measurement
    circ.measure(q[90], c[4])
    with circ.if_test((c[4], 1)):
        circ.h(q[14])
        circ.h(q[26])
    circ.x(q[36])
    circ.x(q[16])
    # DQC: Mid-circuit measurement
    circ.measure(q[19], c[5])
    with circ.if_test((c[5], 1)):
        circ.s(q[74])
        circ.h(q[88])
    circ.cz(q[49], q[42])
    circ.x(q[69])
    # DQC: Mid-circuit measurement
    circ.measure(q[75], c[6])
    with circ.if_test((c[6], 1)):
        circ.h(q[22])
        circ.x(q[10])
    circ.x(q[30])
    circ.h(q[66])
    # DQC: Mid-circuit measurement
    circ.measure(q[62], c[7])
    with circ.if_test((c[7], 1)):
        circ.s(q[58])
        circ.rz(math.pi/2, q[17])
    circ.rz(math.pi/2, q[43])
    circ.t(q[43])
    # DQC: Mid-circuit measurement
    circ.measure(q[35], c[8])
    with circ.if_test((c[8], 1)):
        circ.cz(q[13], q[56])
        circ.rz(math.pi/2, q[38])
    circ.h(q[30])
    circ.s(q[98])
    # DQC: Mid-circuit measurement
    circ.measure(q[4], c[9])
    with circ.if_test((c[9], 1)):
        circ.x(q[87])
        circ.t(q[48])
    circ.s(q[78])
    circ.t(q[12])
    # DQC: Mid-circuit measurement
    circ.measure(q[75], c[10])
    with circ.if_test((c[10], 1)):
        circ.t(q[52])
        circ.h(q[25])
    circ.rz(math.pi/2, q[79])
    circ.x(q[38])
    # DQC: Mid-circuit measurement
    circ.measure(q[97], c[11])
    with circ.if_test((c[11], 1)):
        circ.cz(q[6], q[8])
        circ.cz(q[4], q[97])
    circ.h(q[60])
    circ.s(q[77])
    # DQC: Mid-circuit measurement
    circ.measure(q[83], c[12])
    with circ.if_test((c[12], 1)):
        circ.cz(q[71], q[6])
        circ.s(q[74])
    circ.s(q[98])
    circ.s(q[59])
    # DQC: Mid-circuit measurement
    circ.measure(q[6], c[13])
    with circ.if_test((c[13], 1)):
        circ.t(q[29])
        circ.rz(math.pi/2, q[31])
    circ.s(q[16])
    circ.h(q[19])
    # DQC: Mid-circuit measurement
    circ.measure(q[67], c[14])
    with circ.if_test((c[14], 1)):
        circ.cz(q[34], q[18])
        circ.s(q[49])
    circ.rz(math.pi/2, q[61])
    circ.h(q[76])
    # DQC: Mid-circuit measurement
    circ.measure(q[8], c[15])
    with circ.if_test((c[15], 1)):
        circ.cx(q[36], q[58])
        circ.s(q[48])
    circ.rz(math.pi/2, q[59])
    circ.cz(q[47], q[7])
    # DQC: Mid-circuit measurement
    circ.measure(q[79], c[16])
    with circ.if_test((c[16], 1)):
        circ.h(q[4])
        circ.t(q[34])
    circ.s(q[40])
    circ.cx(q[40], q[27])
    # DQC: Mid-circuit measurement
    circ.measure(q[94], c[17])
    with circ.if_test((c[17], 1)):
        circ.t(q[68])
        circ.cz(q[81], q[63])
    circ.t(q[71])
    circ.rz(math.pi/2, q[15])
    # DQC: Mid-circuit measurement
    circ.measure(q[9], c[18])
    with circ.if_test((c[18], 1)):
        circ.t(q[1])
        circ.h(q[48])
    circ.h(q[13])
    circ.s(q[20])
    # DQC: Mid-circuit measurement
    circ.measure(q[18], c[19])
    with circ.if_test((c[19], 1)):
        circ.x(q[26])
        circ.rz(math.pi/2, q[29])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode