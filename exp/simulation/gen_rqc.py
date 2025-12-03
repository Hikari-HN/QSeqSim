import random
import sys
import os

def generate_rqc_script(num_qubits=5, depth=10, max_while_depth=1):
    """
    生成一个包含随机 Qiskit 电路的 Python 脚本字符串。
    """
    
    script_content = []
    
    # 1. 头部导入
    script_content.append("from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, qasm3")
    script_content.append("import math")
    script_content.append("")
    script_content.append(f"# Random Quantum Circuit (RQC)")
    script_content.append(f"# Qubits: {num_qubits}, Depth: {depth}")
    script_content.append("")
    
    # 2. 电路初始化
    script_content.append(f"q = QuantumRegister({num_qubits}, 'q')")
    script_content.append(f"c = ClassicalRegister({num_qubits}, 'c')")
    script_content.append("qc = QuantumCircuit(q, c)")
    script_content.append("")
    
    # --- 随机生成逻辑 ---
    
    indent_level = 0
    
    def add_line(line):
        script_content.append("    " * indent_level + line)
        
    def get_qubit_str(idx):
        return f"q[{idx}]"
        
    def get_clbit_str(idx):
        return f"c[{idx}]"

    def random_gate(qubits):
        gate = random.choice(['h', 'x', 'y', 'z', 's', 't', 'rx', 'ry', 'rz', 'cx', 'cz', 'swap'])
        
        if gate in ['h', 'x', 'y', 'z', 's', 't']:
            target = random.choice(qubits)
            add_line(f"qc.{gate}({get_qubit_str(target)})")
            
        elif gate in ['rx', 'ry', 'rz']:
            target = random.choice(qubits)
            # 限制为 pi/2 以兼容 Cliff+T 模拟器
            add_line(f"qc.{gate}(math.pi/2, {get_qubit_str(target)})")
            
        elif gate in ['cx', 'cz', 'swap']:
            if len(qubits) >= 2:
                q1, q2 = random.sample(qubits, 2)
                add_line(f"qc.{gate}({get_qubit_str(q1)}, {get_qubit_str(q2)})")

    # 递归构建块
    def build_block(qubits, current_depth, current_while_depth):
        nonlocal indent_level
        if current_depth <= 0:
            return

        rand_val = random.random()
        
        # === SQC: While Loop (20%) ===
        if rand_val < 0.2 and current_while_depth < max_while_depth:
            flag_idx = random.randint(0, num_qubits - 1)
            trigger_qubit = flag_idx # index
            
            # 为了保证进入循环，我们可以先假设它满足条件，或者先置位
            # 这里简单生成 while(c[i] == 0)
            
            add_line(f"# === SQC Block (While c[{flag_idx}] == 0) ===")
            add_line(f"with qc.while_loop(({get_clbit_str(flag_idx)}, 0)):")
            
            indent_level += 1
            # 循环体
            body_depth = random.randint(2, 4)
            # 除去 trigger 的其他 qubits
            body_qubits = [qb for qb in qubits if qb != trigger_qubit]
            if not body_qubits: body_qubits = [trigger_qubit]

            for _ in range(body_depth):
                random_gate(body_qubits)
            
            # **必须更新条件**: 测量 trigger qubit
            add_line(f"# SQC Update: Measure trigger q[{trigger_qubit}]")
            add_line(f"qc.h({get_qubit_str(trigger_qubit)})") # 增加随机性
            add_line(f"qc.measure({get_qubit_str(trigger_qubit)}, {get_clbit_str(flag_idx)})")
            
            indent_level -= 1
            add_line("")
            
        # === DQC: If-Else (20%) ===
        elif rand_val < 0.4:
            cond_idx = random.randint(0, num_qubits - 1)
            measure_q = random.randint(0, num_qubits - 1)
            
            add_line(f"# === DQC Block (If c[{cond_idx}] == 1) ===")
            add_line(f"qc.measure({get_qubit_str(measure_q)}, {get_clbit_str(cond_idx)})")
            add_line(f"with qc.if_test(({get_clbit_str(cond_idx)}, 1)) as else_:")
            
            indent_level += 1
            for _ in range(2): random_gate(qubits)
            indent_level -= 1
            
            add_line(f"with else_:")
            indent_level += 1
            for _ in range(2): random_gate(qubits)
            indent_level -= 1
            add_line("")

        # === CQC: Normal Gates (60%) ===
        else:
            block_len = random.randint(1, 3)
            for _ in range(block_len):
                random_gate(qubits)

        # 继续下一层
        build_block(qubits, current_depth - 1, current_while_depth)

    # 初始状态
    for i in range(num_qubits):
        add_line(f"qc.h({get_qubit_str(i)})")
    
    # 开始生成
    build_block(list(range(num_qubits)), depth, 0)
    
    # 结尾
    script_content.append("")
    script_content.append("# Final Measurement")
    script_content.append(f"qc.measure(q, c)")
    script_content.append("")
    script_content.append("# Output QASM")
    script_content.append("print(qasm3.dumps(qc))")
    
    return "\n".join(script_content)

if __name__ == "__main__":
    n = int(input("请输入量子比特数 n: ") or 5)
    d = int(input("请输入电路深度 d: ") or 10)
    
    filename = f"rqc_n{n}_d{d}.py"
    
    print(f"Generating {filename}...")
    content = generate_rqc_script(num_qubits=n, depth=d)
    
    with open(filename, 'w') as f:
        f.write(content)
        
    print(f"Done! You can run it with: python {filename}")
