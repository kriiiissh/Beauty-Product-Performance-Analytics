import os
import json
import sys
import io
import traceback
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless execution
import matplotlib.pyplot as plt

def execute_notebook_file(filepath):
    print(f"\nExecuting notebook: {filepath}...")
    
    with open(filepath, "r", encoding="utf-8") as f:
        nb = json.load(f)
        
    # Set up global execution namespace
    globals_dict = {
        '__builtins__': __builtins__,
        '__name__': '__main__',
    }
    
    # Change working directory to notebooks/ folder temporarily to handle relative data paths in notebook code
    original_cwd = os.getcwd()
    notebook_dir = os.path.dirname(os.path.abspath(filepath))
    os.chdir(notebook_dir)
    
    # Add project root to path for execution context
    sys.path.insert(0, os.path.abspath(".."))
    
    try:
        cell_idx = 0
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                cell_idx += 1
                source = "".join(cell.get("source", []))
                if not source.strip():
                    continue
                    
                print(f"  Running cell {cell_idx}...")
                
                # Capture stdout
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                captured_stdout = io.StringIO()
                captured_stderr = io.StringIO()
                sys.stdout = captured_stdout
                sys.stderr = captured_stderr
                
                outputs = []
                execution_success = True
                
                try:
                    # Execute code cell
                    exec(source, globals_dict)
                except Exception as e:
                    execution_success = False
                    tb_str = traceback.format_exc()
                    print(f"Error in cell:\n{tb_str}", file=captured_stderr)
                    
                finally:
                    # Restore stdout
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    
                # Handle standard streams output
                stdout_text = captured_stdout.getvalue()
                if stdout_text:
                    outputs.append({
                        "output_type": "stream",
                        "name": "stdout",
                        "text": [line + "\n" for line in stdout_text.splitlines() if line]
                    })
                    
                stderr_text = captured_stderr.getvalue()
                if stderr_text:
                    outputs.append({
                        "output_type": "stream",
                        "name": "stderr",
                        "text": [line + "\n" for line in stderr_text.splitlines() if line]
                    })
                    
                # Handle plot outputs (matplotlib/seaborn)
                fig_nums = plt.get_fignums()
                if fig_nums:
                    for fig_num in fig_nums:
                        fig = plt.figure(fig_num)
                        
                        # Save figure to bytes buffer as PNG
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
                        buf.seek(0)
                        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                        buf.close()
                        
                        outputs.append({
                            "output_type": "display_data",
                            "data": {
                                "image/png": img_base64,
                                "text/plain": [f"<Figure size {fig.get_figwidth()*100}x{fig.get_figheight()*100} with {len(fig.axes)} Axes>"]
                            },
                            "metadata": {}
                        })
                    
                    # Clear all plots for next cell
                    plt.close('all')
                    
                # Set outputs and execution count
                cell["outputs"] = outputs
                cell["execution_count"] = cell_idx
                
                if not execution_success:
                    print(f"  Execution stopped due to error in cell {cell_idx}")
                    break
                    
        # Write executed notebook back
        os.chdir(original_cwd)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)
        print(f"Finished executing and saved: {filepath}")
        
    except Exception as e:
        os.chdir(original_cwd)
        print(f"Failed to execute notebook {filepath}: {e}")
        traceback.print_exc()

def execute_all_notebooks():
    notebook_files = [
        "notebooks/01_data_overview.ipynb",
        "notebooks/02_product_analysis.ipynb",
        "notebooks/03_review_analysis.ipynb",
        "notebooks/04_sentiment_nlp.ipynb",
        "notebooks/05_business_insights.ipynb"
    ]
    for nb_file in notebook_files:
        if os.path.exists(nb_file):
            execute_notebook_file(nb_file)
        else:
            print(f"Notebook file not found: {nb_file}")

if __name__ == "__main__":
    execute_all_notebooks()
