# VS Code + Jupyter Notebooks — Instructor Quick-Start
### COMP 469 · Lab 01 Setup Guide

> **This is a first-time guide.** Follow every step in order. It takes about 10 minutes total.

---

## Part 1 — Install What You Need (One Time Only)

### Step 1 · Install VS Code
Download from **https://code.visualstudio.com** and install normally.

### Step 2 · Install Python 3.11
Download from **https://www.python.org/downloads/** — pick the 3.11.x installer.

> **Windows users:** On the first installer screen, check ✅ **"Add Python to PATH"** before clicking Install Now. If you miss this, uninstall and reinstall.

Verify in a terminal:
```
python --version
```
Should print `Python 3.11.x`.

### Step 3 · Install VS Code Extensions

Open VS Code. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (Mac) to open Extensions.

Search for and install these two:

| Extension name | Publisher |
|---|---|
| **Python** | Microsoft |
| **Jupyter** | Microsoft |

Both are free. VS Code may prompt you to install them automatically when you open a `.ipynb` file — that works too.

---

## Part 2 — Set Up the Course Python Environment (One Time Per Project)

Jupyter notebooks run inside a **virtual environment** — an isolated Python installation with only the packages you choose. This prevents conflicts with other Python projects on your machine.

### Step 4 · Open the lab folder in VS Code

`File → Open Folder` → select the folder where you saved the `.ipynb` file.

### Step 5 · Open the integrated terminal

`Terminal → New Terminal`  
(or press `` Ctrl+` `` on Windows/Linux, `` Cmd+` `` on Mac)

A terminal panel opens at the bottom of VS Code. All the commands below go here.

### Step 6 · Create the virtual environment

**macOS / Linux:**
```bash
python3 -m venv .env
source .env/bin/activate
```

**Windows PowerShell:**
```powershell
py -m venv .env
# If the next line is blocked by a security policy, first run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.env\Scripts\Activate.ps1
```

You'll know it worked when your terminal prompt changes to show `(.env)` at the start.

### Step 7 · Install required packages
```bash
python -m pip install --upgrade pip
python -m pip install ipykernel notebook jupyter matplotlib
```

This takes 1–2 minutes. You'll see a progress bar.

### Step 8 · Register the environment as a Jupyter kernel
```bash
python -m ipykernel install --user --name comp469 --display-name "COMP 469 (.env)"
```

You only need to do Steps 6–8 once per machine. Next time, just activate the environment (Step 6) before opening VS Code.

---

## Part 3 — Open and Run the Notebook

### Step 9 · Open the notebook file

In the VS Code Explorer panel (left sidebar), click `COMP469_Lab01_SOLUTION.ipynb`.

The notebook opens with cells visible. It will look like this:

```
[ ]  import random                    ← code cell (not yet run)
     from collections import deque
     ...
```

### Step 10 · Select the correct kernel

Look at the **top-right corner** of the notebook editor. You'll see a button that says something like `Select Kernel` or `Python 3.x`.

Click it → a dropdown appears at the top of the screen → choose:

```
COMP 469 (.env)
```

If you don't see it, click **"Python Environments…"** and look for `comp469` in the list.

> ⚠️ **This is the most common mistake.** If the kernel is wrong, `import matplotlib` will fail with `ModuleNotFoundError`. Always check the kernel first.

### Step 11 · Run all cells

Click the **▶▶ Run All** button at the top of the notebook toolbar.

Each cell runs in sequence. Watch for:
- A **green checkmark** ✅ = cell succeeded
- A **red X** ❌ = cell errored (read the error message below the cell)
- A **spinning circle** = cell is currently running

The first full run takes 5–10 seconds because matplotlib renders several plots.

---

## Part 4 — Understanding the VS Code Jupyter Interface

```
┌─────────────────────────────────────────────────────────┐
│  ▶ Run All  | ↺ Restart  | ⬛ Interrupt | Kernel: COMP 469 (.env) │  ← toolbar
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [ Markdown cell ]  — formatted text, not runnable      │
│                                                         │
│  [1] import random          ← [1] = ran first           │
│      ...                                                │
│  Out: Setup complete.                                   │
│       Python: 3.11.x                                    │
│                                                         │
│  [2] env = VacuumEnvironment(...)                       │
│  Out: Start location: (0, 0)                            │
│       Dirty squares: 8                                  │
│       ...                                               │
│                                                         │
│  [3] display_text(env)      ← plots appear inline below │
│  [image of grid]                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key controls

| Action | Shortcut |
|---|---|
| Run current cell | `Shift+Enter` |
| Run current cell, stay on it | `Ctrl+Enter` |
| Run all cells | Toolbar → **Run All** |
| Restart kernel (clears all output & variables) | Toolbar → **↺ Restart** |
| Restart and run all | `Ctrl+Shift+P` → type *"Notebook: Restart and Run All"* |
| Insert cell below | `B` (when a cell is selected but not being edited) |
| Delete current cell | `DD` (press D twice) |
| Switch cell to markdown | `M` |
| Switch cell to code | `Y` |

### What "Restart and Run All" means

Restarting the kernel clears Python's memory — all variables, imported modules, and function definitions are erased. Then "Run All" re-executes every cell from the top. This is what the submission checklist means by *"runs top to bottom without errors after a fresh restart."* Always do this before submitting or grading.

---

## Part 5 — Every Time You Come Back

Each new VS Code session, you need to re-activate the environment. VS Code usually does this automatically if you've already set it up, but if you see `ModuleNotFoundError`, do this:

1. Open the terminal (`` Ctrl+` ``)
2. Activate: `source .env/bin/activate` (Mac/Linux) or `.\.env\Scripts\Activate.ps1` (Windows)
3. Check the kernel in the top-right corner — should say **COMP 469 (.env)**
4. Restart the kernel: toolbar → **↺ Restart**

---

## Part 6 — Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'matplotlib'` | Wrong kernel selected. Click the kernel button top-right → choose **COMP 469 (.env)** |
| Kernel dropdown doesn't show COMP 469 | Re-run Step 8 in the terminal, then reload VS Code (`Ctrl+Shift+P` → "Developer: Reload Window") |
| `.env` activation blocked on Windows | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first, then activate |
| Plots don't appear | Make sure the Jupyter extension is installed (Step 3). Try `Ctrl+Shift+P` → "Jupyter: Clear All Outputs" then Run All |
| Cell shows `[*]` forever | The cell is stuck. Click toolbar → **⬛ Interrupt**, then re-run |
| `NameError: name 'VacuumEnvironment' is not defined` | Cells ran out of order. Always run from the top — use **Run All** or **Restart and Run All** |
| Can't find the `.env` folder | It's hidden by default. In VS Code Explorer, click the `...` menu → "Show Hidden Files" |

---

## Part 7 — Quick Reference Card

```
First time on a new machine
────────────────────────────
1. Install VS Code + Python 3.11
2. Install Python + Jupyter extensions in VS Code
3. Open folder → open terminal
4. python3 -m venv .env
5. source .env/bin/activate          (or Windows: .\.env\Scripts\Activate.ps1)
6. pip install ipykernel notebook jupyter matplotlib
7. python -m ipykernel install --user --name comp469 --display-name "COMP 469 (.env)"
8. Open .ipynb file → select "COMP 469 (.env)" kernel → Run All

Every subsequent session
─────────────────────────
1. Open folder in VS Code
2. Check kernel (top-right) says "COMP 469 (.env)"
3. Run All (or Restart & Run All to be safe)
```
