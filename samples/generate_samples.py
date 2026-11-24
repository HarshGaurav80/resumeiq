"""
Generates the two demo resumes in this folder (fictional people):

  * resume_priya_sharma_data_analyst.pdf   – PDF, strong data-analyst resume
  * resume_arjun_mehta_web_developer.docx  – DOCX, web-developer resume with weak bullet points

Run from the backend virtualenv (needs reportlab + python-docx):
    python ../samples/generate_samples.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

HERE = Path(__file__).resolve().parent

PRIYA = {
    "name": "Priya Sharma",
    "contact": "priya.sharma@example.com | +91 98765 43210 | Pune, India | linkedin.com/in/priya-sharma-demo | github.com/priya-demo",
    "sections": [
        ("Summary", ["Final-year Computer Science student and aspiring Data Analyst with hands-on experience in SQL, "
                     "Python and Power BI. Skilled at turning raw data into dashboards and insights that drive decisions."]),
        ("Education", ["B.Tech in Computer Science and Engineering, Savitribai Phule Pune University (2022 - 2026), CGPA 8.7/10",
                       "Higher Secondary (Science), Delhi Public School, Pune (2022), 92%"]),
        ("Skills", ["Languages: Python, SQL, R",
                    "Tools: Power BI, Tableau, Advanced Excel (Pivot Tables, VLOOKUP), Jupyter, Git",
                    "Libraries: Pandas, NumPy, Matplotlib, Seaborn, scikit-learn",
                    "Concepts: Data Cleaning, Data Visualization, Statistics, Hypothesis Testing, ETL, Dashboards",
                    "Soft skills: Communication, Problem Solving, Teamwork"]),
        ("Experience", ["Data Analyst Intern, BrightCart Retail Pvt. Ltd. (May 2025 - Jul 2025)",
                        "• Built 6 interactive Power BI dashboards tracking sales across 40 stores, used weekly by the regional managers.",
                        "• Wrote SQL queries on a 2M-row PostgreSQL sales database to identify slow-moving inventory, cutting stock holding cost by 12%.",
                        "• Automated a weekly Excel report with Python and Pandas, saving the team 5 hours every week.",
                        "• Presented findings on customer churn to stakeholders and recommended a loyalty offer adopted in 3 cities."]),
        ("Projects", ["Customer Churn Analysis | Python, Pandas, scikit-learn, Seaborn",
                      "• Analyzed 7,000 telecom customer records and built a logistic regression model with 81% accuracy to predict churn.",
                      "COVID-19 India Dashboard | Tableau, Excel",
                      "• Designed a Tableau dashboard visualizing state-wise trends; published on Tableau Public with 1,200+ views.",
                      "E-commerce Sales SQL Case Study | MySQL",
                      "• Solved 25 business questions using joins, window functions and CTEs on a 100k-order dataset (github.com/priya-demo/sql-case-study)."]),
        ("Certifications", ["Google Data Analytics Professional Certificate - Coursera (2024)",
                            "Microsoft Power BI Data Analyst (PL-300) - Microsoft (2025)",
                            "SQL (Advanced) - HackerRank (2024)"]),
        ("Achievements", ["Winner, Inter-college Data Hackathon 2024 (out of 85 teams)"]),
    ],
}

ARJUN = {
    "name": "Arjun Mehta",
    "contact": "arjun.mehta.dev@example.com | +91 91234 56789 | Bengaluru, India",
    "sections": [
        ("Career Objective", ["To obtain a challenging position in a reputed organization where I can use my skills and grow."]),
        ("Education", ["Bachelor of Computer Applications (BCA), Christ University, Bengaluru (2023 - 2026), CGPA 7.9",
                       "Class XII (CBSE), Kendriya Vidyalaya, Mysuru (2023), 84%"]),
        ("Technical Skills", ["HTML, CSS, JavaScript, Bootstrap, PHP, MySQL, WordPress, Git, Java"]),
        ("Internship", ["Web Development Intern, PixelCraft Studios (Jan 2025 - Mar 2025)",
                        "• Responsible for making the company website responsive.",
                        "• Worked on fixing bugs in the WordPress plugins.",
                        "• Helped the senior developer with landing pages for clients.",
                        "• Was involved in testing the website on different browsers."]),
        ("Projects", ["College Event Management Website - HTML, CSS, JavaScript, PHP, MySQL",
                      "• Made a website where students can register for college fest events.",
                      "Personal Portfolio - HTML, CSS, Bootstrap",
                      "• Worked on a portfolio site to show my projects.",
                      "Weather App - JavaScript",
                      "• Helped to build a weather app using a public API."]),
        ("Certifications", ["Responsive Web Design - freeCodeCamp (2024)",
                            "JavaScript Basics - Udemy (2024)"]),
        ("Hobbies", ["Cricket, gaming, music"]),
    ],
}


def build_pdf(data: dict, path: Path) -> None:
    ss = getSampleStyleSheet()
    name = ParagraphStyle("n", parent=ss["Title"], fontSize=20, spaceAfter=2)
    contact = ParagraphStyle("c", parent=ss["Normal"], fontSize=9, alignment=1, textColor="#444444")
    head = ParagraphStyle("h", parent=ss["Heading3"], fontSize=12, spaceBefore=8, spaceAfter=3, textColor="#3730a3")
    body = ParagraphStyle("b", parent=ss["Normal"], fontSize=10, leading=13)

    story = [Paragraph(data["name"], name), Paragraph(data["contact"], contact), Spacer(1, 6)]
    for title, lines in data["sections"]:
        story.append(Paragraph(title.upper(), head))
        bullets = []
        for line in lines:
            if line.startswith("• "):
                bullets.append(ListItem(Paragraph(line[2:], body), leftIndent=10))
            else:
                if bullets:
                    story.append(ListFlowable(bullets, bulletType="bullet", start="•", leftIndent=12))
                    bullets = []
                story.append(Paragraph(line, body))
        if bullets:
            story.append(ListFlowable(bullets, bulletType="bullet", start="•", leftIndent=12))
    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=14 * mm, bottomMargin=14 * mm, title=f"{data['name']} Resume").build(story)


def build_docx(data: dict, path: Path) -> None:
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    doc.add_heading(data["name"], level=0)
    doc.add_paragraph(data["contact"])
    for title, lines in data["sections"]:
        doc.add_heading(title, level=1)
        for line in lines:
            if line.startswith("• "):
                doc.add_paragraph(line[2:], style="List Bullet")
            else:
                doc.add_paragraph(line)
    doc.save(str(path))


if __name__ == "__main__":
    build_pdf(PRIYA, HERE / "resume_priya_sharma_data_analyst.pdf")
    build_docx(ARJUN, HERE / "resume_arjun_mehta_web_developer.docx")
    print("Sample resumes written to", HERE)
