import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.kernel import BDDSeqSim

n = int(input("请输入总量子比特数 n: "))
it = int(input("请输入迭代次数 it: "))

Sim = BDDSeqSim(n, n - 1, 3)
result_list = [0] * (it - 1) + [1]
input_basis_list = [0] * len(result_list)
cnt = 0
Sim.init_stored_state_by_basis(0)

start_time = time.time()
for result, input_basis in zip(result_list, input_basis_list):
    cnt += 1
    Sim.init_input_state_by_basis(input_basis)
    Sim.init_comb_bdd()

    for i in range(n-1):
        Sim.H(i)

    Sim.H(n-1)
    Sim.multi_controlled_X(list(range(n-1)), n-1)
    Sim.H(n-1)

    for i in range(n-1):
        Sim.H(i)
        Sim.X(i)

    Sim.H(n-2)
    Sim.multi_controlled_X(list(range(n-2)), n-2)
    Sim.H(n-2)

    for i in range(n-1):
        Sim.H(i)
        Sim.X(i)

    Sim.measure2([result])
    end_time = time.time()
    print("至此%d轮，运行时间: "%cnt, end_time - start_time, "秒")
# end_time = time.time()
#
# print("运行时间: ", end_time - start_time, "秒")
