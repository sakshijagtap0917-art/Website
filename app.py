from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Technical skills
SKILLS = [
    "Python", "Java", "C", "C++", "C#", "JavaScript",
    "HTML", "CSS", "React", "Angular", "Django", "Flask",
    "SQL", "MySQL", "MongoDB", "Git", "GitHub",
    "AWS", "Azure", "Power BI", "Excel",
    "Machine Learning", "Data Science", "REST API"
]

# Experience-related keywords
EXPERIENCE_KEYWORDS = [
    "Software Developer",
    "Software Engineer",
    "Python Developer",
    "Java Developer",
    "Web Developer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Intern",
    "Internship",
    "Trainee",
    "Developer",
    "Engineer",
    "Work Experience",
    "Professional Experience"
]

# Education keywords
EDUCATION_KEYWORDS = [
    "Bachelor",
    "B.Tech",
    "B.E",
    "BCA",
    "BCS",
    "MCA",
    "M.Tech",
    "M.E",
    "Master",
    "Computer Science",
    "Information Technology",
    "Education"
]


def extract_text_from_pdf(file_path):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def find_skills(text):

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def find_experience_keywords(text):

    found_experience = []

    for keyword in EXPERIENCE_KEYWORDS:

        if re.search(
            re.escape(keyword),
            text,
            re.IGNORECASE
        ):
            found_experience.append(keyword)

    return found_experience


def find_education_details(text):

    found_education = []

    for keyword in EDUCATION_KEYWORDS:

        if re.search(
            re.escape(keyword),
            text,
            re.IGNORECASE
        ):
            found_education.append(keyword)

    # Percentage
    percentages = re.findall(
        r"\b\d{1,3}(?:\.\d{1,2})?\s*%",
        text
    )

    for percentage in percentages:
        found_education.append("Percentage: " + percentage)

    # CGPA
    cgpa = re.findall(
        r"\b(?:CGPA|GPA)\s*[:\-]?\s*\d+(?:\.\d+)?",
        text,
        re.IGNORECASE
    )

    for value in cgpa:
        found_education.append(value)

    # College / University lines
    lines = text.splitlines()

    for line in lines:

        clean_line = line.strip()

        if any(word in clean_line.lower()
               for word in [
                   "college",
                   "university",
                   "institute",
                   "mahavidyalaya"
               ]):

            if len(clean_line) > 3:
                found_education.append(
                    "College: " + clean_line
                )

    return list(dict.fromkeys(found_education))


def find_sections(text):

    sections = []

    section_keywords = {
        "Contact Information": [
            "email", "@", "phone", "mobile"
        ],

        "Education": [
            "education",
            "qualification",
            "academic"
        ],

        "Skills": [
            "skills",
            "technical skills"
        ],

        "Projects": [
            "projects",
            "project"
        ],

        "Experience": [
            "experience",
            "work experience",
            "internship"
        ],

        "Certifications": [
            "certification",
            "certifications"
        ]
    }

    for section, keywords in section_keywords.items():

        for keyword in keywords:

            if re.search(
                re.escape(keyword),
                text,
                re.IGNORECASE
            ):

                sections.append(section)
                break

    return sections


def calculate_ats_score(
    text,
    skills,
    education,
    experience,
    sections
):

    score = 0

    # 1. Skills - 30 points
    skill_score = min(len(skills) * 2, 30)
    score += skill_score

    # 2. Education - 20 points
    if education:
        score += 15

        if any(
            "Percentage:" in item or
            "CGPA" in item.upper()
            for item in education
        ):
            score += 5

    # 3. Experience - 20 points
    if experience:
        score += min(len(experience) * 4, 20)

    # 4. Important sections - 20 points
    important_sections = [
        "Contact Information",
        "Education",
        "Skills",
        "Projects",
        "Experience"
    ]

    section_score = 0

    for section in important_sections:

        if section in sections:
            section_score += 4

    score += section_score

    # 5. Resume length/content - 10 points
    word_count = len(text.split())

    if word_count >= 300:
        score += 10

    elif word_count >= 200:
        score += 8

    elif word_count >= 100:
        score += 5

    elif word_count >= 50:
        score += 3

    # Final score
    score = min(score, 100)

    return score


def generate_suggestions(
    skills,
    education,
    experience,
    sections
):

    suggestions = []

    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills."
        )

    if not education:
        suggestions.append(
            "Add complete education details."
        )

    if education and not any(
        "Percentage:" in item or
        "CGPA" in item.upper()
        for item in education
    ):
        suggestions.append(
            "Add percentage or CGPA in education section."
        )

    if not experience:
        suggestions.append(
            "Add internship or work experience if available."
        )

    if "Projects" not in sections:
        suggestions.append(
            "Add academic or personal projects."
        )

    if "Certifications" not in sections:
        suggestions.append(
            "Add relevant certifications."
        )

    if not suggestions:
        suggestions.append(
            "Your resume has good ATS-friendly content."
        )

    return suggestions


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = None

    if request.method == "POST":

        if "resume" not in request.files:

            error = "Please upload a resume."

        else:

            file = request.files["resume"]

            if file.filename == "":

                error = "Please select a PDF file."

            elif not file.filename.lower().endswith(".pdf"):

                error = "Only PDF files are supported."

            else:

                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    file.filename
                )

                file.save(file_path)

                try:

                    text = extract_text_from_pdf(
                        file_path
                    )

                    skills = find_skills(text)

                    experience = find_experience_keywords(
                        text
                    )

                    education = find_education_details(
                        text
                    )

                    sections = find_sections(text)

                    score = calculate_ats_score(
                        text,
                        skills,
                        education,
                        experience,
                        sections
                    )

                    suggestions = generate_suggestions(
                        skills,
                        education,
                        experience,
                        sections
                    )

                    result = {
                        "score": score,
                        "skills": skills,
                        "education": education,
                        "experience": experience,
                        "sections": sections,
                        "suggestions": suggestions
                    }

                except Exception as e:

                    error = "Unable to analyze this PDF."

                    print("Error:", e)

                finally:

                    if os.path.exists(file_path):
                        os.remove(file_path)

    return render_template(
        "index.html",
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)