from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, qasm3

# 对应 seq_rus.py 的逻辑
# BDDSeqSim(2, 1, 3) -> n=2 (总比特), m=1 (输入/存储比特), r=3 (precision)
# 输入比特 m=1 (q0), 辅助比特 (q1)
# 初始状态 q0=|0>

q = QuantumRegister(2, 'q')
c = ClassicalRegister(1, 'c') 
rus = QuantumCircuit(q, c)

# 对应 result_list = [0] * (it - 1) + [1]
# 这个列表代表的是每次测量的预期结果或者预设值。
# 在 Qiskit 中，RUS (Repeat-Until-Success) 通常用 while_loop 实现。
# seq_rus.py 是展开式的写法（手动循环），这里我将其转换为标准的 Qiskit 动态电路。

# 初始状态: q0 = |0> (默认)

def rus_trial(circuit, q_sys, q_anc, c_anc):
    # Sim.H(0) -> q_sys
    circuit.h(q_sys)
    # Sim.T(0)
    circuit.t(q_sys)
    # Sim.H(0)
    circuit.h(q_sys)
    # Sim.CZ(0, 1) -> CZ(q_sys, q_anc)
    circuit.cz(q_sys, q_anc)
    # Sim.Z(0)
    circuit.z(q_sys)
    # Sim.S(0)
    circuit.s(q_sys)
    # Sim.T(0)
    circuit.t(q_sys)
    # Sim.H(0)
    circuit.h(q_sys)
    # Sim.T(0)
    circuit.t(q_sys)
    # Sim.CZ(0, 1)
    circuit.cz(q_sys, q_anc)
    # Sim.H(0)
    circuit.h(q_sys)
    # Sim.T(0)
    circuit.t(q_sys)
    # Sim.H(0)
    circuit.h(q_sys)
    # Sim.Z(1) -> q_anc
    circuit.z(q_anc)
    
    # Sim.measure([result]) -> 测量 q_anc?
    # 在 seq_rus.py 中: Sim.measure2([result])
    # n=2, m=1 => n-m=1 个比特被测量。通常是把辅助比特测掉。
    # 这里假设测量的是 q1 (q_anc)
    circuit.measure(q_sys, c_anc)

# 第一次尝试
rus_trial(rus, q[0], q[1], c[0])

# 循环直到成功 (result == 1 表示成功)
# 注意：seq_rus.py 中的 result_list 最后一个是 1，前面都是 0。
# 这意味着只要测得 0 就继续，测得 1 就停止。
with rus.while_loop((c, 0)):
    # 如果失败 (测得0)，需要重置辅助比特或者进行修正操作吗？
    # seq_rus.py 只是简单地 init_input_state_by_basis(input_basis)
    # input_basis 都是 0。说明每次循环开始前，辅助比特都是 |0>。
    # 如果刚才测得 0，q1 已经是 |0>，无需重置。
    # 如果测得 1，就退出循环了。
    
    # 重新执行 trial
    rus_trial(rus, q[0], q[1], c[0])

# 打印 QASM 用于验证
print(qasm3.dumps(rus))

