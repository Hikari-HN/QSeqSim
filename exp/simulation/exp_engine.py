"""
Experiment Engine (exp_engine.py)
Collects statistics for Compiling Time (Parsing) and Computation Time (Core Calculation)
"""

import importlib.util
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List
import os
import random
_seed = os.environ.get("QSEQSIM_RNG_SEED")
if _seed is not None:
    random.seed(int(_seed))

# Ensure src directory is importable
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

        # Time metrics (initialized to 0.0)
        self.compile_time: float = 0.0  # Compiling time (Parser -> IR)
        self.compute_time: float = 0.0  # Computation time (BDD Simulation)

        # Import circuit and configuration parameters from experiment file
        self.circ, self.sim_mode, self.preset_values = self._import_experiment_data()

    def _get_exp_abs_path(self) -> Path:
        return Path(__file__).parent.resolve() / f"{self.exp_rel_path}.py"

    def _validate_exp_file(self) -> None:
        if not self.exp_abs_path.exists():
            raise FileNotFoundError(f"Experiment file does not exist: {self.exp_abs_path}")
        if not self.exp_abs_path.is_file():
            raise IsADirectoryError(f"Specified path is not a file: {self.exp_abs_path}")

    def _import_experiment_data(self):
        """Import circuit, simulation mode, and preset values from experiment file"""
        module_name = f"exp_{self.exp_rel_path.replace('/', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, self.exp_abs_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Validate required variables
        if not hasattr(module, "circ"):
            raise AttributeError(f"Experiment file must define 'circ' variable (QuantumCircuit)")
        if not hasattr(module, "sim_mode"):
            raise AttributeError(f"Experiment file must define 'sim_mode' variable (Simulation Mode)")

        # Get simulation mode (convert to lowercase for unified handling)
        sim_mode = module.sim_mode.lower()
        valid_modes = ['preset', 'sample']
        if sim_mode not in valid_modes:
            raise ValueError(f"sim_mode must be one of {valid_modes}, current value: {sim_mode}")

        # Get preset values (only needed for preset mode)
        preset_values = None
        if sim_mode == 'preset':
            if not hasattr(module, "preset_values"):
                raise AttributeError(f"Experiment file must define 'preset_values' variable in preset mode")
            preset_values = module.preset_values
            if not isinstance(preset_values, dict):
                raise TypeError(f"preset_values must be a dictionary, current type: {type(preset_values)}")

        return module.circ, sim_mode, preset_values

    def run(self) -> None:
        print(f"📂 Experiment File: {self.exp_abs_path.name}")
        print(f"▶️ Simulation Mode: {self.sim_mode}")
        if self.sim_mode == 'preset':
            print(f"▶️ Preset Values: {self.preset_values}")
        print("▶️ Ready, starting execution...")

        try:
            # 1. Initialize Parser
            parser = QiskitParser(self.circ)

            # ========== Phase 1: Compiling (Parsing) ==========
            # Statistics for time from QASM/Circuit parsing to Intermediate Representation (IR)
            t_start_compile = time.perf_counter()
            
            structure = parser.parse()
            
            self.compile_time = time.perf_counter() - t_start_compile
            # ==================================================

            # Initialize Simulator (Build BDD Structure)
            sim = BDDSimulator(structure)

            # ========== Phase 2: Computation (Simulation) ==========
            # Statistics for Core BDD Operation and Path Simulation Time
            t_start_compute = time.perf_counter()

            if self.sim_mode == 'preset':
                sim.run(mode='preset', presets=self.preset_values)
            else:  # sample mode
                sim.run(mode='sample')

            self.compute_time = time.perf_counter() - t_start_compute
            # =======================================================

            print("✅ Execution Completed!")
            
            sim.print_state_vec()

            # Print time statistics
            self._print_stats()

        except Exception as e:
            print(f"❌ Execution Failed: {str(e)}")
            # Print time for completed phases even if failed
            self._print_stats()
            raise e

    def _print_stats(self) -> None:
        total_runtime = self.compile_time + self.compute_time
        
        print("\n===== Performance Time Statistics =====")
        print(f"1. Compiling Time (Parse) : {self.compile_time:.9f} s")
        print(f"2. Computation Time (Exec): {self.compute_time:.9f} s")
        print(f"---------------------------")
        print(f"⏱️ Total Runtime           : {total_runtime:.9f} s")
        print("===========================")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exp_engine.py <circuit_relative_path>")
        print("Example: python exp_engine.py rus/rus_1")
        sys.exit(1)

    try:
        runner = ExperimentRunner(sys.argv[1])
        runner.run()
    except Exception as e:
        # Errors handled or raised in run method, here only ensure non-normal exit code
        sys.exit(1)
