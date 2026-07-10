# Chapter 5 Visual Labs: Adversarial Search and Games

This folder contains five standalone Jupyter notebooks for university-level instruction. Each notebook includes chapter notes, complete Python code, visual search demonstrations, and student practice cells.

## Lab Files

1. `Lab_05A_Minimax_TicTacToe_Game_Trees.ipynb`
2. `Lab_05B_Alpha_Beta_Pruning_Move_Ordering.ipynb`
3. `Lab_05C_Heuristic_Alpha_Beta_Connect4.ipynb`
4. `Lab_05D_MCTS_Stochastic_Games.ipynb`
5. `Lab_05E_Partially_Observable_Games_Limitations.ipynb`

## Software Requirements

Students need:

- Python 3
- Jupyter Notebook
- `matplotlib`
- `ipywidgets` for interactive sliders and buttons
- `ipykernel` so the virtual environment can be used as a Jupyter kernel

The notebooks will still display static first and last frames when `ipywidgets` is unavailable.

## 1. Open a Terminal in the Lab Folder

Navigate to the folder containing the notebooks.

Example:

```bash
cd "/path/to/chapter5_visual_labs"
```

Because the folder name may contain spaces, place the path inside quotation marks.

Confirm that the notebook files are present:

```bash
ls
```

## 2. Create a Python Virtual Environment

A virtual environment keeps the packages for this lab separate from the system-wide Python installation.

Create an environment named `.venv`.

### Linux or macOS

```bash
python3 -m venv .venv
```

### Windows

```powershell
py -m venv .venv
```

This command only needs to be run once.

After it is created, the project folder should contain a hidden directory named `.venv`.

On Linux or macOS, display hidden files with:

```bash
ls -la
```

## 3. Activate the Virtual Environment

The environment normally must be activated each time a new terminal is opened.

### Linux or macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

After activation, the terminal prompt should begin with something similar to:

```text
(.venv)
```

Example:

```text
(.venv) student@computer:~/chapter5_visual_labs$
```

The `(.venv)` text indicates that the virtual environment is active.

## 4. Verify the Active Python Environment

Check which Python interpreter is being used.

### Linux or macOS

```bash
which python
```

### Windows

```powershell
where python
```

The path should point to the `.venv` directory.

You can also verify the Python version:

```bash
python --version
```

## 5. Install the Required Packages

With the virtual environment activated, upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
python -m pip install notebook matplotlib ipywidgets ipykernel
```

Using `python -m pip` is recommended because it ensures packages are installed into the currently selected Python environment.

Verify that `ipykernel` is installed:

```bash
python -m pip show ipykernel
```

## 6. Register the Environment as a Jupyter Kernel

Jupyter and Visual Studio Code may not automatically detect the virtual environment. Register it manually:

```bash
python -m ipykernel install --user --name chapter5-visual-labs --display-name "Python (.venv - Chapter 5 Visual Labs)"
```

A successful installation should display a message similar to:

```text
Installed kernelspec chapter5-visual-labs
```

This command only needs to be run once for the environment.

List the available Jupyter kernels:

```bash
python -m jupyter kernelspec list
```

The output should include:

```text
chapter5-visual-labs
```

## 7. Open the Notebooks

### Using Jupyter Notebook

With the environment activated, run:

```bash
jupyter notebook
```

A browser window should open. Select one of the Chapter 5 notebook files.

To stop Jupyter Notebook, return to the terminal and press:

```text
Ctrl+C
```

Confirm shutdown if prompted.

### Using Visual Studio Code

Open the project folder from the activated terminal:

```bash
code .
```

Open one of the `.ipynb` files.

In the upper-right corner of the notebook, select the kernel:

```text
Python (.venv - Chapter 5 Visual Labs)
```

Depending on the Visual Studio Code version, the selection path may appear as:

```text
Select Kernel
→ Select Another Kernel
→ Jupyter Kernel
→ Python (.venv - Chapter 5 Visual Labs)
```

It may also appear under:

```text
Select Kernel
→ Python Environments
```

Do not select a system Python version such as `Python 3.14` when the lab environment uses a different Python version.

Terminal activation and notebook kernel selection are separate. Seeing `(.venv)` in the terminal does not guarantee that the notebook is using the same environment.

## 8. Verify the Notebook Kernel

Run the following code in a notebook cell:

```python
import sys

print(sys.executable)
print(sys.version)
```

On Linux or macOS, the interpreter path should include:

```text
chapter5_visual_labs/.venv/bin/python
```

On Windows, it should include:

```text
chapter5_visual_labs\.venv\Scripts\python.exe
```

If the path points to a system Python installation instead, change the notebook kernel before continuing.

## 9. Run Notebook Cells

Run the current cell with:

```text
Shift+Enter
```

Run all cells from the notebook menu:

```text
Run
→ Run All Cells
```

Run the notebooks in order when possible because later cells may depend on variables, classes, or functions created in earlier cells.

## 10. Deactivate the Virtual Environment

When finished, close Jupyter Notebook or Visual Studio Code and deactivate the environment:

```bash
deactivate
```

The `(.venv)` prefix should disappear from the terminal prompt.

Deactivating the environment does not delete it. Activate it again the next time you work on the labs.

## Returning to the Labs Later

After opening a new terminal, return to the project directory and reactivate the environment:

```bash
cd "/path/to/chapter5_visual_labs"
source .venv/bin/activate
```

Then start Jupyter Notebook:

```bash
jupyter notebook
```

Or open Visual Studio Code:

```bash
code .
```

## Managing Jupyter Kernels

Jupyter kernel specifications are saved configurations that tell Jupyter which Python interpreter to use. A listed kernel is not necessarily a currently running process.

### List Installed Kernels

Run:

```bash
python -m jupyter kernelspec list
```

Example:

```text
Available kernels:
  python3                 /path/to/project/.venv/share/jupyter/kernels/python3
  chapter3-search-labs    /home/student/.local/share/jupyter/kernels/chapter3-search-labs
  chapter5-visual-labs    /home/student/.local/share/jupyter/kernels/chapter5-visual-labs
