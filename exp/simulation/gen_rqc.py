import random
import sys
import os

def generate_benchmark_script(filename, num_qubits, target_gates, target_mid_meas):
    """
    Generate Benchmark script that meets QSeqSim paper experiment requirements.
    Contains: While Loop, Nested If-Else, Sample Mode Configuration.
    
    [Key Improvements]:
    1. Ensure Trigger Qubit measurement is the last step in the loop body.
    2. Ensure Trigger Qubit is reset to superposition state before measurement to guarantee high loop termination probability.
    3. Random gates in the loop body are forbidden from operating on the Trigger Qubit to prevent logic interference.
    """
    
    # --- Statistics Counter ---
    stats = {
        "qubits": num_qubits,
        "static_gates": 0,
        "mid_measurements": 0
    }
    
    content = []
    def emit(line, indent=0):
        content.append("    " * indent + line)

    # 1. Header Imports
    emit("from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister")
    emit("import math")
    emit("")
    
    # 2. Register Definition
    # Number of classical bits = Target measurements (if 0, keep at least 1 for loop control)
    # c[0] fixed as the control bit for while loop
    num_clbits = max(1, target_mid_meas)
    
    emit(f"# Benchmark Configuration")
    emit(f"# Target Qubits: {num_qubits}")
    emit(f"# Target Gates: {target_gates}")
    emit(f"# Target Mid-Circuit Measurements: {target_mid_meas}")
    emit("")
    emit(f"q = QuantumRegister({num_qubits}, 'q')")
    emit(f"c = ClassicalRegister({num_clbits}, 'c')")
    emit("circ = QuantumCircuit(q, c)")
    emit("")

    # --- Helper Function: Generate Random Gates ---
    def add_random_gates(indent_level, count, forbidden_qubits=None):
        """
        Generate random gates.
        forbidden_qubits: List, forbids generating gates on these qubits.
        """
        if forbidden_qubits is None:
            forbidden_qubits = []
            
        available_qubits = [i for i in range(num_qubits) if i not in forbidden_qubits]
        
        # If no qubits available (extreme case), return directly
        if not available_qubits:
            return 

        for _ in range(count):
            gate_type = random.choice(['h', 't', 's', 'cx', 'cz', 'rz', 'x'])
            
            if gate_type in ['h', 't', 's', 'x']:
                q_idx = random.choice(available_qubits)
                emit(f"circ.{gate_type}(q[{q_idx}])", indent_level)
                stats["static_gates"] += 1
                
            elif gate_type == 'rz':
                q_idx = random.choice(available_qubits)
                emit(f"circ.rz(math.pi/2, q[{q_idx}])", indent_level)
                stats["static_gates"] += 1
                
            elif gate_type in ['cx', 'cz']:
                if len(available_qubits) >= 2:
                    q1, q2 = random.sample(available_qubits, 2)
                    emit(f"circ.{gate_type}(q[{q1}], q[{q2}])", indent_level)
                    stats["static_gates"] += 1

    # 3. Circuit Construction Logic
    
    # 3.1 Initialization Part
    init_gates = int(target_gates * 0.1)
    emit("# --- Initialization ---")
    add_random_gates(0, init_gates)
    emit("")

    # 3.2 While Loop Structure (Core Part)
    # Set c[0] as loop flag bit.
    # Set q[0] as loop trigger qubit (Trigger Qubit).
    loop_clbit_idx = 0
    trigger_qubit_idx = 0 
    
    # To ensure loop starts, assume c[0] is initially 0.
    # (In Qiskit, classical registers are initialized to 0 by default)
    
    emit(f"# --- SQC Block: While Loop (Controlled by c[{loop_clbit_idx}]) ---")
    emit(f"with circ.while_loop((c[{loop_clbit_idx}], 0)):") 
    
    current_indent = 1
    emit(f"# Loop Body", current_indent)
    
    # Calculate budget within loop body
    available_mid_meas_for_body = max(0, target_mid_meas - 1)
    remaining_gates = target_gates - init_gates
    
    # Reserve 2 gates for Trigger Reset/H operations to ensure termination
    remaining_gates -= 2
    
    # [Key]: When generating random gates in the loop body, strictly forbid operating on trigger_qubit_idx (q[0])
    # This prevents random logic from interfering with loop exit condition.
    forbidden_in_loop = [trigger_qubit_idx]
    
    if available_mid_meas_for_body <= 0:
        # No extra measurement budget, only generate gates
        add_random_gates(current_indent, remaining_gates, forbidden_qubits=forbidden_in_loop)
    else:
        # Have measurement budget, generate nested structure
        gates_per_segment = max(1, remaining_gates // (available_mid_meas_for_body + 1))
        
        meas_idx_pool = list(range(1, num_clbits))
        if not meas_idx_pool: meas_idx_pool = [0] 
        
        for i in range(available_mid_meas_for_body):
            # 1. Add some gates
            add_random_gates(current_indent, gates_per_segment, forbidden_qubits=forbidden_in_loop)
            remaining_gates -= gates_per_segment
            
            # 2. Add a DQC (If-Else)
            # Also avoid trigger qubit
            candidates = [x for x in range(num_qubits) if x not in forbidden_in_loop]
            if not candidates: candidates = [trigger_qubit_idx] # Fallback
            
            target_q = random.choice(candidates)
            target_c = meas_idx_pool[i % len(meas_idx_pool)]
            
            emit(f"# DQC: Mid-circuit measurement", current_indent)
            emit(f"circ.measure(q[{target_q}], c[{target_c}])", current_indent)
            stats["mid_measurements"] += 1
            
            emit(f"with circ.if_test((c[{target_c}], 1)):", current_indent)
            # Inside if branch, add only a few gates, and do not touch trigger
            add_random_gates(current_indent + 1, 2, forbidden_qubits=forbidden_in_loop)
            remaining_gates -= 2
            
        # Fill remaining gates
        if remaining_gates > 0:
            add_random_gates(current_indent, remaining_gates, forbidden_qubits=forbidden_in_loop)

    # 3.3 Loop Guard Update (Must be the LAST step of the Block)
    # [Key Logic]: To ensure termination, we force reset Trigger Qubit and apply H gate.
    # This ensures 50% probability of measuring 1 (exit loop) each time.
    # Geometric distribution expected value is 2 iterations, almost impossible to loop infinitely.
    
    emit(f"# Update Loop Condition (Must be FINAL op for q[{trigger_qubit_idx}])", current_indent)
    emit(f"# Ensure termination: Reset q[{trigger_qubit_idx}] to |0> then apply H", current_indent)
    emit(f"circ.reset(q[{trigger_qubit_idx}])", current_indent) 
    emit(f"circ.h(q[{trigger_qubit_idx}])", current_indent)
    emit(f"circ.measure(q[{trigger_qubit_idx}], c[{loop_clbit_idx}])", current_indent)
    
    stats["mid_measurements"] += 1
    stats["static_gates"] += 2 # Reset + H
    
    emit("")
    
    # 4. Simulator Configuration
    emit("# Simulator Configuration by User")
    emit("sim_mode = 'sample'")
    emit("# No preset values needed for sample mode")
    
    # --- Write to file ---
    with open(filename, 'w') as f:
        f.write("\n".join(content))
        
    return stats

if __name__ == "__main__":
    # Default values or user input
    try:
        if len(sys.argv) > 1:
            # Support command line arguments: python gen_rqc.py 100 500 10
            n = int(sys.argv[1])
            g = int(sys.argv[2])
            m = int(sys.argv[3])
        else:
            print("Using default/interactive mode.")
            n = int(input("Enter number of qubits (default 100): ") or 100)
            g = int(input("Enter target gate count (default 200): ") or 200)
            m = int(input("Enter target mid-circuit measurements (default 5): ") or 5)
    except ValueError:
        print("Invalid input, using defaults.")
        n, g, m = 100, 200, 5

    # --- Path and Filename Handling ---
    # Get directory of current script (exp/simulation)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target directory set to rqc under current script directory
    output_dir = os.path.join(current_script_dir, "rqc")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Filename format: rqc_q{n}_g{g}_m{m}.py
    short_filename = f"rqc_q{n}_g{g}_m{m}.py"
    full_path = os.path.join(output_dir, short_filename)
    
    final_stats = generate_benchmark_script(full_path, n, g, m)
    
    # Print table row format
    print("\n" + "="*65)
    print(f"{'Benchmark File':<25} | {'Qubits':<8} | {'Gates':<8} | {'Mid-Meas':<8}")
    print("-" * 65)
    print(f"{short_filename:<25} | {final_stats['qubits']:<8} | {final_stats['static_gates']:<8} | {final_stats['mid_measurements']:<8}")
    print("="*65 + "\n")
    print(f"Saved to: {full_path}")
