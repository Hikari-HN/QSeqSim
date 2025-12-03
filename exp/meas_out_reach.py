import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import time
from src.kernel import BDDSeqSim

it = int(input("请输入迭代次数 k: "))
cnt = 0
Sim = BDDSeqSim(2, 1, 3)
result_list = [0] * (it - 1) + [1]
input_basis_list = [0] * len(result_list)
Sim.init_stored_state_by_basis(0)

start_time = time.time()
for result, input_basis in zip(result_list, input_basis_list):
    cnt += 1
    Sim.init_input_state_by_basis(input_basis)
    Sim.init_comb_bdd()
    Sim.H(0)
    Sim.CNOT(0, 1)
    Sim.measure([result])
    end_time = time.time()
    
print(Sim.prob_list[-1])
end_time = time.time()

print("运行时间: ", end_time - start_time, "秒")