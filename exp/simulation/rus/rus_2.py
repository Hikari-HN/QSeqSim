# rus_2.py (Figure 7)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

q = QuantumRegister(2, 'q')
c = ClassicalRegister(1, 'c') 
circ = QuantumCircuit(q, c)

def rus_trial(circuit, anc, tar, c):
    circuit.h(anc)
    circuit.tdg(anc)
    circuit.h(anc)
    circuit.cz(anc, tar)
    circuit.h(tar)
    circuit.t(tar)
    circuit.h(tar)
    circuit.tdg(tar)
    circuit.h(tar)
    circuit.cz(anc, tar)
    circuit.h(anc)
    circuit.tdg(anc)
    circuit.h(anc)
    circuit.measure(anc, c)

rus_trial(circ, q[0], q[1], c[0])

def reset_ancilla(circuit, anc):
    circuit.x(anc)

with circ.while_loop((c, 1)):
    reset_ancilla(circ, q[0])
    rus_trial(circ, q[0], q[1], c[0])

# Simulator Configuration by User
sim_mode = 'preset' 
ITER_TIME = 100
preset_values = {0: [1] * (ITER_TIME - 1) + [0]} 