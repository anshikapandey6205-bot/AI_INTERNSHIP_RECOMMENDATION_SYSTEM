from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import re
from datetime import datetime


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = "internmatch-ai-secret-key-change-this"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "internships.json")


# =========================================================
# DATA FUNCTIONS
# =========================================================

def load_internships():
    """
    Load internship data from data/internships.json
    """

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("internships", [])

        return []

    except Exception as error:
        print("Error loading internships:", error)
        return []


def normalize(value):
    """
    Convert text into a comparable lowercase format.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def convert_to_list(value):
    """
    Converts strings/lists into a clean list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):

        # Support comma-separated values
        if "," in value:
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return [value.strip()] if value.strip() else []

    return []


# =========================================================
# MATCHING FUNCTIONS
# =========================================================

def calculate_domain_match(student_domain, internship_domains):

    student_domain = normalize(student_domain)

    internship_domains = [
        normalize(item)
        for item in convert_to_list(internship_domains)
    ]

    if not student_domain or not internship_domains:
        return 0

    # Exact match
    if student_domain in internship_domains:
        return 100

    # Partial match
    for domain in internship_domains:

        if student_domain in domain or domain in student_domain:
            return 80

    # Common domain relationships
    related_domains = {
        "ai": ["artificial intelligence", "machine learning", "data science"],
        "artificial intelligence": ["ai", "machine learning"],
        "machine learning": ["ai", "artificial intelligence", "data science"],
        "python": ["software development", "data science", "ai"],
        "web development": ["software development", "frontend", "backend"],
        "data science": ["data analysis", "machine learning", "ai"],
        "cyber security": ["cybersecurity", "information security"],
    }

    related = related_domains.get(student_domain, [])

    for domain in internship_domains:
        if domain in related:
            return 60

    return 0


def calculate_skill_match(student_skills, internship_skills):
    """
    Calculate skill compatibility between the student and internship.

    Returns:
        score: percentage match
        matched: skills that match
        missing: skills the student may need to learn
    """

    student_skills = convert_to_list(student_skills)
    internship_skills = convert_to_list(internship_skills)

    # Normalize all skills
    student_skills = [
        normalize(skill)
        for skill in student_skills
        if normalize(skill)
    ]

    internship_skills = [
        normalize(skill)
        for skill in internship_skills
        if normalize(skill)
    ]

    if not internship_skills:
        return 100, [], []

    if not student_skills:
        return 0, [], internship_skills

    # --------------------------------------------------------
    # Related skill groups
    # --------------------------------------------------------

    related_skills = {

        "python": [
            "python",
            "pandas",
            "numpy",
            "django",
            "flask",
            "fastapi",
            "machine learning",
            "data analysis"
        ],

        "java": [
            "java",
            "spring",
            "spring boot",
            "android"
        ],

        "javascript": [
            "javascript",
            "js",
            "react",
            "react.js",
            "node",
            "node.js",
            "frontend",
            "web development"
        ],

        "web development": [
            "web development",
            "html",
            "css",
            "javascript",
            "frontend",
            "backend",
            "react",
            "node.js"
        ],

        "data analysis": [
            "data analysis",
            "data analytics",
            "pandas",
            "numpy",
            "excel",
            "sql",
            "statistics",
            "python"
        ],

        "machine learning": [
            "machine learning",
            "ml",
            "artificial intelligence",
            "ai",
            "python",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "data science"
        ],

        "artificial intelligence": [
            "artificial intelligence",
            "ai",
            "machine learning",
            "deep learning",
            "python",
            "tensorflow",
            "pytorch"
        ],

        "data science": [
            "data science",
            "python",
            "machine learning",
            "statistics",
            "data analysis",
            "pandas",
            "numpy",
            "sql"
        ],

        "cybersecurity": [
            "cybersecurity",
            "cyber security",
            "information security",
            "network security",
            "ethical hacking",
            "penetration testing",
            "linux"
        ],

        "communication": [
            "communication",
            "communication skills",
            "presentation",
            "public speaking",
            "writing"
        ],

        "software development": [
            "software development",
            "programming",
            "python",
            "java",
            "javascript",
            "c++",
            "c",
            "git"
        ]
    }

    # --------------------------------------------------------
    # Check whether two skills are related
    # --------------------------------------------------------

    def skills_are_related(student_skill, required_skill):

        if student_skill == required_skill:
            return True

        # Direct substring match
        if (
            student_skill in required_skill
            or required_skill in student_skill
        ):
            return True

        # Check related skill groups
        for group in related_skills.values():

            student_related = student_skill in group
            required_related = required_skill in group

            if student_related and required_related:
                return True

        return False

    # --------------------------------------------------------
    # Calculate matches
    # --------------------------------------------------------

    matched = []
    missing = []

    for required_skill in internship_skills:

        found = False

        for student_skill in student_skills:

            if skills_are_related(
                student_skill,
                required_skill
            ):
                found = True
                break

        if found:
            matched.append(required_skill)
        else:
            missing.append(required_skill)

    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    score = round(
        (len(matched) / len(internship_skills)) * 100
    )

    return score, matched, missing

    # Skill aliases / equivalent technologies
    skill_aliases = {
        "python": [
            "python",
            "python programming",
            "python development"
        ],
        "javascript": [
            "javascript",
            "js",
            "javascript programming"
        ],
        "html": [
            "html",
            "html5"
        ],
        "css": [
            "css",
            "css3"
        ],
        "c++": [
            "c++",
            "cpp"
        ],
        "machine learning": [
            "machine learning",
            "ml"
        ],
        "artificial intelligence": [
            "artificial intelligence",
            "ai"
        ],
        "data science": [
            "data science",
            "data analytics",
            "data analysis"
        ],
        "web development": [
            "web development",
            "web developer"
        ],
        "frontend": [
            "frontend",
            "front end",
            "frontend development"
        ],
        "backend": [
            "backend",
            "back end",
            "backend development"
        ],
        "sql": [
            "sql",
            "mysql",
            "postgresql",
            "database"
        ],
        "cybersecurity": [
            "cybersecurity",
            "cyber security",
            "information security"
        ]
    }

    def get_canonical_skill(skill):
        for canonical, aliases in skill_aliases.items():
            if skill in aliases:
                return canonical

        return skill

    student_canonical = {
        get_canonical_skill(skill)
        for skill in student_skills
    }

    internship_canonical = {
        get_canonical_skill(skill)
        for skill in internship_skills
    }

    if not internship_canonical:
        return 0

    matched_skills = (
        student_canonical.intersection(internship_canonical)
    )

    score = (
        len(matched_skills) /
        len(internship_canonical)
    ) * 100

    return round(min(score, 100))

    student_skills = convert_to_list(student_skills)
    internship_skills = convert_to_list(internship_skills)

    student_skills = [
        normalize(skill)
        for skill in student_skills
    ]

    internship_skills = [
        normalize(skill)
        for skill in internship_skills
    ]

    student_skills = [
        skill for skill in student_skills if skill
    ]

    internship_skills = [
        skill for skill in internship_skills if skill
    ]

    if not internship_skills:
        return 50, [], []

    matched = []
    missing = []

    for required_skill in internship_skills:

        found = False

        for student_skill in student_skills:

            if (
                student_skill == required_skill
                or student_skill in required_skill
                or required_skill in student_skill
            ):
                found = True
                break

        if found:
            matched.append(required_skill)
        else:
            missing.append(required_skill)

    score = round(
        (len(matched) / len(internship_skills)) * 100
    )

    return score, matched, missing


def calculate_work_mode_match(student_mode, internship_modes):

    student_mode = normalize(student_mode)

    internship_modes = [
        normalize(mode)
        for mode in convert_to_list(internship_modes)
    ]

    if not student_mode or not internship_modes:
        return 50

    if student_mode in internship_modes:
        return 100

    # If internship offers flexible options
    for mode in internship_modes:
        if mode in ["remote", "hybrid", "on-site", "onsite"]:
            continue

    return 40


def calculate_location_match(student_location, internship_locations):
    """
    Calculate location compatibility.
    """

    student_location = normalize(student_location)

    internship_locations = [
        normalize(location)
        for location in convert_to_list(internship_locations)
    ]

    internship_locations = [
        location
        for location in internship_locations
        if location
    ]

    if not student_location or not internship_locations:
        return 50

    # Remote is compatible with any location
    if "remote" in internship_locations:
        return 100

    # Exact location match
    if student_location in internship_locations:
        return 100

    # Partial location match
    for location in internship_locations:

        if (
            student_location in location
            or location in student_location
        ):
            return 90

    # Common Indian location relationships
    related_locations = {
        "patna": ["bihar"],
        "bihar": ["patna"],

        "delhi": ["new delhi", "ncr"],
        "new delhi": ["delhi", "ncr"],

        "bangalore": ["bengaluru"],
        "bengaluru": ["bangalore"],

        "mumbai": ["maharashtra"],
        "maharashtra": ["mumbai"],

        "kolkata": ["west bengal"],
        "west bengal": ["kolkata"],

        "hyderabad": ["telangana"],
        "telangana": ["hyderabad"],

        "chennai": ["tamil nadu"],
        "tamil nadu": ["chennai"],

        "pune": ["maharashtra"],
    }

    related = related_locations.get(
        student_location,
        []
    )

    for location in internship_locations:
        if location in related:
            return 80

    return 30


