# OpportunityMatch

**Personalized Student Opportunity Discovery & Skill-Gap Analysis Platform**

[![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## 1. Executive Summary & Vision

Students are bombarded with opportunities—internships, hackathons, research fellowships, competitions, and scholarships—across dozens of scattered portals, telegram channels, and bulletin boards. Identifying suitable opportunities manually is inefficient, stressful, and error-prone.

**OpportunityMatch** is an explainable, automated discovery platform that reverses this dynamic.

> ### "Don't Search for Opportunities. Let the System Search for You."

Instead of manual search and guesswork:
$$\text{Student Profile} \longrightarrow \text{Eligibility Gate} \longrightarrow \text{Weighted Matching} \longrightarrow \text{Ranked Results} \longrightarrow \text{Explainable Skill Gap}$$

The system operates strictly on a **No-Middleman Principle**: student matches are computed mathematically and transparently by the scoring engine, without relying on human counselors or coordinators.

---

## 2. Core Features & "WOW" Highlights

- 🎯 **Automatic Opportunity Matching:** Matches students against a curated opportunity database based on academic profile, technical competencies, and scheduling constraints.
- 📊 **100% Explainable Scoring Engine:** Every match score comes with a complete point-by-point breakdown and positive checkmarks (`✓`) explaining *why* it was recommended.
- 🧩 **Deterministic Skill-Gap Analysis:** Computes $(\text{Required Skills} - \text{Student Skills} = \text{Missing Skills})$ and provides an opportunity alignment readiness percentage.
- 📚 **"What Should I Learn Next?":** Analyzes all opportunities matching the student's branch/year and identifies the most frequently missing skill (e.g. *Git is required by 15 of your relevant opportunities*).
- ⏰ **Deadline Awareness:** Automatically accounts for active dates and displays closing deadlines in the student dashboard.
- 📈 **Opportunity Skill Demand Analytics:** Live aggregation of most requested technical skills across active opportunities currently stored on the platform.
- 📝 **Student Application Tracking:** Personal Kanban/tracker for students to manage the status of their applications (`Saved`, `Applied`, `Under Review`, `Selected`, `Rejected`, `Completed`).
- 🛡️ **Administrator Analytics:** Dedicated dashboard for monitoring registered students, opportunities, platform demand metrics, and CRUD operations.

---

## 3. Deterministic Matching Engine Architecture

The platform uses a deterministic, transparent, weighted rule-based scoring engine (no unexplainable black-box models):

```text
Component                     Weight      Details
─────────────────────────────────────────────────────────────────────────────
1. Eligibility Gate            30%        Hard gate: Branch, Year, CGPA, Deadline
2. Technical Skill Match       30%        Matched Required Skills / Total Required
3. Domain & Interest Match     20%        Overlap of Student Interests with Opportunity
4. Preference Alignment        10%        Mode (Online/Offline), Type, Duration, Location
5. Availability Schedule       10%        Immediate vs Flexible availability alignment
─────────────────────────────────────────────────────────────────────────────
TOTAL COMPATIBILITY           100%        0 to 100%
```

### Match Categories

- **90% – 100%:** Excellent Match (Emerald)
- **75% – 89%:** Strong Match (Teal)
- **60% – 74%:** Moderate Match (Blue)
- **40% – 59%:** Low Match (Amber)
- **Below 40%:** Poor Match (Rose / Ineligible)

### Explainable Match Output Example

```text
94% MATCH — Excellent Match

✓ Information Technology branch eligible
✓ 3rd year eligible
✓ CGPA requirement satisfied (8.00 >= 7.00)
✓ Python skill matched (Advanced)
✓ Django skill matched (Intermediate)
✓ SQL skill matched (Intermediate)
✓ AI & Machine Learning interests aligned
✓ Remote work mode preference matched

Missing Skills (Skill Gap):
⚠ Docker
⚠ Git
```

---

## 4. Tech Stack

- **Backend:** Python 3.13, Django 5.1 (ORM, Auth, Forms, Context Processors, Management Commands)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js
- **Database:** SQLite (Development) / PostgreSQL (Production) via `dj-database-url`
- **Static Asset Serving:** WhiteNoise 6.12 (CompressedManifestStaticFilesStorage)
- **Production Server:** Gunicorn (WSGI)
- **Deployment Target:** Heroku, Render, AWS, or any containerized Linux host

---

## 5. Project Directory Structure

```text
opportunitymatch/
│
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
├── .gitignore
├── .env.example
├── .env
│
├── opportunitymatch/        # Project Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py             # Landing Page View
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # Authentication & User Management
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── students/                # Student Profiles, Skills, Interests & Notifications
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   ├── context_processors.py
│   ├── tests.py
│   └── management/commands/seed_data.py
│
├── opportunities/           # Opportunity Catalog, Saved, and Tracking
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── matching/                # Deterministic Engine & Analytics
│   ├── models.py            # MatchResult
│   ├── eligibility.py       # Hard Gate Evaluation
│   ├── scoring.py           # Weighted Scoring Engine
│   ├── skill_gap.py         # Skill Gap & "What Should I Learn Next?"
│   ├── services.py          # Orchestration Service
│   └── tests.py
│
├── recommendations/         # Personalized Recommendations Hub
│   ├── urls.py
│   └── views.py
│
├── dashboard/               # Student & Admin Dashboards
│   ├── urls.py
│   └── views.py
│
├── templates/               # Responsive HTML Templates
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── students/
│   ├── opportunities/
│   ├── dashboard/
│   └── recommendations/
│
├── static/                  # Static CSS, JS, Assets
│   └── css/styles.css
│
└── media/                   # Uploaded User Files
```

---

## 6. Getting Started Locally

### Prerequisites

- Python 3.10+ (Tested on Python 3.13)
- Git

### 1. Clone & Enter Project Directory

```bash
git clone <repository-url>
cd "opportunitymatch"
```

### 2. Set Up Virtual Environment (Optional but recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` based on `.env.example`:

```bash
cp .env.example .env
```

Default local `.env`:
```ini
DEBUG=True
SECRET_KEY=django-insecure-opportunitymatch-dev-secret-key-12345
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Populate Realistic Seed Data

Populates the platform with **30+ Students**, **50+ Skills**, **30+ Interests**, and **40+ Opportunities** across all 9 categories:

```bash
python manage.py seed_data
```

### 7. Run Local Development Server

```bash
python manage.py runserver
```

Open your browser at: **`http://127.0.0.1:8000/`**

---

## 7. Demo Accounts

| Role | Username | Password | Profile Highlights |
| :--- | :--- | :--- | :--- |
| **Primary Demo Student** | `saikrishna` | `password123` | IT Branch, 3rd Year, CGPA 8.0, Python, Django, SQL, AI/ML |
| **Platform Administrator** | `admin` | `admin123` | Full access to Admin Analytics & Opportunity CRUD |
| **Additional Students** | `ananya_sharma`, `rohit_verma`, etc. | `password123` | 30+ pre-seeded student profiles |

---

## 8. College / Live Demonstration Script

1. **Visit Landing Page (`/`):**
   Showcase the hero section, live stats ($42+$ active opportunities, $50+$ skills), and the core USP: *"Don't Search for Opportunities. Let the System Search for You."*
2. **Sign In as Student (`/login`):**
   Log in with `saikrishna` / `password123`.
3. **Inspect Student Dashboard (`/dashboard`):**
   - Profile completion gauge ($85\%+$).
   - Instant display of **Top Matches** (e.g. 94% AI Research Internship).
   - "What Should I Learn Next?" card recommending **Git** and **Docker**.
4. **Open Opportunity Detail (`/opportunities/<id>`):**
   - Examine the **Why is this recommended?** section.
   - Review the **Component Score Breakdown**: Eligibility (30/30), Skills (27/30), Interests (20/20), Preferences (10/10), Availability (7/10).
   - Show missing skills: `Git`, `Docker`.
   - Read the readiness message: *"You are 60% aligned with this opportunity's skill requirements. Adding [Git, Docker] would improve your compatibility score under the platform's scoring model."*
5. **Explore Skill Gap Hub (`/skill-gaps`):**
   - Point out the **Opportunity Skill Demand Analytics** chart (e.g., Python required in 25 opportunities, SQL in 18, etc.).
   - Review the *"What Should I Learn Next?"* top recommendation based on student missing skills.
6. **Save & Apply (`/saved` & `/applications`):**
   - Click Save to bookmark the opportunity.
   - Click Apply to record application notes and track its status stage (`Under Review`, `Selected`).
7. **Sign In as Administrator (`/login`):**
   - Log in with `admin` / `admin123`.
   - View `/admin-dashboard`: interactive Chart.js charts for Skill Demand and Opportunity Type distribution.
   - Demonstrate CRUD: create or edit an opportunity and see real-time updates.

---

## 9. Automated Test Suite

Run the comprehensive test suite covering Authentication, Student Profiles, Skills, Opportunities CRUD, Access Permissions, Eligibility Gating, and Scoring:

```bash
python manage.py test
```

Result:
```text
Ran 14 tests in 18.854s
OK
```

---

## 10. Production Deployment (Heroku / Container)

### Key Production Assets Included:
- `Procfile`: `web: gunicorn opportunitymatch.wsgi --log-file -`
- `runtime.txt`: `python-3.13.2`
- `settings.py`: Automatically parses `DATABASE_URL` for PostgreSQL and serves assets with `WhiteNoise`.

### Deployment Steps:
1. Create Heroku app: `heroku create opportunitymatch-app`
2. Add PostgreSQL add-on: `heroku addons:create heroku-postgresql:essential-0`
3. Set environment variables:
   ```bash
   heroku config:set DEBUG=False SECRET_KEY="your-secure-production-key" ALLOWED_HOSTS=".herokuapp.com"
   ```
4. Push code: `git push heroku main`
5. Run migrations & seed data on production:
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py seed_data
   ```

---

## 11. Future Scope

- 🤖 **Machine Learning Recommendation Engine:** Train collaborative filtering / contextual bandit models on student application feedback, interview conversions, and interaction telemetry.
- 🔗 **Direct University LMS & ATS Integrations:** Webhook integrations with college placement portals and Greenhouse/Lever ATS for automatic application status synchronization.
- 📱 **Mobile Application:** Native Flutter mobile application utilizing the Django REST endpoints.

---

## 12. License

This project is licensed under the MIT License.
