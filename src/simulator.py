# import random
# import math
# from typing import List, Dict, Optional, Any
# from src.kernel import BDDCombSim
# from src.parser import CQC, DQC, SQC, GateOp

# class BDDSimulator:
#     def __init__(self, parsed_blocks: list, precision: int = 32):
#         self.blocks = parsed_blocks
#         if not self.blocks:
#             self.num_qubits = 0
#             print("[Sim Warning] Empty circuit blocks.")
#         else:
#             self.num_qubits = self.blocks[0].global_num_qubits
        
#         self.kernel = BDDCombSim(self.num_qubits, precision) 
#         if hasattr(self.kernel, 'init_basis_state'):
#             self.kernel.init_basis_state(0)
        
#         self.clbit_store: Dict[int, int] = {}
#         self.mode = 'sample'
#         self.presets = {}
        
#         # 全局概率累积 (用于归一化)
#         self.global_probability = 1.0
        
#         self.GATE_METHOD_MAP = {
#             'x': 'X', 'y': 'Y', 'z': 'Z', 'h': 'H', 's': 'S', 't': 'T',
#             'sdg': 'SDG', 'tdg': 'TDG', 'x2p': 'X2P', 'y2p': 'Y2P', 
#             'cx': 'CNOT', 'cz': 'CZ', 'swap': 'SWAP', 'ccx': 'Toffoli', 'cswap': 'Fredkin'
#         }

#     def run(self, mode: str = 'sample', presets: Optional[Dict[int, List[int]]] = None):
#         self.mode = mode
#         self.presets = presets if presets else {}
#         self.clbit_store.clear()
#         self.global_probability = 1.0 # 重置概率
        
#         print(f"\n[Sim] Starting Simulation (Mode: {self.mode}, Qubits: {self.num_qubits})...")
#         try:
#             self._execute_blocks(self.blocks)
#             print("[Sim] Simulation Finished Successfully.")
#         except Exception as e:
#             print(f"[Sim] Simulation Failed: {e}")
#             raise e
#         return self.clbit_store

#     def print_state_vec(self):
#         """
#         打印归一化后的量子态向量。
#         自动处理中间测量导致的概率坍缩。
#         """
#         print(f"\n--- Final Quantum State Vector (Normalized) ---")
#         print(f"Global Probability Factor: {self.global_probability:.6f}")
        
#         if self.global_probability <= 0:
#             print("State has collapsed to 0 probability (Impossible path).")
#             return

#         norm_factor = math.sqrt(self.global_probability)
        
#         # # 对于 1000 比特，不要尝试遍历所有状态！
#         # if self.num_qubits > 20:
#         #     print(f"Num qubits ({self.num_qubits}) is too large to print full state vector.")
#         #     return

#         for i in range(1 << self.num_qubits):
#             # 获取未归一化的振幅
#             raw_amp = self.kernel.get_amplitude(i)
#             # 归一化
#             norm_amp = raw_amp / norm_factor
            
#             # 只打印非零项 (可选)
#             if abs(norm_amp) > 1e-10:
#                 print(f"|{bin(i)[2:].zfill(self.num_qubits)}>: {norm_amp:.6f}")

#     def _execute_blocks(self, blocks: list):
#         for block in blocks:
#             if isinstance(block, CQC): self._run_cqc(block)
#             elif isinstance(block, DQC): self._run_dqc(block)
#             elif isinstance(block, SQC): self._run_sqc(block)

#     def _run_cqc(self, cqc: CQC):
#         for op in cqc.ops: self._dispatch_op(op)

#     def _run_dqc(self, dqc: DQC):
#         current_val = self._read_clbit_register(dqc.target_clbits)
#         if current_val in dqc.cases:
#             self._execute_blocks(dqc.cases[current_val])
#         else:
#             self._execute_blocks(dqc.default_block)

#     def _run_sqc(self, sqc: SQC):
#         target_indices = sqc.loop_condition['indices']
#         expected_val = sqc.loop_condition['value']
#         iteration = 0
#         MAX_ITER = 1000 
        
#         while True:
#             current_val = self._read_clbit_register(target_indices)
#             if current_val != expected_val: break
#             if iteration >= MAX_ITER: raise RuntimeError("Max iterations reached in SQC.")
            
