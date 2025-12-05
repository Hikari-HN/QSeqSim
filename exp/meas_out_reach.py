import sys
import os
import time
import math  # For standard deviation calculation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from simulation.rus.rus_1 import circ
from src.parser import QiskitParser
from src.simulator import BDDSimulator

# Configuration: repeat runs per k to reduce random fluctuation
REPEAT_RUNS = 5  # Adjust this value (e.g., 10 for more stable results)

parser = QiskitParser(circ)
structure = parser.parse()
sim = BDDSimulator(structure)

# Global array to store probabilities for cumulative sum
all_probabilities = []

for k in range(1, 10):
    run_times = []  # Store time of each repeat run
    current_prob = None  # Probability is consistent for the same k
    
    # Run multiple times for the same k to get stable time metrics
    for _ in range(REPEAT_RUNS):
        start = time.perf_counter()
        sim.run(mode='preset', presets={0: [1] * (k - 1) + [0]})
        end = time.perf_counter() 
        run_times.append(end - start)
        current_prob = sim.global_probability  # Probability is stable for same k

    # Calculate statistical metrics for time
    avg_time = sum(run_times) / REPEAT_RUNS
    std_time = math.sqrt(sum([(t - avg_time)**2 for t in run_times]) / REPEAT_RUNS)
    
    # Update global probability array and cumulative sum
    all_probabilities.append(current_prob)
    cumulative_prob = sum(all_probabilities)

    # Print results with high precision (8 decimal places for time)
    print(f"=== Iteration k = {k} ===")
    print(f"Path Probability for k={k}: {current_prob:.5f}")
    print(f"Average Execution Time (n={REPEAT_RUNS} runs): {avg_time:.5f} seconds")
    print(f"Time Standard Deviation: {std_time:.5f} seconds")
    print(f"Cumulative Termination Probability (1-{k}): {cumulative_prob:.5f}")
    print("-" * 70 + "\n")