```

The `python3` entry inside the current project's `.venv` belongs to the active virtual environment and normally should not be removed manually.

### Inspect a Kernel

To inspect a registered kernel, open its `kernel.json` file.

Example:

```bash
cat ~/.local/share/jupyter/kernels/chapter5-visual-labs/kernel.json
```

Look at the first path in the `"argv"` list. It should point to the intended Python interpreter.

Example:

```json
{
  "argv": [
    "/path/to/chapter5_visual_labs/.venv/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python (.venv - Chapter 5 Visual Labs)",
  "language": "python"
}
```

If the path points to an old, deleted, or incorrect virtual environment, remove and recreate the kernel.

### Remove an Old or Duplicate Kernel

Remove a kernel by its registered name:

```bash
python -m jupyter kernelspec uninstall kernel-name
```

Example:

```bash
python -m jupyter kernelspec uninstall chapter5-visual-labs
```

Jupyter will ask for confirmation. Enter:

```text
y
```

Multiple old kernels can be removed in one command:

```bash
python -m jupyter kernelspec uninstall old-kernel-1 old-kernel-2 old-kernel-3
```

Only remove kernels that are no longer needed. Do not manually delete the current project's `.venv/share/jupyter/kernels/python3` directory.

### Re-register the Chapter 5 Kernel

After removing an incorrect or duplicate kernel, activate the environment and register it again:

```bash
source .venv/bin/activate
python -m ipykernel install --user --name chapter5-visual-labs --display-name "Python (.venv - Chapter 5 Visual Labs)"
```

Confirm the result:

```bash
python -m jupyter kernelspec list
```

### Check for Running Jupyter Processes

Installed kernel specifications are different from running kernel processes.

On Linux or macOS, check for running Jupyter or IPython kernel processes with:

```bash
ps -ef | grep -E 'jupyter|ipykernel' | grep -v grep
```

Stop a Jupyter server started from a terminal by returning to that terminal and pressing:

```text
Ctrl+C
```

In Visual Studio Code, use the Command Palette:

```text
Ctrl+Shift+P
→ Jupyter: Shut Down All Kernels
```

After adding or removing kernels, reload Visual Studio Code:

```text
Ctrl+Shift+P
→ Developer: Reload Window
```

## Common Problems

### The Terminal Does Not Show `(.venv)`

Make sure you are in the correct project directory:

```bash
pwd
ls -la
```

Confirm that `.venv` exists, then activate it:

```bash
source .venv/bin/activate
```

If `.venv` does not exist, create it:

```bash
python3 -m venv .venv
```

### Visual Studio Code Asks to Install `ipykernel`

First confirm that the notebook is using the correct kernel.

Activate the environment and install `ipykernel`:

```bash
source .venv/bin/activate
python -m pip install ipykernel
```

Register the kernel again:

```bash
python -m ipykernel install --user --name chapter5-visual-labs --display-name "Python (.venv - Chapter 5 Visual Labs)"
```

Reload Visual Studio Code:

```text
Ctrl+Shift+P
→ Developer: Reload Window
```

Then select:

```text
Python (.venv - Chapter 5 Visual Labs)
```

### Visual Studio Code Shows the Wrong Python Version

Open the Command Palette:

```text
Ctrl+Shift+P
```

Select:

```text
Python: Select Interpreter
```

Choose the interpreter located inside the project's `.venv` directory.

On Linux or macOS, obtain the exact interpreter path with:

```bash
realpath .venv/bin/python
```

### A Package Cannot Be Imported

Confirm that the environment is active:

```bash
which python
```

Then install the missing package:

```bash
python -m pip install package-name
```

For example:

```bash
python -m pip install matplotlib
```

Restart the notebook kernel after installing new packages.

### Interactive Widgets Do Not Appear

Install or upgrade `ipywidgets`:

```bash
python -m pip install --upgrade ipywidgets
```

Restart the notebook kernel and run the cells again.

The notebooks can still display static first and last frames when interactive widgets are unavailable.

## Optional: Remove and Recreate the Environment

Only do this when the environment is damaged or incorrectly configured.

Deactivate it first:

```bash
deactivate
```

Remove it:

```bash
rm -rf .venv
```

Recreate and configure it:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install notebook matplotlib ipywidgets ipykernel
python -m ipykernel install --user --name chapter5-visual-labs --display-name "Python (.venv - Chapter 5 Visual Labs)"
```

Be careful with `rm -rf`. Confirm that you are inside the correct project folder before running it.