#             try: self._execute_blocks(sqc.body_block)
#             except StopIteration: break
#             iteration += 1

#     def _dispatch_op(self, op: GateOp):
#         if op.name == 'break': raise StopIteration("break")
#         elif op.name == 'measure': self._handle_measurement(op)
#         else:
#             method_name = self.GATE_METHOD_MAP.get(op.name)
#             if not method_name: raise ValueError(f"Unknown gate '{op.name}'")
#             method = getattr(self.kernel, method_name, None)
#             if method: method(*op.qubits)
#             else:
#                 apply_gate = getattr(self.kernel, 'apply_gate', None)
#                 if apply_gate: apply_gate(method_name, op.qubits)
#                 else: raise AttributeError(f"Kernel object has no method '{method_name}'")

#     def _handle_measurement(self, op: GateOp):
#         for q_idx, c_idx in zip(op.qubits, op.c_targets):
#             # 1. 获取未归一化的联合概率 P(outcome, history)
#             prob_0_joint = 0.0
#             prob_1_joint = 0.0
            
#             # 优化：如果是 preset 模式，且我们不需要计算概率（例如只关心路径），可以跳过 get_prob
#             # 但为了计算 global_probability，通常还是需要。
            
#             if hasattr(self.kernel, 'get_prob'):
#                 # 尝试优化大规模 qubit 的测量
#                 # 如果 qubit 数太大，get_prob 会爆栈/超时。
#                 # 对于 RQ 1000，这里的 get_prob 必须被优化或绕过。
                
#                 # Hack: 暂时捕获 RecursionError 并提示
#                 try:
#                     prob_0_joint = self.kernel.get_prob([q_idx], [0])
#                     prob_1_joint = self.kernel.get_prob([q_idx], [1])
#                 except RecursionError:
#                     print(f"[Sim Warning] Recursion limit reached during measurement of q[{q_idx}]. "
#                           f"Approximating/Skipping probability calculation (Assuming uniform if applicable).")
#                     # 这是一个非常粗暴的假设，但在跑不通的情况下只能这样
#                     prob_0_joint = 0.5 
#                     prob_1_joint = 0.5
#             else: raise AttributeError("Kernel missing 'get_prob' method.")
            
#             # 2. 计算当前归一化系数 (即 P(history))
#             current_norm = prob_0_joint + prob_1_joint
            
#             if current_norm <= 1e-15:
#                 raise ValueError("State collapsed to 0 probability.")
            
#             # 3. 计算真实的条件概率 P(0 | history)
#             real_prob_0 = prob_0_joint / current_norm
            
#             # 4. 决定结果
#             measured_val = 0
#             if self.mode == 'sample':
#                 measured_val = 0 if random.random() < real_prob_0 else 1
#             elif self.mode == 'preset':
#                 if c_idx in self.presets and len(self.presets[c_idx]) > 0:
#                     measured_val = self.presets[c_idx].pop(0)
#                 else: raise ValueError(f"No preset value available for clbit {c_idx}.")
            
#             # 5. 累积全局概率
#             # 我们选择了某个分支，该分支的条件概率是 real_prob
#             branch_prob = real_prob_0 if measured_val == 0 else (1.0 - real_prob_0)
#             self.global_probability *= branch_prob
            
#             # 6. 坍缩状态 (Kernel 内部不归一化)
#             if hasattr(self.kernel, 'mid_measure'):
#                 self.kernel.mid_measure([q_idx], [measured_val])
#             else: raise AttributeError("Kernel missing 'mid_measure' method.")
            
#             self.clbit_store[c_idx] = measured_val

#     def _read_clbit_register(self, indices: List[int]) -> int:
#         val = 0
#         for i, idx in enumerate(indices):
#             bit_val = self.clbit_store.get(idx, 0)
#             val += bit_val * (1 << i)
#         return val


import random
import math
from typing import List, Dict, Optional, Any
from src.kernel import BDDCombSim
from src.parser import CQC, DQC, SQC, GateOp

