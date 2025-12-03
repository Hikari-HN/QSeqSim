from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# 5 个量子比特 + 2 个经典比特 (out1, out2)
q = QuantumRegister(5, 'q')
c = ClassicalRegister(2, 'c')  # c[0] <-> out1, c[1] <-> out2
qec = QuantumCircuit(q, c)

# === 对应 init_basis_state(16) ===
qec.x(q[0])

# === 量子门序列 ===
qec.cx(q[0], q[1])
qec.cx(q[1], q[2])
qec.x(q[0])
qec.cx(q[0], q[3])
qec.cx(q[1], q[3])
qec.cx(q[0], q[4])
qec.cx(q[2], q[4])

# === 测量并写入 out1、out2 ===
qec.measure(q[3], c[0])  # out1
qec.measure(q[4], c[1])  # out2

# === 基于测量结果的条件操作 ===
with qec.if_test((c[0], 1)):  # out1 == 1
    qec.x(q[3])

with qec.if_test((c[1], 1)):  # out2 == 1
    qec.x(q[4])

with qec.if_test((c, 3)):     # out1=1, out2=1 -> 0b11 = 3
    qec.x(q[0])

with qec.if_test((c, 1)):     # out1=1, out2=0 -> 0b01 = 1
    qec.x(q[1])

with qec.if_test((c, 2)):     # out1=0, out2=1 -> 0b10 = 2
    qec.x(q[2])
