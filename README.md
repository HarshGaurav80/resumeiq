# ResumeIQ – AI Resume Analyzer

ResumeIQ lets you upload a resume (PDF or DOCX) and paste a job description. It then shows:

- an overall **match score** (0–100) and an **ATS compatibility score**
- the candidate's **details** pulled from the resume (name, email, phone, education, experience, projects, certifications)
- the **skills found** and the **skills missing** compared with the job description
- **section scores** (Skills, Experience, Education, Projects, Formatting)
- specific **suggestions**, including weak bullet points rewritten with action verbs
- a **PDF report** you can download, and a **history** of past analyses

The AI part uses **Google Gemini** (free tier) or **OpenAI**. If you don't set an API key, or the AI call fails,
ResumeIQ switches to an **offline analyzer**. That analyzer matches the resume against a built-in list of about 320
skills and scores how similar the resume is to the job description using **TF-IDF + cosine similarity**. So the app
works without an API key.

---

## Tech stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React 19, Vite, Tailwind CSS v4, shadcn/ui-style components, Framer Motion, Recharts, Sonner (toasts), react-dropzone, lucide-react |
| Backend    | Python FastAPI, Pydantic, httpx |
| Parsing    | pdfplumber (PDF), python-docx (DOCX) |
| AI         | Google Gemini API or OpenAI API (REST) |
| Fallback   | scikit-learn TF-IDF + cosine similarity, keyword matching, rule-based section parser |
| Database   | SQLite (Python's built-in `sqlite3`) |
| PDF report | ReportLab |

---

## Folder structure

```
resumeiq/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app and all API routes
│   │   ├── config.py             # settings from .env, list of job roles
│   │   ├── database.py           # SQLite history (create / list / get / delete)
│   │   ├── schemas.py            # Pydantic models that validate the AI's JSON
│   │   └── services/
│   │       ├── parser.py           # PDF / DOCX text extraction
│   │       ├── ai_analyzer.py      # Gemini / OpenAI prompt and JSON parsing
│   │       ├── fallback_analyzer.py# offline keyword + TF-IDF analyzer
│   │       ├── skills_db.py        # ~320 skills, aliases, role skills, action verbs
│   │       └── report.py           # PDF report generation
│   ├── data/                     # SQLite database file (created automatically)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui-style primitives (button, card, badge, table…)
│   │   │   ├── Navbar.jsx, Footer.jsx, Logo.jsx, ThemeProvider.jsx
│   │   │   ├── ScoreRing.jsx     # animated circular score meter
│   │   │   └── SectionChart.jsx  # Recharts bar chart
│   │   ├── pages/                # Landing, Analyze, Results, History, About, NotFound
│   │   ├── lib/                  # api.js (backend client), utils.js
│   │   ├── App.jsx, main.jsx, index.css
│   ├── vite.config.js            # dev proxy: /api -> http://127.0.0.1:8000
│   └── package.json
└── samples/                      # 2 demo resumes and 2 demo job descriptions
```

---

## Prerequisites

- **Python 3.9 or newer** (3.11+ recommended)
- **Node.js 20 or newer** with npm
- *(Optional)* a free Gemini API key from <https://aistudio.google.com/app/apikey>, or an OpenAI API key

---

## 1. Backend setup (FastAPI)

```bash
cd resumeiq/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

Open `.env` and add your key. You can skip this step to use the offline analyzer.

```bash
uvicorn app.main:app --reload --port 8000
```

- API: <http://localhost:8000>
- Interactive API docs (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/health>. It shows which AI provider is active (`gemini`, `openai` or `none`).

## 2. Frontend setup (React + Vite)

Open a second terminal:

```bash
cd resumeiq/frontend
npm install
npm run dev
```

Then open <http://localhost:5173>. During development, Vite forwards every `/api` request to the backend on port 8000,
so no extra setup is needed.

To build for production, run `npm run build`. The output goes to `frontend/dist/`. If the backend is hosted somewhere
else, set `VITE_API_URL` before building.

---

## Environment variables

### `backend/.env`

| Variable          | Default                          | Description |
|-------------------|----------------------------------|-------------|
| `AI_PROVIDER`     | `auto`                           | `auto` picks Gemini, then OpenAI, then offline, based on which keys are set. You can also force `gemini`, `openai` or `none`. |
| `GEMINI_API_KEY`  | *(empty)*                        | Google Gemini API key |
| `GEMINI_MODEL`    | `gemini-2.5-flash`               | Gemini model name |
| `OPENAI_API_KEY`  | *(empty)*                        | OpenAI API key |
| `OPENAI_MODEL`    | `gpt-4o-mini`                    | OpenAI model name |
| `AI_TIMEOUT`      | `60`                             | Seconds to wait for the AI before using the offline analyzer |
| `DATABASE_PATH`   | `data/resumeiq.db`               | Location of the SQLite file |
| `CORS_ORIGINS`    | `http://localhost:5173,...`      | Frontend addresses allowed to call the API |

### `frontend/.env` (optional)

| Variable       | Description |
|----------------|-------------|
| `VITE_API_URL` | Full backend URL, e.g. `https://api.example.com`. Leave it empty in development. |

> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## API endpoints

| Method | Endpoint                         | Description |
|--------|----------------------------------|-------------|
| GET    | `/api/health`                    | Status and active AI provider |
| GET    | `/api/roles`                     | Job roles for the dropdown |
| POST   | `/api/analyze`                   | `multipart/form-data`: `file` (PDF/DOCX ≤ 5 MB), `job_description`, `job_role` (optional) |
| GET    | `/api/history`                   | List of past analyses |
| GET    | `/api/history/{id}`              | Full result for one analysis |
| DELETE | `/api/history/{id}`              | Delete an analysis |
| GET    | `/api/history/{id}/report`       | Download the PDF report |

---

## How the analysis works

1. **Validation.** The backend accepts only `.pdf` and `.docx` files up to 5 MB. It checks the file's real
   signature, not only its extension, and requires a job description of at least 30 characters. The frontend runs
   the same checks before uploading.
2. **Text extraction.** `pdfplumber` reads PDFs. `python-docx` reads Word files, including text inside tables.
   Scanned image-only PDFs are rejected with a clear message.
3. **AI analysis.** The resume text and job description go to Gemini or OpenAI with a prompt that asks for strict
   JSON in this shape:
   ```json
   { "candidate": { "name": "", "email": "", "phone": "", "education": [], "experience": [], "projects": [], "certifications": [] },
     "match_score": 0, "ats_score": 0,
     "section_scores": { "skills": 0, "experience": 0, "education": 0, "projects": 0, "formatting": 0 },
     "skills_found": [], "missing_skills": [], "strengths": [], "suggestions": [], "summary": "" }
   ```
4. **Validation of the AI's answer.** The response is cleaned of markdown fences, parsed, and checked with
   Pydantic. Small mistakes are corrected: `"85"` becomes `85`, `0.82` becomes `82`, `120` is capped at `100`, a
   single string becomes a list, and duplicates are removed. An empty or invalid response counts as a failure.
5. **Offline fallback.** This runs when there is no API key or the AI fails. It:
   - finds skills in both texts with whole-word regex matching against `skills_db.py`, including aliases such as
     `ReactJS → React` and `k8s → Kubernetes`. Skills listed under *"Nice to have"* in the job description count half.
   - computes **TF-IDF cosine similarity** between the resume and the job description (word pairs included, English
     stop words removed).
   - scores each section with rules: are the headings present, do bullet points start with action verbs, are
     results quantified, are the degree and grades listed, are there project links, are the contact details
     complete, and is the length reasonable.
   - calculates the **match score** as 55% skill coverage, 30% TF-IDF similarity and 15% content quality.
   - calculates the **ATS score** as 45% formatting, 40% keyword coverage and 15% similarity.
   - writes suggestions, including weak bullets rewritten with action verbs
     (*"Worked on fixing bugs…" → "Fixed bugs…, resulting in [measurable result]"*).
6. **Storage.** Each result is saved in SQLite and shown on the dashboard. The PDF report is generated from the
   saved result when you download it.

---

## Sample data (for demos)

The `samples/` folder contains made-up demo data:

| File | Description |
|------|-------------|
| `resume_priya_sharma_data_analyst.pdf` | Strong data-analyst resume (PDF) |
| `resume_arjun_mehta_web_developer.docx` | Junior web-developer resume with weak bullet points (DOCX) |
| `jd_data_analyst.txt` | Entry-level Data Analyst job description |
| `jd_frontend_developer.txt` | Frontend Developer job description |

Suggested demo:

- **Priya + Data Analyst JD** gives a high score (about 75 with the offline analyzer).
- **Arjun + Frontend Developer JD** gives a low score, many missing skills, and the bullet-rewrite suggestions.
- **Priya + Frontend Developer JD** shows how much the score depends on the job description.

To recreate the sample resumes, run `python ../samples/generate_samples.py` from `backend/` with the virtualenv active.

---

## Deploying for free (public link)

**Simplest: one Render service.** The built website is kept in `backend/static/`, and the backend serves it, so
the Render service from step 2 below is the whole app: its `https://….onrender.com` address is the website.
After changing the frontend, run `npm run build:backend` in `frontend/` and push.

The steps below also cover hosting the website separately on Vercel, which is optional.

The backend goes on **Render** and the website on **Vercel**. Both have free plans and sign in with GitHub.

1. **Put the project on GitHub.** Create an empty repository on github.com, then push this `resumeiq/` folder to it.
2. **Backend on Render.**
   - On render.com, choose **New + → Blueprint** and pick the repository. Render reads `render.yaml` and creates
     the `resumeiq-api` web service.
   - Optional: in the service's **Environment** tab, paste your `GEMINI_API_KEY`.
   - When it's live, copy its address, e.g. `https://resumeiq-api.onrender.com`, and open `/api/health` on it to check.
3. **Website on Vercel.**
   - On vercel.com, choose **Add New → Project**, import the repository, and set **Root Directory** to `frontend`.
   - Under **Environment Variables**, add `VITE_API_URL` = the Render address from step 2 (no trailing `/`).
   - Set the **Project Name** to the name you want in the link, starting with `resumeiq` (for example
     `resumeiq-harsh` gives `https://resumeiq-harsh.vercel.app`). The backend only accepts sites whose name starts
     with `resumeiq`; to use another name, change `CORS_ORIGIN_REGEX` in Render.
   - Click **Deploy**.

Notes on the free plans:

- The Render backend sleeps after about 15 minutes without visitors. The first analysis after that can take
  30–60 seconds while it wakes. Open the site a minute before a demo.
- Render's free disk is temporary, so the **History** list resets whenever the backend restarts or redeploys.
- The hosted History page is public: anyone with the link can see every analysis. Use the sample resumes, not
  real personal resumes, on the public site.

## Customising for your submission

- **Team members and guide:** edit the `TEAM` and `GUIDE` constants at the top of `frontend/src/pages/About.jsx`.
- **Job roles:** edit `JOB_ROLES` in `backend/app/config.py` and `ROLE_SKILLS` in `backend/app/services/skills_db.py`.
- **Skills list:** add to `SKILL_CATEGORIES` and `ALIASES` in `skills_db.py`.
- **Brand colours:** change the CSS variables in `frontend/src/index.css`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot reach the ResumeIQ server" | Start the backend on port 8000 first. |
| Results say *Offline (Keyword + TF-IDF)* although you set a key | Restart `uvicorn` after editing `.env`, check `/api/health`, and read the backend terminal for the AI error. |
| "Very little text could be extracted" | The PDF is a scanned image. Export it again as a text-based PDF or DOCX. |
| `reportlab requires 3.10+` | Run `pip install -r requirements.txt` again. It installs a ReportLab version that supports Python 3.9. |
