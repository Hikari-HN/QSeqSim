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
circ.h(q[76])
circ.t(q[40])
circ.h(q[42])
circ.h(q[19])
circ.x(q[26])
circ.cz(q[19], q[8])
circ.cz(q[99], q[76])
circ.rz(math.pi/2, q[81])
circ.rz(math.pi/2, q[15])
circ.t(q[74])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.t(q[93])
    circ.s(q[14])
    circ.cz(q[97], q[7])
    circ.cz(q[88], q[4])
    circ.rz(math.pi/2, q[50])
    circ.t(q[46])
    circ.cz(q[94], q[4])
    circ.rz(math.pi/2, q[32])
    # DQC: Mid-circuit measurement
    circ.measure(q[17], c[1])
    with circ.if_test((c[1], 1)):
        circ.s(q[72])
        circ.s(q[75])
    circ.x(q[33])
    circ.cx(q[78], q[41])
    circ.x(q[4])
    circ.s(q[28])
    circ.x(q[97])
    circ.rz(math.pi/2, q[89])
    circ.t(q[10])
    circ.x(q[60])
    # DQC: Mid-circuit measurement
    circ.measure(q[9], c[2])
    with circ.if_test((c[2], 1)):
        circ.h(q[32])
        circ.rz(math.pi/2, q[9])
    circ.h(q[50])
    circ.h(q[28])
    circ.h(q[24])
    circ.x(q[41])
    circ.cx(q[21], q[95])
    circ.rz(math.pi/2, q[92])
    circ.t(q[98])
    circ.h(q[8])
    # DQC: Mid-circuit measurement
    circ.measure(q[28], c[3])
    with circ.if_test((c[3], 1)):
        circ.s(q[37])
        circ.x(q[87])
    circ.x(q[1])
    circ.x(q[55])
    circ.cx(q[57], q[95])
    circ.cz(q[89], q[67])
    circ.h(q[90])
    circ.h(q[77])
    circ.h(q[35])
    circ.cx(q[21], q[92])
    # DQC: Mid-circuit measurement
    circ.measure(q[67], c[4])
    with circ.if_test((c[4], 1)):
        circ.h(q[2])
        circ.cz(q[19], q[48])
    circ.t(q[47])
    circ.cz(q[19], q[55])
    circ.cx(q[17], q[91])
    circ.cx(q[44], q[94])
    circ.s(q[10])
    circ.cz(q[62], q[68])
    circ.rz(math.pi/2, q[4])
    circ.cz(q[66], q[73])
    # DQC: Mid-circuit measurement
    circ.measure(q[76], c[5])
    with circ.if_test((c[5], 1)):
        circ.rz(math.pi/2, q[41])
        circ.cx(q[76], q[85])
    circ.x(q[79])
    circ.h(q[53])
    circ.cx(q[94], q[85])
    circ.h(q[11])
    circ.s(q[14])
    circ.x(q[53])
    circ.s(q[34])
    circ.t(q[54])
    # DQC: Mid-circuit measurement
    circ.measure(q[13], c[6])
    with circ.if_test((c[6], 1)):
        circ.cx(q[83], q[5])
        circ.t(q[62])
    circ.h(q[26])
    circ.s(q[54])
    circ.cx(q[77], q[30])
    circ.h(q[51])
    circ.cx(q[49], q[11])
    circ.cx(q[37], q[71])
    circ.h(q[73])
    circ.cx(q[34], q[25])
    # DQC: Mid-circuit measurement
    circ.measure(q[60], c[7])
    with circ.if_test((c[7], 1)):
        circ.cx(q[88], q[90])
        circ.rz(math.pi/2, q[37])
    circ.rz(math.pi/2, q[16])
    circ.cx(q[66], q[25])
    circ.s(q[22])
    circ.x(q[79])
    circ.x(q[50])
    circ.s(q[66])
    circ.x(q[54])
    circ.rz(math.pi/2, q[31])
    # DQC: Mid-circuit measurement
    circ.measure(q[83], c[8])
    with circ.if_test((c[8], 1)):
        circ.h(q[95])
        circ.s(q[16])
    circ.cx(q[67], q[94])
    circ.cz(q[49], q[10])
    circ.cz(q[48], q[24])
    circ.h(q[87])
    circ.x(q[89])
    circ.t(q[85])
    circ.s(q[18])
    circ.t(q[99])
    # DQC: Mid-circuit measurement
    circ.measure(q[82], c[9])
    with circ.if_test((c[9], 1)):
        circ.rz(math.pi/2, q[50])
        circ.x(q[47])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode