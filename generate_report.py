from __future__ import annotations
import os, sys, shutil, subprocess, tempfile
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

data = {
    "gender": {"Male": 13222, "Female": 14025},
    "academic_level": {
        "Undergraduate": 7967,
        "Graduate": 11076,
        "Post‑Graduation Training": 7881,
        "Other": 323
    },
    "visa_type": {"F‑1": 26671, "J‑1": 337, "Other": 239},
    "undergrad_programs": [
        ("Economics", "College of Arts & Science", 642),
        ("Global Liberal Studies", "College of Arts & Science", 586),
        ("Media, Culture & Communication", "Steinhardt", 413),
        ("Business", "Stern School of Business", 402)
    ],
    "grad_programs": [
        ("Integrated Marketing", "School of Professional Studies", 839),
        ("Computer Engineering", "Tandon School of Engineering", 773),
        ("Management of Technology", "Tandon School of Engineering", 475),
        ("Management & Systems", "School of Professional Studies", 463)
    ]
}

# Charts
STATIC_DIR = Path("static/charts")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def generate_donut(data_dict: dict[str,int], filename: str, colors: list[str]) -> None:
    labels, sizes = list(data_dict.keys()), list(data_dict.values())
    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, _ = ax.pie(
        sizes, labels=None, startangle=-40,
        wedgeprops=dict(width=0.4), colors=colors
    )
    ax.set(aspect="equal")
    plt.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(STATIC_DIR / filename, transparent=True)
    plt.close()

# Make all three donuts
generate_donut(data["gender"],          "gender_chart.png",
               ["#C8102E", "#9E0B20"])
generate_donut(data["academic_level"], "academic_level_chart.png",
               ["#C8102E", "#9E0B20", "#F58A1F", "#69737C"])
generate_donut(data["visa_type"],      "visa_type_chart.png",
               ["#C8102E", "#69737C", "#F58A1F"])

# Jinja2 rendering
env      = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("report.html")
# html_out = template.render(data=data)
project_root = Path(__file__).resolve().parent.as_uri() + "/"
print(project_root)
html_out = template.render(data=data, base_href=project_root)


# Write HTML to a temporary file so Chrome can open it via file://
tmp_dir   = Path(tempfile.mkdtemp())
html_file = tmp_dir / "report.html"
html_file.write_text(html_out, encoding="utf‑8")

shutil.copytree("static", tmp_dir / "static", dirs_exist_ok=True)

# check for chrom binary
def find_chrome() -> str | None:
    candidates = [
        "google-chrome", "chromium-browser", "chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "chrome"  # custom alias
    ]
    for exe in candidates:
        path = shutil.which(exe)
        if path:
            return path
    return None

chrome_path = find_chrome()
if not chrome_path:
    sys.exit("❌  Chrome/Chromium executable not found. Install it and rerun.")

# Run Chrome in headless mode to generate the PDF
OUTPUT_PDF = Path("output/report.pdf").resolve()
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

cmd = [
    chrome_path,
    "--headless",          # 'new' mode (Chrome ≥ 109).  Use --headless if older.
    "--disable-gpu",
    f"--print-to-pdf={OUTPUT_PDF}",
    f"file://{html_file}"
]

print("🚀  Generating PDF with Chrome…")
proc = subprocess.run(cmd, capture_output=True, text=True)
if proc.returncode:
    print(proc.stderr)
    sys.exit(f"❌  Chrome failed with exit {proc.returncode}")

print(f"✅  Report generated: {OUTPUT_PDF}")

shutil.rmtree(tmp_dir, ignore_errors=True)
