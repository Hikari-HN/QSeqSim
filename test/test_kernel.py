import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import random
from src.kernel import BDDCombSim
from math import pi

Sim = BDDCombSim(5, 3)
Sim.init_basis_state(16) # |10000>
Sim.CNOT(0, 1) # |10000> -> |11000>
Sim.CNOT(1, 2) # |11000> -> |11100>
Sim.X(0) # |11100> -> |01100>
Sim.CNOT(0, 3) # |01100> -> |01100>
Sim.CNOT(1, 3) # |01100> -> |01110>
Sim.CNOT(0, 4) # |01110> -> |01110>
Sim.CNOT(2, 4) # |01110> -> |01111> 

out1 = 1
out2 = 1
Sim.measure([3], [out1])
Sim.measure([4], [out2])
if out1 == 1:
    Sim.X(3) # |01111> -> |01101>
if out2 == 1:
    Sim.X(4) # |01101> -> |01100>
if out1 == 1 and out2 == 1:
    Sim.X(0) # |01111> -> |11111>
if out1 == 1 and out2 == 0:
    Sim.X(1)
if out1 == 0 and out2 == 1:
    Sim.X(2)

Sim.print_state_vec()
print('Finally, r = %d.' % Sim.r)
