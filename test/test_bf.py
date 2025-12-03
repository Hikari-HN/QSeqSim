from kernel import BDDCombSim
import time
# 记录开始时间

def simulate_bitflip_qec(n, error_qubit=None):
    """
    使用更新后的 BDDCombSim 模拟位翻转 QEC 电路。
    参数:
    - n: 数据比特数 (逻辑量子比特 + 辅助比特)，需满足 n >= 3
    - error_qubit: 可选，指定注入错误的量子比特编号（如 0 表示数据比特）
    """
    # 初始化量子寄存器：data[0..n-2] + ancilla[n-1]
    sim = BDDCombSim(n, r=3)
    sim.init_basis_state(0)  # 所有量子比特初始化为 |0⟩

    # 编码阶段：将 data[0] 复制到辅助比特 data[1..n-2]
    for i in range(n - 1):
        sim.H(i)
    for i in range(1, n - 1):
        sim.CNOT(0, i)
    # 注入错误（可选）
    if error_qubit is not None:
        sim.X(error_qubit)

    syndrome = []  # 存储测量结果
    for k in range(n - 1):
        sim.CNOT(k, n-1)
        # 测量并记录结果（假设实际结果为 syndrome_value）
        syndrome_value = 1 if k == 0 else 0  # 示例：假设第一个稳定子检测到错误
        sim.mid_measure([n-1], [syndrome_value])
        syndrome.append(syndrome_value)
        # 重置辅助比特为 |0⟩
        sim.reset(n-1)

    # 纠错阶段
    for k in range(n - 1):
        if syndrome[k] == 1:
            sim.X(k)  # 根据稳定子结果翻转对应比特
    for i in range(n - 1):
        sim.H(i)

# 示例调用
try:
    n = int(input("请输入量子比特数 n (n ≥ 3): "))
except ValueError:
    print("请输入一个有效的整数。")
    exit(1)

if n < 3:
    print("量子比特数 n 必须至少为 3。")
    exit(1)
start_time = time.time()
simulate_bitflip_qec(n, error_qubit=0)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time:.6f} seconds")