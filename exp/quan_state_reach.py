import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import time
from src.kernel import BDDSeqSim

# Define configurations to test: (total number of qubits n, number of iterations k)
configs = [(256, 1), (256, 2), (256, 3), (256, 4), (256, 5),
           (256, 6), (256, 7), (256, 8), (256, 9), (256, 10)]

for n, it in configs:
    print(f"===== Starting test configuration: Number of qubits={n}, Number of iterations={it} =====")
    cnt = 0
    # Initialize simulator (keep the parameters n-1 and 3 from the original code)
    Sim = BDDSeqSim(n, n - 1, 3)
    # Construct result list and input basis list
    result_list = [0] * (it - 1) + [1]
    input_basis_list = [0] * len(result_list)
    
    Sim.init_stored_state_by_basis(0)
    
    start_time = time.time()
    for result, input_basis in zip(result_list, input_basis_list):
        cnt += 1
        Sim.init_input_state_by_basis(input_basis)
        Sim.init_comb_bdd()
        Sim.H(1)
        Sim.cwalk(1, list(range(2, n)))
        Sim.multi_controlled_X(list(range(1, n)), 0)
        Sim.measure([result])
    
    # Output results for current configuration
    print(f"Probability result: {Sim.prob_list[-1]}")
    end_time = time.time()
    print(f"Running time: {end_time - start_time:.4f} seconds")
    print(f"===== Test configuration: Number of qubits={n}, Number of iterations={it} completed =====\n")