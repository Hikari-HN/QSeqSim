import random
import sys
import os

def generate_benchmark_script(filename, num_qubits, target_gates, target_mid_meas):
    """
    生成符合 QSeqSim 论文实验要求的 Benchmark 脚本。
    包含：While Loop, Nested If-Else, Sample Mode 配置。
    
    【关键改进】：
    1. 保证 Trigger Qubit 的测量是循环体最后一步。
    2. 保证 Trigger Qubit 在测量前被重置到叠加态，确保循环高概率终止。
    3. 循环体内的随机门禁止操作 Trigger Qubit，防止逻辑干扰。
    """
    
    # --- 统计计数器 ---
    stats = {
        "qubits": num_qubits,
        "static_gates": 0,
        "mid_measurements": 0
    }
    
    content = []
    def emit(line, indent=0):
        content.append("    " * indent + line)

    # 1. 头部导入
    emit("from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister")
    emit("import math")
    emit("")
    
    # 2. 寄存器定义
    # 经典比特数 = 目标测量数 (如果为0，至少留1个给循环控制)
    # c[0] 固定作为 while loop 的控制位
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

    # --- 辅助函数：生成随机门 ---
    def add_random_gates(indent_level, count, forbidden_qubits=None):
        """
        生成随机门。
        forbidden_qubits: 列表，禁止在这些 qubit 上生成门。
        """
        if forbidden_qubits is None:
            forbidden_qubits = []
            
        available_qubits = [i for i in range(num_qubits) if i not in forbidden_qubits]
        
        # 如果没有可用比特（极端情况），直接返回
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

    # 3. 电路构建逻辑
    
    # 3.1 初始化部分
    init_gates = int(target_gates * 0.1)
    emit("# --- Initialization ---")
    add_random_gates(0, init_gates)
    emit("")

    # 3.2 While Loop 结构 (核心部分)
    # 设定 c[0] 为循环标志位。
    # 设定 q[0] 为循环触发比特 (Trigger Qubit)。
    loop_clbit_idx = 0
    trigger_qubit_idx = 0 
    
    # 为了保证循环能开始，我们假设 c[0] 初始为 0。
    # (在 Qiskit 中，经典寄存器默认初始化为 0)
    
    emit(f"# --- SQC Block: While Loop (Controlled by c[{loop_clbit_idx}]) ---")
    emit(f"with circ.while_loop((c[{loop_clbit_idx}], 0)):") 
    
    current_indent = 1
    emit(f"# Loop Body", current_indent)
    
    # 计算循环体内的预算
    available_mid_meas_for_body = max(0, target_mid_meas - 1)
    remaining_gates = target_gates - init_gates
    
    # 预留 2 个门给 Trigger 的 Reset/H 操作，保证终止性
    remaining_gates -= 2
    
    # 【关键】：在循环体生成随机门时，绝对禁止操作 trigger_qubit_idx (q[0])
    # 这样可以防止随机逻辑干扰循环退出条件。
    forbidden_in_loop = [trigger_qubit_idx]
    
    if available_mid_meas_for_body <= 0:
        # 没有额外的测量预算，只生成门
        add_random_gates(current_indent, remaining_gates, forbidden_qubits=forbidden_in_loop)
    else:
        # 有测量预算，生成嵌套结构
        gates_per_segment = max(1, remaining_gates // (available_mid_meas_for_body + 1))
        
        meas_idx_pool = list(range(1, num_clbits))
        if not meas_idx_pool: meas_idx_pool = [0] 
        
        for i in range(available_mid_meas_for_body):
            # 1. 加一些门
            add_random_gates(current_indent, gates_per_segment, forbidden_qubits=forbidden_in_loop)
            remaining_gates -= gates_per_segment
            
            # 2. 加一个 DQC (If-Else)
            # 同样避开 trigger qubit
            candidates = [x for x in range(num_qubits) if x not in forbidden_in_loop]
            if not candidates: candidates = [trigger_qubit_idx] # Fallback
            
            target_q = random.choice(candidates)
            target_c = meas_idx_pool[i % len(meas_idx_pool)]
            
            emit(f"# DQC: Mid-circuit measurement", current_indent)
            emit(f"circ.measure(q[{target_q}], c[{target_c}])", current_indent)
            stats["mid_measurements"] += 1
            
            emit(f"with circ.if_test((c[{target_c}], 1)):", current_indent)
            # if 分支内也只加少量门，且不碰 trigger
            add_random_gates(current_indent + 1, 2, forbidden_qubits=forbidden_in_loop)
            remaining_gates -= 2
            
        # 填补剩余的门
        if remaining_gates > 0:
            add_random_gates(current_indent, remaining_gates, forbidden_qubits=forbidden_in_loop)

    # 3.3 循环守卫更新 (必须是 Block 的最后一步)
    # 【关键逻辑】：为了保证终止，我们强制将 Trigger Qubit 重置并施加 H 门。
    # 这样每次测量得到 1 (退出循环) 的概率固定为 50%。
    # 几何分布期望值为 2 次迭代，几乎不可能无限循环。
    
    emit(f"# Update Loop Condition (Must be FINAL op for q[{trigger_qubit_idx}])", current_indent)
    emit(f"# Ensure termination: Reset q[{trigger_qubit_idx}] to |0> then apply H", current_indent)
    emit(f"circ.reset(q[{trigger_qubit_idx}])", current_indent) 
    emit(f"circ.h(q[{trigger_qubit_idx}])", current_indent)
    emit(f"circ.measure(q[{trigger_qubit_idx}], c[{loop_clbit_idx}])", current_indent)
    
    stats["mid_measurements"] += 1
    stats["static_gates"] += 2 # Reset + H
    
    emit("")
    
    # 4. 模拟器配置
    emit("# Simulator Configuration by User")
    emit("sim_mode = 'sample'")
    emit("# No preset values needed for sample mode")
    
    # --- 写入文件 ---
    with open(filename, 'w') as f:
        f.write("\n".join(content))
        
    return stats

if __name__ == "__main__":
    # 默认值或用户输入
    try:
        if len(sys.argv) > 1:
            # 支持命令行参数: python gen_rqc.py 100 500 10
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

    # --- 路径和文件名处理 ---
    # 获取当前脚本所在的目录 (exp/simulation)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 目标目录设为当前脚本目录下的 rqc
    output_dir = os.path.join(current_script_dir, "rqc")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 文件名格式: rqc_q{n}_g{g}_m{m}.py
    short_filename = f"rqc_q{n}_g{g}_m{m}.py"
    full_path = os.path.join(output_dir, short_filename)
    
    final_stats = generate_benchmark_script(full_path, n, g, m)
    
    # 打印表格行格式
    print("\n" + "="*65)
    print(f"{'Benchmark File':<25} | {'Qubits':<8} | {'Gates':<8} | {'Mid-Meas':<8}")
    print("-" * 65)
    print(f"{short_filename:<25} | {final_stats['qubits']:<8} | {final_stats['static_gates']:<8} | {final_stats['mid_measurements']:<8}")
    print("="*65 + "\n")
    print(f"Saved to: {full_path}")