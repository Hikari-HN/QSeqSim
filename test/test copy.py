# from demo1 import qec
# from demo2 import rus
# from rqc_n100_d10 import qc
from parser import QiskitParser
from simulator import BDDSimulator

from qiskit.circuit import QuantumCircuit, Clbit, Qubit
bits = [Qubit(), Qubit(), Clbit()]
qc = QuantumCircuit(bits)
 
with qc.while_loop((bits[2], 0)):
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    with qc.if_test((0, 1)):
        qc.x(0)

parser = QiskitParser(qc)
parser.to_qasm3()
print(parser.qasm_str)
structure = parser.parse()
# sim = BDDSimulator(structure)
# sim.run(mode='sample')
# sim.print_state_vec()