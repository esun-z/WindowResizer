import os
import subprocess
from pathlib import Path

def run(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def compile_uis():
    ui_dir = Path(".")  # or wherever your .ui files are
    out_dir = Path(".")  # adjust as needed

    for ui_file in ui_dir.glob("*.ui"):
        py_file = out_dir / f"ui_{ui_file.stem}.py"
        run(["pyside6-uic", str(ui_file), "-o", str(py_file)])

def compile_translations():
    ts_dir = Path("i18n")
    for ts_file in ts_dir.glob("*.ts"):
        qm_file = ts_file.with_suffix(".qm")
        run(["pyside6-lrelease", str(ts_file), "-qm", str(qm_file)])

if __name__ == "__main__":
    compile_uis()
    compile_translations()