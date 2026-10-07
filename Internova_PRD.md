# Product Requirements Document (PRD): Internova

## 1. Product Overview
**Internova** is an AI-powered career counseling and recruitment readiness platform designed to help candidates optimize their resumes, prepare for interviews, and find relevant internships. By leveraging advanced generative AI (Google Gemini and Groq), Internova acts as a virtual career counselor, providing personalized feedback, actionable roadmaps, and mock interview simulations based on a user's resume and profile.

## 2. Target Audience
- **Students & Recent Graduates:** Seeking their first internships or entry-level roles, needing guidance on resume building and skill development.
- **Early-Career Professionals:** Looking to pivot careers or upskill and needing objective feedback on their market readiness.
- **Job Seekers:** Anyone looking to improve their resume, practice interviewing, and align their skills with market demands.

## 3. Core Value Proposition
Internova bridges the gap between raw candidate potential and market expectations by providing instant, brutal, yet constructive AI-driven feedback. It goes beyond simple spell-checkers to offer deep career alignment, personalized upskilling roadmaps, and realistic interview practice, saving users time and increasing their chances of getting hired.

## 4. Key Features (Functional Requirements)

### 4.1. User Management & Authentication
- **Authentication:** Secure login and registration using Google Sign-In (via Firebase Auth) or standard email/password (future-proofing).
- **User Profiles:** Users can maintain a detailed profile including First/Last Name, Headline, Bio, Skills, Education, Experience, LinkedIn, GitHub, and Portfolio URLs.
- **Credit System:** 
  - Users start with a default balance of credits (e.g., 10).
  - Generating initial resume analysis costs 1 credit.
  - Generating advanced bundles (Internships, Interview Prep, Career Alignment) costs 1 credit.
  - Prevents abuse of the AI API.

### 4.2. Resume Management & Parsing
- **Upload:** Users can upload resumes in `.pdf` and `.docx` formats.
- **Text Extraction:** The system accurately extracts raw text from uploaded files using `PyPDF2` and `python-docx` for AI processing.
- **Versioning:** Users can upload new versions of an existing resume to track progress and improvements over time.
- **History:** Dashboard displays all uploaded resumes and their historical versions with corresponding AI skill scores.

### 4.3. AI Career Dashboard (Resume Analysis)
- **Initial Analysis:** Upon upload, the AI generates a comprehensive dashboard:
  - **Actionable Roadmap:** A 3-step immediate action plan.
  - **Skill Score:** An integer score (0-100) indicating market readiness based on extracted skills.
  - **Skills to Improve:** Specific missing or weak skills along with 2-3 real learning URLs (e.g., YouTube, freeCodeCamp).
  - **Portfolio Design Rating & Suggestions:** Visual/structural feedback on the resume/portfolio with tool suggestions (e.g., Canva, Novoresume).
  - **"Why Not Hired" Report:** A blunt, constructive 2-paragraph analysis identifying major profile gaps.
- **Version Comparison:** When a user uploads a new version, the AI (using fallback models via Groq) compares the new resume against the old one and the previous AI advice to measure if feedback was successfully applied, outputting a score change (e.g., "+15").

### 4.4. Advanced AI Content Generation (The "Bundle")
Users can unlock advanced insights for a specific resume, which generates multiple modules at once:
- **Internship Finder:**
  - Recommends 3-5 suitable internship roles or company types based on the user's skill level.
  - Evaluates "Overall Readiness" (Ready for internship boolean).
  - Suggests preparatory courses for each recommended internship.
- **Mock Interview Prep (Static & Interactive):**
  - **Static Questions:** Generates 5 mock interview questions tailored to specific categories (General, Technical, Behavioral). Includes difficulty, hints, sample answers, and what the interviewer is evaluating.
  - **Interactive Chat (Virtual Manager 'Alex'):** A chat interface simulating a demanding engineering manager who conducts a 1-on-1 interview, pushing back on vague answers.
- **Career Alignment Insights:**
  - **Recommended Paths:** Suggests 3 specific roles with match percentages and reasoning.
  - **AI Vulnerability:** Assesses the risk of the user's desired career being automated by AI, providing a risk score and future-proofing advice.
  - **Market Scope:** Analyzes current hiring demand and growth trajectories for the user's skillset.
- **AI Roadmap Generator:**
  - Proposes 3 possible career paths.
  - **Interactive Roadmap Chat:** Users can chat with an "AI Advisor" about their career trajectory.
  - **Specific HTML Roadmap:** Generates a detailed, step-by-step HTML roadmap for a user-selected career option.

### 4.5. Admin Dashboard
- **Access Control:** Restricted to users matching the `ADMIN_EMAIL` environment variable.
- **User Management:** View all registered users in the system.
- **Credit Management:** Manually update/add credits for specific users.

## 5. Non-Functional Requirements

### 5.1. Tech Stack
- **Backend:** Python 3, Flask framework.
- **Database:** SQLite (default for development/MVP) using SQLAlchemy ORM and Flask-Migrate for schema management.
- **AI/LLM Providers:**
  - Primary: Google Gemini (`gemini-3.1-flash-lite`) via `google-generativeai`.
  - Secondary/Fallback: Groq API (models like `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`) for specific tasks like version comparison.
- **Authentication:** Firebase Admin SDK for secure token verification.
- **Frontend:** HTML5, CSS, vanilla JavaScript, Jinja2 templating.
- **Document Parsing:** `PyPDF2` (PDFs), `python-docx` (Word documents).

### 5.2. Performance & Scalability
- **Asynchronous AI Calls:** AI generation can be slow; the system utilizes a credit system to throttle usage and bundles API calls where possible.
- **Database:** SQLite is suitable for MVP but should be migrated to PostgreSQL or MySQL for production scalability.

### 5.3. Security
- API endpoints are protected by session validation.
- Resume text is processed in-memory and not stored persistently as raw files on the server disk (only text is saved to DB).
- Firebase ID tokens are securely verified on the backend.

## 6. Future Roadmap (Coming Soon)
- **Virtual Office:** A planned feature to simulate a remote work environment or provide collaborative tools.
- **In-App Partner Internships:** Direct integration with partner companies to allow users to apply for internships directly through the Internova platform based on their AI readiness score.
