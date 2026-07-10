# Chapter 8 Visual Labs: First-Order Logic

These five standalone Jupyter notebooks teach Chapter 8, **First-Order Logic**, with executable Python code and visualizations. Each notebook can be run independently; students do not need to import code from another lab.

## Lab list

1. **Lab 08A — FOL Models, Symbols, and Interpretations**  
   Build a finite first-order model with objects, constants, predicates, relations, and functions. Visualize the Richard/John/crown example and evaluate atomic, complex, universal, and existential sentences.

2. **Lab 08B — Quantifiers and Database Semantics**  
   Use relation matrices to see how `∀` and `∃` work, why nested quantifier order matters, how quantified De Morgan rules behave, and how database semantics differs from standard first-order semantics.

3. **Lab 08C — FOL Wumpus World Model Checking**  
   Represent Wumpus World rules using FOL-style schemas such as `Breeze(s) ⇔ ∃p Adjacent(p,s) ∧ Pit(p)`. Step through percepts and watch the set of possible worlds shrink visually.

4. **Lab 08D — Knowledge Engineering with Digital Circuits**  
   Build a structured FOL-style ontology for a full adder using `Gate`, `Type`, `In`, `Out`, `Connected`, and `Signal`. Visualize signal propagation, run ASKVARS-style queries, and debug a faulty circuit KB.

5. **Lab 08E — FOL Workbench: ASKVARS, Ontologies, and Limits**  
   Use a finite-domain workbench to answer variable queries, visualize family and enrollment ontologies, compare FOL schema size with propositional grounding, and examine vague predicates such as `Tall(x)`.

## What students need

- A computer with Python installed. Python 3.9 or newer is recommended.
- No internet connection is needed after the packages are installed.
- The notebooks use only common packages: `jupyter`, `matplotlib`, `ipywidgets`, and `ipykernel`.

## Option 1: Run with a Python virtual environment, recommended

A virtual environment keeps this lab's packages separate from the rest of your computer.

### Windows PowerShell

Open PowerShell in the folder that contains these notebooks. Then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m jupyter notebook
```

If PowerShell says script execution is disabled, run this command in the same PowerShell window and then try the activation command again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m jupyter notebook
```

### macOS or Linux terminal

Open Terminal in the folder that contains these notebooks. Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m jupyter notebook
```

On some systems, the command may be `python` instead of `python3`.

## How to know the environment is active

After activation, your terminal prompt usually starts with `(.venv)`. You can also check with:

```bash
python -m pip --version
```

The path shown should include the `.venv` folder.

## How to deactivate or disable the environment

When you are done, type:

```bash
deactivate
```

This turns off the virtual environment for the current terminal window. It does not delete anything.

To completely remove the environment, first deactivate it, then delete the `.venv` folder. You can recreate it later with the setup commands above.

## Selecting the correct Jupyter kernel

When a notebook opens, use the top menu:

`Kernel` → `Change Kernel`

Choose the Python kernel connected to this environment. If you do not see one, activate the environment and run:

```bash
python -m ipykernel install --user --name chapter8-fol-labs --display-name "Python (chapter8-fol-labs)"
```

Then restart Jupyter Notebook and select `Python (chapter8-fol-labs)`.

## Option 2: Install directly without a virtual environment

This is simpler but less clean because packages are installed into your main Python setup:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m jupyter notebook
```

Use this only if your instructor or lab computer setup allows it.

## Running a notebook

1. Start Jupyter Notebook with `python -m jupyter notebook`.
2. A browser window will open.
3. Click one of the `.ipynb` files.
4. Run cells from top to bottom using `Shift + Enter`.
5. Always run the first code cell before running later cells.
6. Interactive sliders and dropdowns require `ipywidgets`. If widgets do not appear, the notebook still includes static fallback output.

## Troubleshooting

### `python` is not recognized

Python may not be installed or may not be on your PATH. On Windows, try:

```powershell
py --version
```

On macOS/Linux, try:

```bash
python3 --version
```

### `jupyter` is not recognized

Use:

```bash
python -m jupyter notebook
```

This uses the Jupyter installed inside the active Python environment.

### `ModuleNotFoundError: No module named matplotlib` or `ipywidgets`

Make sure the environment is active, then run:

```bash
python -m pip install -r requirements.txt
```

### Widgets do not display

Run:

```bash
python -m pip install --upgrade ipywidgets
```

Then restart the notebook kernel: `Kernel` → `Restart Kernel`.

### The notebook opens but uses the wrong Python

Install and select the dedicated kernel:

```bash
python -m ipykernel install --user --name chapter8-fol-labs --display-name "Python (chapter8-fol-labs)"
```

Then in Jupyter, choose `Kernel` → `Change Kernel` → `Python (chapter8-fol-labs)`.

### You want to start over

1. Close Jupyter.
2. In the terminal, run `deactivate` if the environment is active.
3. Delete `.venv`.
4. Recreate it using the setup commands.

## Suggested teaching sequence

- Use **08A** before formal proofs. It helps students understand what a model and interpretation are.
- Use **08B** when teaching quantifiers; the matrix makes nested quantifiers concrete.
- Use **08C** to connect Chapter 8 back to Wumpus World and show why FOL is more concise than propositional logic.
- Use **08D** as the main knowledge-engineering lab. It follows the chapter's circuit example closely.
- Use **08E** as a capstone or homework lab on ontology choices, variable queries, scaling, and limitations.

## Package list

The package list is in `requirements.txt`:

```text
jupyter
matplotlib
ipywidgets
ipykernel
```