# ============================================================
# EDUCATION MATCHING
# ============================================================

def calculate_education_match(
    student_education,
    internship_education
):
    """
    Calculate education/qualification compatibility.
    """

    student_education = normalize(
        student_education
    )

    internship_education = normalize(
        internship_education
    )

    if not internship_education:
        return 70

    if not student_education:
        return 40

    # Exact match
    if student_education == internship_education:
        return 100

    # Partial match
    if (
        student_education in internship_education
        or internship_education in student_education
    ):
        return 90

    education_groups = {
        "computer science": [
            "computer science",
            "information technology",
            "software engineering",
            "computer engineering"
        ],

        "information technology": [
            "information technology",
            "computer science",
            "software engineering"
        ],

        "software engineering": [
            "software engineering",
            "computer science",
            "information technology"
        ],

        "engineering": [
            "engineering",
            "computer science",
            "information technology"
        ],

        "data science": [
            "data science",
            "computer science",
            "statistics",
            "mathematics"
        ],

        "artificial intelligence": [
            "artificial intelligence",
            "computer science",
            "machine learning",
            "data science"
        ],

        "machine learning": [
            "machine learning",
            "artificial intelligence",
            "computer science",
            "data science"
        ]
    }

    for group, related in education_groups.items():

        if group in student_education:

            for item in related:

                if item in internship_education:
                    return 80

    return 50


# ============================================================
# OVERALL MATCH SCORE
# ============================================================

