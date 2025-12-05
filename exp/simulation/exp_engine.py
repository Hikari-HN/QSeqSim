"""
实验引擎 (exp_engine.py)
统计 Compiling Time (解析) 与 Computation Time (核心计算)
"""

import importlib.util
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List

# 确保src目录可导入
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.parser import QiskitParser
from src.simulator import BDDSimulator


class ExperimentRunner:
    def __init__(self, exp_rel_path: str):
        self.exp_rel_path = exp_rel_path
        self.exp_abs_path = self._get_exp_abs_path()
        self._validate_exp_file()

        # 时间指标 (初始化为0.0)
        self.compile_time: float = 0.0  # 编译时间 (Parser -> IR)
        self.compute_time: float = 0.0  # 计算时间 (BDD Simulation)

        # 从实验文件导入电路和配置参数
        self.circ, self.sim_mode, self.preset_values = self._import_experiment_data()

    def _get_exp_abs_path(self) -> Path:
        return Path(__file__).parent.resolve() / f"{self.exp_rel_path}.py"

    def _validate_exp_file(self) -> None:
        if not self.exp_abs_path.exists():
            raise FileNotFoundError(f"实验文件不存在: {self.exp_abs_path}")
        if not self.exp_abs_path.is_file():
            raise IsADirectoryError(f"指定路径不是文件: {self.exp_abs_path}")

    def _import_experiment_data(self):
        """从实验文件导入电路、模拟模式和预设值"""
        module_name = f"exp_{self.exp_rel_path.replace('/', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, self.exp_abs_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 验证必须的变量
        if not hasattr(module, "circ"):
            raise AttributeError(f"实验文件需定义 'circ' 变量（量子电路）")
        if not hasattr(module, "sim_mode"):
            raise AttributeError(f"实验文件需定义 'sim_mode' 变量（模拟模式）")

        # 获取模拟模式（转为小写统一处理）
        sim_mode = module.sim_mode.lower()
        valid_modes = ['preset', 'sample']
        if sim_mode not in valid_modes:
            raise ValueError(f"sim_mode 必须为 {valid_modes} 中的一种，当前值: {sim_mode}")

        # 获取预设值（仅preset模式需要）
        preset_values = None
        if sim_mode == 'preset':
            if not hasattr(module, "preset_values"):
                raise AttributeError(f"preset模式下，实验文件需定义 'preset_values' 变量")
            preset_values = module.preset_values
            if not isinstance(preset_values, dict):
                raise TypeError(f"preset_values 必须是字典类型，当前类型: {type(preset_values)}")

        return module.circ, sim_mode, preset_values

    def run(self) -> None:
        print(f"📂 实验文件: {self.exp_abs_path.name}")
        print(f"▶️ 模拟模式: {self.sim_mode}")
        if self.sim_mode == 'preset':
            print(f"▶️ 预设值: {self.preset_values}")
        print("▶️ 准备就绪，开始执行...")

        try:
            # 1. 初始化解析器
            parser = QiskitParser(self.circ)

            # ========== Phase 1: Compiling (Parsing) ==========
            # 统计从 QASM/Circuit 解析为中间表示 (IR) 的时间
            t_start_compile = time.perf_counter()
            
            structure = parser.parse()
            
            self.compile_time = time.perf_counter() - t_start_compile
            # ==================================================

            # 初始化模拟器 (BDD结构建立)
            sim = BDDSimulator(structure)

            # ========== Phase 2: Computation (Simulation) ==========
            # 统计核心 BDD 运算与路径模拟的时间
            t_start_compute = time.perf_counter()

            if self.sim_mode == 'preset':
                sim.run(mode='preset', presets=self.preset_values)
            else:  # sample模式
                sim.run(mode='sample')

            self.compute_time = time.perf_counter() - t_start_compute
            # =======================================================

            print("✅ 执行完成!")
            
            sim.print_state_vec()

            # 打印时间统计
            self._print_stats()

        except Exception as e:
            print(f"❌ 执行失败: {str(e)}")
            # 即使失败也打印已完成阶段的时间
            self._print_stats()
            raise e

    def _print_stats(self) -> None:
        total_runtime = self.compile_time + self.compute_time
        
        print("\n===== 性能时间统计 =====")
        print(f"1. Compiling Time (Parse) : {self.compile_time:.9f} s")
        print(f"2. Computation Time (Exec): {self.compute_time:.9f} s")
        print(f"---------------------------")
        print(f"⏱️ Total Runtime           : {total_runtime:.9f} s")
        print("===========================")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python exp_engine.py <电路相对路径>")
        print("示例: python exp_engine.py rus/rus_1")
        sys.exit(1)

    try:
        runner = ExperimentRunner(sys.argv[1])
        runner.run()
    except Exception as e:
        # 错误已在 run 方法中处理或抛出，此处仅确保非正常退出码
        sys.exit(1)