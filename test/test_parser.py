from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.parser import QiskitParser
from src.simulator import BDDSimulator
import math

if __name__ == "__main__":
    print("="*50)
    print(" TEST: Full Feature Coverage (Qiskit Native)")
    print("="*50)

    q = QuantumRegister(3, 'q')
    c = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(q, c)

    # ----------------------------------------------------
    # 1. CQC & Gates
    # ----------------------------------------------------
    qc.h(q[0])
    qc.x(q[1])
    qc.rx(math.pi/2, q[2]) 
    qc.swap(q[0], q[1])    

    # ----------------------------------------------------
    # 2. For Loop (Fixed)
    # ----------------------------------------------------
    with qc.for_loop(range(2)) as i:
        qc.z(q[0])

    # ----------------------------------------------------
    # 3. Switch (DQC)
    # ----------------------------------------------------
    qc.measure(q[0], c[0])
    
    with qc.switch(c[0]) as case:
        with case(0):
            qc.x(q[1])
        with case(1):
            qc.z(q[1])

    # ----------------------------------------------------
    # 4. If-Else (DQC)
    # ----------------------------------------------------
    with qc.if_test((c[0], 1)) as else_:
        qc.x(q[0])
    with else_:
        qc.id(q[0]) 

    # ----------------------------------------------------
    # 5. While Loop (SQC)
    # ----------------------------------------------------
    with qc.while_loop((c, 0)):
        qc.h(q[0])
        qc.h(q[1])
        qc.measure(q[0], c[0])
        qc.measure(q[1], c[1])

    # Final measurement
    qc.measure(q[2], c[0])

    # ==========================================
    # Parsing and Simulation
    # ==========================================
    print("\n[Step 1] Parsing Qiskit Circuit...")
    parser = QiskitParser(qc) 

    # === View generated QASM ===
    parser.to_qasm3() # Manually trigger conversion
    print("\n--- Generated OpenQASM 3 ---")
    print(parser.qasm_str)
    print("----------------------------\n")

    structure = parser.parse()
    
    print(f"Parsed {len(structure)} top-level blocks.")
    
    for i, block in enumerate(structure):
        print(f"  Block {i+1}: {type(block).__name__}")
        
        if block.type == 'CQC':
            print(f"    -> Gates: {len(block.ops)} ops")
            for op in block.ops:
                if op.name == 'z': print(f"       - {op} (Unrolled)")
                else: print(f"       - {op}")
            print()

        elif block.type == 'DQC':
            # Update: target_clbits is a list
            print(f"    -> Targets: c{block.target_clbits}")
            print(f"    -> Cases: {list(block.cases.keys())}")
        
        elif block.type == 'SQC':
            # Update: indices is a list
            print(f"    -> Loop Flag: c{block.loop_condition['indices']} == {block.loop_condition['value']}")

    # ==========================================
    # Simulation (Preset Mode)
    # ==========================================
    print("\n[Step 2] Simulating (Sample Mode)...")
    
    sim = BDDSimulator(structure)
    final_clbits = sim.run(mode='sample')
    sim.print_state_vec()
    
    print(f"\nFinal Classical Register: {final_clbits}")
