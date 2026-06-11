# Developer Log — Entry 00: Environment Setup

**Date:** 2026-06-05 | **Sprint:** Pre-Sprint (Before Sprint 1) | **Status:** Completed

---

## What We Did

### 1. Verified Python Installation
Confirmed Python was already installed on the machine.

```
python --version
→ Python 3.13.3
```

### 2. Created the Project Folder
Chose Desktop as the project location and created the root folder.

```
cd C:\Users\Marlan Alfonso\Desktop
mkdir Sinaing-Predictor
cd Sinaing-Predictor
```

### 3. Created Full Folder Structure
```
mkdir data\raw, data\processed, db, src\etl, notebooks, models, backend, frontend, tests, .github\workflows, docs\sprint-logs, docs\developer-logs, paper
```

Added `.gitkeep` files to empty folders so Git would track them.

### 4. Set Up Python Virtual Environment

**Blocker encountered:** Running `python -m venv venv` hung and was interrupted, leaving a broken venv folder.

**Root cause:** The `ensurepip` step inside venv creation timed out or was accidentally interrupted with Ctrl+C.

**Solution:**
- Deleted the broken venv with `rmdir /s /q venv`
- Re-created venv without pip: `python -m venv venv --without-pip`
- Activated via cmd: `cmd /k "venv\Scripts\activate.bat"`
- Manually installed pip using the get-pip.py bootstrap script

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip --version
→ pip 26.1.2
```

**Time lost:** ~20 minutes

**Lesson learned:** On Windows with Python 3.13, `ensurepip` can hang in certain network or antivirus environments. Using `--without-pip` and bootstrapping manually is a reliable workaround.

### 5. Installed Core Dependencies (Sprint 1)

```
pip install pandas numpy matplotlib seaborn sqlalchemy jupyter ipykernel
pip freeze > requirements.txt
```

### 6. Registered Jupyter Kernel

```
python -m ipykernel install --user --name=sinaing --display-name "Sinaing Predictor"
```

This allows selecting the venv as the kernel inside Jupyter notebooks.

### 7. Opened Project in VS Code

```
code .
```

Set Python interpreter to the venv via `Ctrl+Shift+P → Python: Select Interpreter`.

### 8. Initialized Git

```
git init
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
```

Added the following to the bottom of `.gitignore`:

```
venv/
*.pkl
*.db
.env
.ipynb_checkpoints/
```

### 9. First Commit

```
git add .
git commit -m "chore: initialize project structure"
```

### 10. Pushed to GitHub

Created a new empty public repository at github.com, then:

```
git remote add origin https://github.com/YOUR_USERNAME/sinaing-predictor.git
git branch -M main
git push -u origin main
```

---

## Environment Summary

| Tool | Version |
|---|---|
| Python | 3.13.3 |
| pip | 26.1.2 |
| pandas | latest |
| numpy | latest |
| matplotlib | latest |
| seaborn | latest |
| sqlalchemy | latest |
| jupyter | latest |
| ipykernel | latest |
| Git | installed |
| VS Code | installed |
| Node.js | 18+ installed |

---

## Blockers

| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| `python -m venv venv` hung on ensurepip | Possible network/AV interference or accidental interrupt | Used `--without-pip` flag + manual get-pip.py bootstrap | ~20 min |
| PowerShell could not run `venv\Scripts\activate` | PS script execution policy blocks `.ps1` by default | Used `cmd /k "venv\Scripts\activate.bat"` instead | ~5 min |

---

## Next Steps

- Sprint 1, Week 1: Download PSA OpenStat datasets (2015–2026)
- Explore WFP Economic Explorer for cross-validation data
- Document all sources in README
- Commit raw CSV files to `/data/raw/`