from src.parser import QiskitParser
from src.simulator import BDDSimulator
from demo.demo1 import qec

parser = QiskitParser(qec)
structure = parser.parse()
sim = BDDSimulator(structure)
sim.run(mode='sample')
sim.print_state_vec()

from demo.demo2 import rus

parser = QiskitParser(rus)
structure = parser.parse()
sim = BDDSimulator(structure)
sim.run(mode='preset', presets={0: [1]})
sim.print_state_vec()