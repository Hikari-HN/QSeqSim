import argparse
import time
import sys
import os
import signal

# Add root directory to Python path (consistent with original script)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.kernel import BDDSeqSim

# Define experiment configurations: (number of qubits n, number of iterations it)
EXPERIMENT_CONFIGS = [
    (16, 1000),
    (128, 1000),
    (256, 1000)
]
TIMEOUT_SECONDS = 1800  # Timeout threshold: 30 minutes

# Create data directory if not exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(LOG_DIR, exist_ok=True)

class TimeoutException(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Signal handler: trigger timeout exception"""
    raise TimeoutException("Runtime exceeds 1800 seconds, terminating current experiment")

# Register signal handler (applicable to Linux/macOS)
signal.signal(signal.SIGALRM, timeout_handler)

def init_log(n):
    """
    Initialize log file: clear/overwrite existing file before experiment
    :param n: Number of qubits (for log file naming)
    """
    log_file = os.path.join(LOG_DIR, f"grover_{n}.log")
    # Open file in 'w' mode to clear existing content (create if not exists)
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] Grover experiment log (n={n}) initialized\n")

def write_log(n, content):
    """
    Write content to specific log file (grover_{n}.log) with timestamp
    :param n: Number of qubits (for log file naming)
    :param content: Content to write
    """
    log_file = os.path.join(LOG_DIR, f"grover_{n}.log")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {content}\n")

def _parse_report_iters(report_iters_str):
    """
    Parse comma-separated iteration list.
    Example: "3,10,100" -> {3,10,100}
    """
    if not report_iters_str:
        return set()
    items = []
    for part in report_iters_str.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            items.append(int(part))
        except ValueError:
            pass
    return set(items)

def run_grover_experiment(n, it, report_iters=None, timeout_seconds=TIMEOUT_SECONDS):
    """
    Execute a single group of Grover experiments
    :param n: Number of qubits
    :param it: Number of iterations
    :return: Experiment result (success/timeout/error), total runtime
    """
    # Initialize log file (overwrite existing content)
    init_log(n)
    
    # Console: only print key experiment start info
    experiment_start_msg = f"\n========== Starting experiment: n={n}, it={it} =========="
    print(experiment_start_msg)
    write_log(n, experiment_start_msg.strip())
    
    start_total_time = time.time()  # Global start time of the experiment
    result = "success"
    
    if report_iters is None:
        report_iters = set()
    
    try:
        # Set timeout alarm
        signal.alarm(timeout_seconds)
        
        # Initialize simulator
        Sim = BDDSeqSim(n, n - 1, 3)
        result_list = [0] * (it - 1) + [1]
        input_basis_list = [0] * len(result_list)
        cnt = 0
        Sim.init_stored_state_by_basis(0)

        # Execute iteration by iteration (only write to log, no console print)
        for result_val, input_basis in zip(result_list, input_basis_list):
            cnt += 1
            
            # Core calculation logic (consistent with original script)
            Sim.init_input_state_by_basis(input_basis)
            Sim.init_comb_bdd()

            for i in range(n-1):
                Sim.H(i)
            Sim.H(n-1)
            Sim.multi_controlled_X(list(range(n-1)), n-1)
            Sim.H(n-1)

            for i in range(n-1):
                Sim.H(i)
                Sim.X(i)
            Sim.H(n-2)
            Sim.multi_controlled_X(list(range(n-2)), n-2)
            Sim.H(n-2)

            for i in range(n-1):
                Sim.H(i)
                Sim.X(i)

            Sim.measure([result_val])
            
            # Calculate cumulative time (from experiment start to end of current iteration)
            cumulative_time = time.time() - start_total_time
            # ONLY write to specific log file, no console print
            iter_msg = f"Iteration {cnt} - Probability: {Sim.prob_list[-1]}, Cumulative time: {cumulative_time:.4f} seconds"
            write_log(n, iter_msg)

            # [AE Helper] Print machine-readable report lines for specific iterations
            if cnt in report_iters:
                print(f"[REPORT] n={n} iter={cnt} time={cumulative_time:.6f}")
        
        # Turn off timeout alarm
        signal.alarm(0)
        
    except TimeoutException as e:
        # Catch timeout exception (console + log)
        result = "timeout"
        error_msg = f"\n❌ {e}"
        print(error_msg)
        write_log(n, error_msg.strip())
    except Exception as e:
        # Catch other exceptions (console + log)
        result = "error"
        error_msg = f"\n❌ Experiment error: {str(e)}"
        print(error_msg)
        write_log(n, error_msg.strip())
    finally:
        # Calculate total runtime
        total_time = time.time() - start_total_time
        # Console: print experiment end and status
        experiment_end_msg = f"\n========== Experiment finished: n={n}, it={it} =========="
        status_msg = f"Experiment status: {result}, Total runtime: {total_time:.4f} seconds"
        print(experiment_end_msg)
        print(status_msg)
        # Write to specific log file
        write_log(n, experiment_end_msg.strip())
        write_log(n, status_msg)
        return result, total_time

def main():
    """Main function: execute all experiment configurations in order"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=None, help="Number of qubits (override EXPERIMENT_CONFIGS)")
    parser.add_argument("--max-iters", type=int, default=None, help="Max iterations to run (override default it=1000)")
    parser.add_argument("--report-iters", type=str, default="", help="Comma-separated iterations to report, e.g., 3,10,100")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS, help="Timeout seconds (default 1800)")
    args = parser.parse_args()

    report_iters = _parse_report_iters(args.report_iters)

    # Record all experiment results
    experiment_results = []
    
    # Determine which configurations to run
    configs = EXPERIMENT_CONFIGS
    if args.n is not None:
        # If --n is specified, run only one configuration
        it = args.max_iters if args.max_iters is not None else 1000
        configs = [(args.n, it)]
    else:
        # If no --n, optionally override it for all EXPERIMENT_CONFIGS if --max-iters is given
        if args.max_iters is not None:
            configs = [(n, args.max_iters) for n, _ in EXPERIMENT_CONFIGS]
    
    for n, it in configs:
        # Write experiment start marker to specific log
        write_log(n, "="*50)
        write_log(n, f"Grover experiment (n={n}, it={it}) started")
        write_log(n, "="*50)
        
        # Execute current experiment
        result, total_time = run_grover_experiment(n, it, report_iters=report_iters, timeout_seconds=args.timeout)
        experiment_results.append({
            "n": n,
            "it": it,
            "status": result,
            "total_time": total_time
        })
        
        # Write experiment end marker to specific log
        write_log(n, "="*50)
        write_log(n, f"Grover experiment (n={n}, it={it}) finished")
        write_log(n, "="*50)
        
        # Console: print next experiment prompt
        next_exp_msg = f"\n----------------------------------------"
        prepare_msg = f"Preparing to execute next experiment configuration..."
        separator_msg = f"----------------------------------------"
        print(next_exp_msg)
        print(prepare_msg)
        print(separator_msg)
    
    # Console: print final summary
    summary_title = "\n========== All experiments completed, summary results =========="
    print(summary_title)
    for res in experiment_results:
        summary_msg = f"n={res['n']}, it={res['it']} - Status: {res['status']}, Total runtime: {res['total_time']:.4f} seconds"
        print(summary_msg)

if __name__ == "__main__":
    main()