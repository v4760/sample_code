import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

# Sample data (you'd load this from Excel in production)
data = {
    "gender": {"Male": 13222, "Female": 14025},
    "academic_level": {
        "Undergraduate": 7967,
        "Graduate": 11076,
        "Post-Graduation Training": 7881,
        "Other": 323
    },
    "visa_type": {"F-1": 26671, "J-1": 337, "Other": 239},
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

def generate_donut(data_dict, filename, colors):
    labels = list(data_dict.keys())
    sizes = list(data_dict.values())
    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.4), startangle=-40, colors=colors)
    ax.set(aspect="equal")
    plt.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(f"static/charts/{filename}", transparent=True)
    plt.close()

# Generate charts
os.makedirs("static/charts", exist_ok=True)
generate_donut(data["gender"], "gender_chart.png", ["#C8102E", "#9E0B20"])
generate_donut(data["academic_level"], "academic_level_chart.png", ["#C8102E", "#9E0B20", "#F58A1F", "#69737C"])
generate_donut(data["visa_type"], "visa_type_chart.png", ["#C8102E", "#69737C", "#F58A1F"])

# Render template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("report.html")
html_out = template.render(data=data)

# Generate PDF
from pathlib import Path
HTML(string=html_out, base_url=Path(__file__).resolve().parent).write_pdf("output/report.pdf")

print("✅ Report generated: output/report.pdf")