def calculate_overall_match(
    student,
    internship
):
    """
    Calculate final internship recommendation score.

    Skills       = 40%
    Domain       = 25%
    Work Mode    = 15%
    Location     = 10%
    Education    = 10%
    """

    student_domain = student.get(
        "domain",
        ""
    )

    student_skills = student.get(
        "skills",
        []
    )

    student_mode = student.get(
        "work_mode",
        student.get("mode", "")
    )

    student_location = student.get(
        "location",
        ""
    )

    student_education = student.get(
        "education",
        ""
    )

    internship_domain = internship.get(
        "domain",
        internship.get(
            "category",
            internship.get("field", "")
        )
    )

    internship_skills = internship.get(
        "skills",
        internship.get(
            "required_skills",
            []
        )
    )

    internship_modes = internship.get(
        "work_mode",
        internship.get(
            "work_modes",
            internship.get(
                "mode",
                []
            )
        )
    )

    internship_locations = internship.get(
        "locations",
        internship.get(
            "location",
            internship.get(
                "city",
                []
            )
        )
    )

    internship_education = internship.get(
        "education",
        internship.get(
            "qualification",
            internship.get(
                "eligibility",
                ""
            )
        )
    )

    # --------------------------------------------------------
    # DOMAIN SCORE
    # --------------------------------------------------------

    domain_score = calculate_domain_match(
        student_domain,
        internship_domain
    )

    # --------------------------------------------------------
    # SKILL SCORE
    # --------------------------------------------------------

    skill_result = calculate_skill_match(
        student_skills,
        internship_skills
    )

    # Your existing function returns:
    # score, matched, missing

    if isinstance(skill_result, tuple):

        skill_score = skill_result[0]

        matched_skills = skill_result[1]

        missing_skills = skill_result[2]

    else:

        skill_score = skill_result

        matched_skills = []

        missing_skills = []

    # --------------------------------------------------------
    # WORK MODE SCORE
    # --------------------------------------------------------

    work_mode_score = calculate_work_mode_match(
        student_mode,
        internship_modes
    )

    # --------------------------------------------------------
    # LOCATION SCORE
    # --------------------------------------------------------

    location_score = calculate_location_match(
        student_location,
        internship_locations
    )

    # --------------------------------------------------------
    # EDUCATION SCORE
    # --------------------------------------------------------

    education_score = calculate_education_match(
        student_education,
        internship_education
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    final_score = (
        skill_score * 0.40
        + domain_score * 0.25
        + work_mode_score * 0.15
        + location_score * 0.10
        + education_score * 0.10
    )

    return {
        "score": round(final_score),

        "skill_score": round(skill_score),

        "domain_score": round(domain_score),

        "work_mode_score": round(
            work_mode_score
        ),

        "location_score": round(
            location_score
        ),

        "education_score": round(
            education_score
        ),

        "matched_skills": matched_skills,

        "missing_skills": missing_skills
    }


# ============================================================
# RECOMMENDATION GENERATOR
# ============================================================

def generate_recommendations(
    student,
    internships,
    limit=10
):
    """
    Generate ranked internship recommendations.
    """

    recommendations = []

    for internship in internships:

        try:

            result = calculate_overall_match(
                student,
                internship
            )

            recommendation = internship.copy()

            recommendation["match_score"] = (
                result["score"]
            )

            recommendation["skill_score"] = (
                result["skill_score"]
            )

            recommendation["domain_score"] = (
                result["domain_score"]
            )

            recommendation["work_mode_score"] = (
                result["work_mode_score"]
            )

            recommendation["location_score"] = (
                result["location_score"]
            )

            recommendation["education_score"] = (
                result["education_score"]
            )

            recommendation["matched_skills"] = (
                result["matched_skills"]
            )

            recommendation["missing_skills"] = (
                result["missing_skills"]
            )

            recommendations.append(
                recommendation
            )

        except Exception as error:

            print(
                "Recommendation error:",
                error
            )

    # Highest match first
    recommendations.sort

def calculate_location_match(student_location, internship_locations):

    student_location = normalize(student_location)

    internship_locations = [
        normalize(location)
        for location in convert_to_list(internship_locations)
    ]

    if not student_location or not internship_locations:
        return 50

    # India / nationwide opportunity
    for location in internship_locations:

        if location in [
            "india",
            "pan india",
            "pan-india",
            "all india",
            "nationwide",
            "remote"
        ]:
            return 100

    if student_location in internship_locations:
        return 100

    for location in internship_locations:

        if (
            student_location in location
            or location in student_location
        ):
            return 80

    return 30


# =========================================================
# ELIGIBILITY
# =========================================================

def check_basic_eligibility(student, internship):

    reasons = []
    warnings = []

    eligible = True

    # -----------------------------------------------------
    # CGPA
    # -----------------------------------------------------

    student_cgpa = student.get("cgpa", "")

    try:
        student_cgpa = float(student_cgpa)
    except (ValueError, TypeError):
        student_cgpa = 0

    minimum_cgpa = internship.get("minimum_cgpa", 0)

    try:
        minimum_cgpa = float(minimum_cgpa)
    except (ValueError, TypeError):
        minimum_cgpa = 0

    if student_cgpa >= minimum_cgpa:

        reasons.append(
            f"CGPA meets the minimum requirement of {minimum_cgpa}"
        )

    else:

        eligible = False

        warnings.append(
            f"Minimum CGPA required: {minimum_cgpa}"
        )

    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    required_education = convert_to_list(
        internship.get("education", [])
    )

    student_education = normalize(
        student.get("education", "")
    )

    if required_education:

        education_match = False

        for education in required_education:

            education = normalize(education)

            if (
                education in student_education
                or student_education in education
            ):
                education_match = True
                break

        if education_match:

            reasons.append("Your education level is compatible.")

        else:

            eligible = False

            warnings.append(
                "Your education level may not satisfy the requirement."
            )

    # -----------------------------------------------------
    # BRANCH
    # -----------------------------------------------------

    required_branches = convert_to_list(
        internship.get("branches", [])
    )

    student_branch = normalize(
        student.get("branch", "")
    )

    if required_branches:

        branch_match = False

        for branch in required_branches:

            branch = normalize(branch)

            if (
                branch in student_branch
                or student_branch in branch
            ):
                branch_match = True
                break

        if branch_match:

            reasons.append("Your academic branch matches.")

        else:

            eligible = False

            warnings.append(
                "Your academic branch may not match the requirement."
            )

    return eligible, reasons, warnings


# =========================================================
# MAIN RECOMMENDATION ENGINE
# =========================================================

def recommend_internships(student, internships):

    recommendations = []

    for internship in internships:

        # -------------------------------------------------
        # ONLY VERIFIED RECORDS
        # -------------------------------------------------

        if not internship.get("verified", False):
            continue

        # -------------------------------------------------
        # ELIGIBILITY
        # -------------------------------------------------

        eligible, eligibility_reasons, warnings = (
            check_basic_eligibility(
                student,
                internship
            )
        )

        # -------------------------------------------------
        # DOMAIN
        # -------------------------------------------------

        domain_score = calculate_domain_match(
            student.get("domain", ""),
            internship.get("domains", [])
        )

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        skill_score, matched_skills, missing_skills = (
            calculate_skill_match(
                student.get("skills", []),
                internship.get("skills", [])
            )
        )

        # -------------------------------------------------
        # WORK MODE
        # -------------------------------------------------

        work_mode_score = calculate_work_mode_match(
            student.get("work_mode", ""),
            internship.get("work_modes", [])
        )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        location_score = calculate_location_match(
            student.get("location", ""),
            internship.get("locations", [])
        )

        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        student_experience = normalize(
            student.get("experience", "")
        )

        internship_experience = normalize(
            internship.get("experience_level", "")
        )

        if not internship_experience:

            experience_score = 70

        elif internship_experience in [
            "beginner",
            "entry level",
            "entry-level"
        ]:

            if student_experience in [
                "",
                "none",
                "no experience",
                "beginner",
                "fresher"
            ]:
                experience_score = 100
            else:
                experience_score = 90

        elif internship_experience == student_experience:

            experience_score = 100

        else:

            experience_score = 50

        # -------------------------------------------------
        # FINAL WEIGHTED SCORE
        # -------------------------------------------------

        score = (
            domain_score * 0.30
            + skill_score * 0.35
            + work_mode_score * 0.10
            + location_score * 0.10
            + experience_score * 0.05
            + (100 if eligible else 0) * 0.10
        )

        score = round(
            max(0, min(100, score))
        )

        # -------------------------------------------------
        # EXPLANATION
        # -------------------------------------------------

        reasons = []

        if domain_score >= 100:

            reasons.append(
                "Your preferred domain directly matches this internship."
            )

        elif domain_score >= 60:

            reasons.append(
                "Your preferred domain is related to this internship."
            )

        if matched_skills:

            reasons.append(
                "Matching skills: "
                + ", ".join(matched_skills[:5])
            )

        if work_mode_score >= 80:

            reasons.append(
                "Your preferred work mode matches."
            )

        if location_score >= 80:

            reasons.append(
                "Location preference is compatible."
            )

        reasons.extend(
            eligibility_reasons
        )

        if missing_skills:

            reasons.append(
                "Skills you may want to learn: "
                + ", ".join(missing_skills[:5])
            )

        # -------------------------------------------------
        # RESULT OBJECT
        # -------------------------------------------------

        result = {
            "id": internship.get(
                "id",
                "INTERNSHIP"
            ),

            "title": internship.get(
                "title",
                "Internship Opportunity"
            ),

            "organization": internship.get(
                "organization",
                internship.get(
                    "company",
                    "Organization"
                )
            ),

            "description": internship.get(
                "description",
                ""
            ),

            "domains": internship.get(
                "domains",
                []
            ),

            "skills": internship.get(
                "skills",
                []
            ),

            "locations": internship.get(
                "locations",
                ["India"]
            ),

            "work_modes": internship.get(
                "work_modes",
                []
            ),

            "duration": internship.get(
                "duration",
                "Varies by listing"
            ),

            "stipend": internship.get(
                "stipend",
                "Varies by listing"
            ),

            "deadline": internship.get(
                "deadline",
                "Check official source"
            ),

            "eligibility": internship.get(
                "eligibility",
                []
            ),

            "documents": internship.get(
                "documents",
                []
            ),

            "source_name": internship.get(
                "source_name",
                "Official Source"
            ),

            "source_url": internship.get(
                "source_url",
                "#"
            ),

            "application_url": internship.get(
                "application_url",
                internship.get(
                    "source_url",
                    "#"
                )
            ),

            "verified": internship.get(
                "verified",
                False
            ),

            "verified_by": internship.get(
                "verified_by",
                ""
            ),

            "last_verified": internship.get(
                "last_verified",
                ""
            ),

            "match": score,

            "eligible": eligible,

            "reasons": reasons,

            "warnings": warnings,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "domain_score": domain_score,

            "skill_score": skill_score,

            "work_mode_score": work_mode_score,

            "location_score": location_score,

            "experience_score": experience_score
        }

        recommendations.append(result)

    # -----------------------------------------------------
    # SORT RESULTS
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item["eligible"],
            item["match"]
        ),
        reverse=True
    )

    return recommendations


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# INTERNSHIPS PAGE
# =========================================================