class BDDSimulator:
    def __init__(self, parsed_blocks: list, precision: int = 32):
        self.blocks = parsed_blocks
        if not self.blocks:
            self.num_qubits = 0
            print("[Sim Warning] Empty circuit blocks.")
        else:
            self.num_qubits = self.blocks[0].global_num_qubits
        
        self.kernel = BDDCombSim(self.num_qubits, precision) 
        if hasattr(self.kernel, 'init_basis_state'):
            self.kernel.init_basis_state(0)
        
        self.clbit_store: Dict[int, int] = {}
        self.mode = 'sample'
        self.presets: Dict[int, List[int]] = {}
        
        # 全局概率累积 (用于归一化)
        self.global_probability = 1.0
        
        self.GATE_METHOD_MAP = {
            'x': 'X', 'y': 'Y', 'z': 'Z', 'h': 'H', 's': 'S', 't': 'T',
            'sdg': 'SDG', 'tdg': 'TDG', 'x2p': 'X2P', 'y2p': 'Y2P', 
            'cx': 'CNOT', 'cz': 'CZ', 'swap': 'SWAP', 'ccx': 'Toffoli', 'cswap': 'Fredkin'
        }

    def run(self, mode: str = 'sample', presets: Optional[Dict[int, List[int]]] = None):
        self.mode = mode
        self.presets = presets if presets else {}
        self.clbit_store.clear()
        self.global_probability = 1.0 # 重置概率
        
        print(f"\n[Sim] Starting Simulation (Mode: {self.mode}, Qubits: {self.num_qubits})...")
        try:
            self._execute_blocks(self.blocks)
            print("[Sim] Simulation Finished Successfully.")
        except Exception as e:
            print(f"[Sim] Simulation Failed: {e}")
            raise e
        return self.clbit_store

    def print_state_vec(self):
        """
        打印归一化后的量子态向量。
        自动处理中间测量导致的概率坍缩。
        """
        print(f"\n--- Final Quantum State Vector (Normalized) ---")
        print(f"Global Probability Factor: {self.global_probability:.6f}")
        
        if self.global_probability <= 0:
            print("State has collapsed to 0 probability (Impossible path).")
            return

        norm_factor = math.sqrt(self.global_probability)
        
        # # 对于 1000 比特，不要尝试遍历所有状态！
        # if self.num_qubits > 20:
        #     print(f"Num qubits ({self.num_qubits}) is too large to print full state vector.")
        #     return

        for i in range(1 << self.num_qubits):
            # 获取未归一化的振幅
            raw_amp = self.kernel.get_amplitude(i)
            # 归一化
            norm_amp = raw_amp / norm_factor
            
            # 只打印非零项 (可选)
            if abs(norm_amp) > 1e-10:
                print(f"|{bin(i)[2:].zfill(self.num_qubits)}>: {norm_amp:.6f}")

    def _execute_blocks(self, blocks: list):
        for block in blocks:
            if isinstance(block, CQC):
                self._run_cqc(block)
            elif isinstance(block, DQC):
                self._run_dqc(block)
            elif isinstance(block, SQC):
                self._run_sqc(block)

    def _run_cqc(self, cqc: CQC):
        for op in cqc.ops:
            self._dispatch_op(op)

    def _run_dqc(self, dqc: DQC):
        current_val = self._read_clbit_register(dqc.target_clbits)
        if current_val in dqc.cases:
            self._execute_blocks(dqc.cases[current_val])
        else:
            self._execute_blocks(dqc.default_block)

    def _run_sqc(self, sqc: SQC):
        target_indices = sqc.loop_condition['indices']
        expected_val = sqc.loop_condition['value']
        iteration = 0
        MAX_ITER = 1000 
        
        while True:
            current_val = self._read_clbit_register(target_indices)
            if current_val != expected_val:
                break
            if iteration >= MAX_ITER:
                raise RuntimeError("Max iterations reached in SQC.")
            
            try:
                self._execute_blocks(sqc.body_block)
            except StopIteration:
                break
            iteration += 1

    def _dispatch_op(self, op: GateOp):
        if op.name == 'break':
            raise StopIteration("break")
        elif op.name == 'measure':
            self._handle_measurement(op)
        else:
            method_name = self.GATE_METHOD_MAP.get(op.name)
            if not method_name:
                raise ValueError(f"Unknown gate '{op.name}'")
            method = getattr(self.kernel, method_name, None)
            if method:
                method(*op.qubits)
            else:
                apply_gate = getattr(self.kernel, 'apply_gate', None)
                if apply_gate:
                    apply_gate(method_name, op.qubits)
                else:
                    raise AttributeError(f"Kernel object has no method '{method_name}'")

    def _handle_measurement(self, op: GateOp):
        """
        统一处理测量：
        - 如果是 mid-measure（op.is_final_measure == False）：
          * 需要坍缩量子态 + 更新 global_probability。
        - 如果是 final-measure（op.is_final_measure == True）：
          * 只产生 classical 结果，不坍缩、不影响 global_probability，
            也不要求 preset 必须提供。
        """
        for q_idx, c_idx in zip(op.qubits, op.c_targets):
            # 1) Final measurement：只决定 classical 结果，不坍缩量子态
            if getattr(op, "is_final_measure", False):
                measured_val = self._decide_final_measure_value(q_idx, c_idx)
                self.clbit_store[c_idx] = measured_val
                continue

            # 2) Mid-measure：执行原有流程
            prob_0_joint = 0.0
            prob_1_joint = 0.0
            
            if hasattr(self.kernel, 'get_prob'):
                try:
                    prob_0_joint = self.kernel.get_prob([q_idx], [0])
                    prob_1_joint = self.kernel.get_prob([q_idx], [1])
                except RecursionError:
                    print(f"[Sim Warning] Recursion limit reached during measurement of q[{q_idx}]. "
                          f"Approximating/Skipping probability calculation (Assuming uniform if applicable).")
                    prob_0_joint = 0.5 
                    prob_1_joint = 0.5
            else:
                raise AttributeError("Kernel missing 'get_prob' method.")
            
            current_norm = prob_0_joint + prob_1_joint
            if current_norm <= 1e-15:
                raise ValueError("State collapsed to 0 probability.")
            
            real_prob_0 = prob_0_joint / current_norm
            
            # 决定结果
            if self.mode == 'sample':
                measured_val = 0 if random.random() < real_prob_0 else 1
            elif self.mode == 'preset':
                if c_idx in self.presets and len(self.presets[c_idx]) > 0:
                    measured_val = self.presets[c_idx].pop(0)
                else:
                    raise ValueError(f"No preset value available for clbit {c_idx}.")
            else:
                measured_val = 0
            
            # 累积全局概率 (mid-measure 才需要)
            branch_prob = real_prob_0 if measured_val == 0 else (1.0 - real_prob_0)
            self.global_probability *= branch_prob
            
            # 坍缩状态
            if hasattr(self.kernel, 'mid_measure'):
                self.kernel.mid_measure([q_idx], [measured_val])
            else:
                raise AttributeError("Kernel missing 'mid_measure' method.")
            
            self.clbit_store[c_idx] = measured_val

    def _decide_final_measure_value(self, q_idx: int, c_idx: int) -> int:
        """
        决定 final measurement 的 classical 结果。
        - 不坍缩量子态
        - 不更新 global_probability
        - sample 模式：按当前态的真实分布采样一次（如 get_prob 可用）
        - preset 模式：若有 preset 就用；若没有就按真实分布采样（不报错）
        """
        # 1) preset 模式下，如有 preset，优先使用
        if self.mode == 'preset' and c_idx in self.presets and self.presets[c_idx]:
            return self.presets[c_idx].pop(0)

        # 2) 其余情况（sample / preset 无 preset）：根据真实分布采样一次，但不坍缩
        real_p0 = 0.5
        if hasattr(self.kernel, 'get_prob'):
            try:
                p0 = self.kernel.get_prob([q_idx], [0])
                p1 = self.kernel.get_prob([q_idx], [1])
                norm = p0 + p1
                if norm > 1e-15:
                    real_p0 = p0 / norm
            except RecursionError:
                print(f"[Sim Warning] Recursion limit reached during final measurement of q[{q_idx}]. "
                      f"Assuming uniform distribution for readout.")
                real_p0 = 0.5
        else:
            real_p0 = 0.5
        
        return 0 if random.random() < real_p0 else 1

    def _read_clbit_register(self, indices: List[int]) -> int:
        val = 0
        for i, idx in enumerate(indices):
            bit_val = self.clbit_store.get(idx, 0)
            val += bit_val * (1 << i)
        return val