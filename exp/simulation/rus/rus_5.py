# rus_5.py (Figure 10b)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

q = QuantumRegister(2, 'q')
c = ClassicalRegister(1, 'c') 
circ = QuantumCircuit(q, c)

def rus_trial(circuit, anc, tar, c):
    circuit.h(anc)
    circuit.s(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.sdg(anc)
    circuit.h(anc)
    circuit.cz(anc, tar)
    circuit.h(anc)
    circuit.s(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.x(tar)
    circuit.cz(anc, tar)
    circuit.h(anc)
    circuit.s(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.t(anc)
    circuit.h(anc)
    circuit.s(anc)
    circuit.h(anc)
    circuit.x(tar)
    circuit.measure(anc, c)

rus_trial(circ, q[0], q[1], c[0])

# Notice: this RUS example success condition is c = 1!
with circ.while_loop((c, 0)):
    rus_trial(circ, q[0], q[1], c[0])

# Simulator Configuration by User
import os
sim_mode = 'preset' 
ITER_TIME = int(os.environ.get("ITER_TIME", "100"))
preset_values = {0: [0] * (ITER_TIME - 1) + [1]} 