@app.route("/internships")
def internships():

    all_internships = load_internships()

    # Only verified records
    verified_internships = [
        item
        for item in all_internships
        if item.get("verified", False)
    ]

    return render_template(
        "internships.html",
        internships=verified_internships
    )


# =========================================================
# PROFILE PAGE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        # ---------------------------------------------
        # BASIC INFORMATION
        # ---------------------------------------------

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        education = request.form.get(
            "education",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        cgpa = request.form.get(
            "cgpa",
            ""
        ).strip()

        # ---------------------------------------------
        # SKILLS
        # ---------------------------------------------

        skills_text = request.form.get(
            "skills",
            ""
        ).strip()

        skills = [
            skill.strip()
            for skill in re.split(
                r"[,;\n]",
                skills_text
            )
            if skill.strip()
        ]

        # ---------------------------------------------
        # DOMAIN
        # ---------------------------------------------

        domain = request.form.get(
            "domain",
            ""
        ).strip()

        # ---------------------------------------------
        # LOCATION
        # ---------------------------------------------

        location = request.form.get(
            "location",
            ""
        ).strip()

        # ---------------------------------------------
        # WORK MODE
        # ---------------------------------------------

        work_mode = request.form.get(
            "work_mode",
            ""
        ).strip()

        # ---------------------------------------------
        # EXPERIENCE
        # ---------------------------------------------

        experience = request.form.get(
            "experience",
            ""
        ).strip()

        # ---------------------------------------------
        # SAVE PROFILE IN SESSION
        # ---------------------------------------------

        student = {
            "name": name,
            "email": email,
            "education": education,
            "branch": branch,
            "cgpa": cgpa,
            "skills": skills,
            "domain": domain,
            "location": location,
            "work_mode": work_mode,
            "experience": experience
        }

        session["student"] = student

        # Go to recommendations
        return redirect(
            url_for("recommendations")
        )

    # GET request
    return render_template(
        "profile.html"
    )


# =========================================================
# RECOMMENDATIONS PAGE
# =========================================================

@app.route("/recommendations")
def recommendations():

    student = session.get(
        "student"
    )

    if not student:

        return redirect(
            url_for("profile")
        )

    internships = load_internships()

    results = recommend_internships(
        student,
        internships
    )

    return render_template(
        "recommendations.html",
        recommendations=results,
        student=student
    )


# =========================================================
# API - ALL INTERNSHIPS
# =========================================================

@app.route("/api/internships")
def api_internships():

    internships = load_internships()

    verified = [
        item
        for item in internships
        if item.get("verified", False)
    ]

    return jsonify({
        "success": True,
        "count": len(verified),
        "internships": verified
    })


# =========================================================
# API - RECOMMENDATIONS
# =========================================================

@app.route(
    "/api/recommend",
    methods=["POST"]
)
def api_recommend():

    try:

        student = request.get_json()

        if not student:

            return jsonify({
                "success": False,
                "error": "No student profile provided."
            }), 400

        internships = load_internships()

        results = recommend_internships(
            student,
            internships
        )

        return jsonify({
            "success": True,
            "count": len(results),
            "recommendations": results
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# =========================================================
# RESET PROFILE
# =========================================================

@app.route("/reset")
def reset():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    internships = load_internships()

    return jsonify({
        "status": "running",
        "application": "InternMatch AI",
        "verified_internships": len([
            item
            for item in internships
            if item.get("verified", False)
        ]),
        "timestamp": datetime.now().isoformat()
    })


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return """
    <h1>InternMatch AI - Server Error</h1>
    <p>Something went wrong on the server.</p>
    <p>Please check the VS Code terminal for the error.</p>
    """, 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("        INTERNMATCH AI")
    print("        AI Internship Recommendation System")
    print("=" * 60)

    print()
    print("Data file:")
    print(DATA_FILE)

    internships = load_internships()

    verified_count = len([
        item
        for item in internships
        if item.get("verified", False)
    ])

    print(
        f"Loaded internships: {len(internships)}"
    )

    print(
        f"Verified internships: {verified_count}"
    )

    print()
    print("Server starting...")
    print("Open: http://127.0.0.1:5000")
    print("=" * 60)
   


# ============================================================
# RECOMMENDATIONS PAGE
# ============================================================





# ============================================================
# START SERVER
# ============================================================

app.run(
    host="127.0.0.1",
    port=5000,
    debug=True
)