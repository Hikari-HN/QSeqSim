from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

# Benchmark Configuration
# Target Qubits: 100
# Target Gates: 50
# Target Mid-Circuit Measurements: 5

q = QuantumRegister(100, 'q')
c = ClassicalRegister(5, 'c')
circ = QuantumCircuit(q, c)

# --- Initialization ---
circ.cx(q[89], q[71])
circ.h(q[73])
circ.cz(q[94], q[39])
circ.cx(q[98], q[21])
circ.cx(q[27], q[14])

# --- SQC Block: While Loop (Controlled by c[0]) ---
with circ.while_loop((c[0], 0)):
    # Loop Body
    circ.cz(q[6], q[97])
    circ.x(q[43])
    circ.cx(q[97], q[43])
    circ.h(q[31])
    circ.cx(q[42], q[29])
    circ.t(q[30])
    circ.t(q[91])
    circ.cz(q[27], q[96])
    # DQC: Mid-circuit measurement
    circ.measure(q[37], c[1])
    with circ.if_test((c[1], 1)):
        circ.x(q[98])
        circ.cz(q[91], q[21])
    circ.s(q[95])
    circ.cz(q[11], q[95])
    circ.t(q[40])
    circ.x(q[24])
    circ.cz(q[45], q[77])
    circ.cz(q[99], q[42])
    circ.cx(q[63], q[82])
    circ.x(q[62])
    # DQC: Mid-circuit measurement
    circ.measure(q[41], c[2])
    with circ.if_test((c[2], 1)):
        circ.cz(q[90], q[30])
        circ.x(q[49])
    circ.s(q[86])
    circ.h(q[91])
    circ.rz(math.pi/2, q[72])
    circ.cz(q[47], q[69])
    circ.x(q[61])
    circ.cz(q[72], q[3])
    circ.t(q[68])
    circ.h(q[42])
    # DQC: Mid-circuit measurement
    circ.measure(q[97], c[3])
    with circ.if_test((c[3], 1)):
        circ.cz(q[65], q[18])
        circ.rz(math.pi/2, q[87])
    circ.h(q[77])
    circ.rz(math.pi/2, q[33])
    circ.x(q[91])
    circ.rz(math.pi/2, q[39])
    circ.t(q[20])
    circ.x(q[62])
    circ.x(q[84])
    circ.rz(math.pi/2, q[95])
    # DQC: Mid-circuit measurement
    circ.measure(q[85], c[4])
    with circ.if_test((c[4], 1)):
        circ.t(q[97])
        circ.x(q[27])
    circ.cx(q[8], q[83])
    circ.h(q[82])
    circ.h(q[48])
    # Update Loop Condition (Must be FINAL op for q[0])
    # Ensure termination: Reset q[0] to |0> then apply H
    circ.reset(q[0])
    circ.h(q[0])
    circ.measure(q[0], c[0])

# Simulator Configuration by User
sim_mode = 'sample'
# No preset values needed for sample mode