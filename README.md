# 🚀 Internova

### *The Intelligent, AI-Powered Career Accelerator & Resume Ecosystem*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-PythonAnywhere-blue?style=for-the-badge&logo=python&logoColor=white)](https://mantrabareda.pythonanywhere.com/internova/)
[![Tech Stack](https://img.shields.io/badge/Stack-Flask%20%7C%20Gemini%20%7C%20SQLite-orange?style=for-the-badge)](#-tech-stack)

Internova is an all-in-one, end-to-end career intelligence platform designed to bridge the gap between academic preparation and industry landing. By leveraging contextual AI models, Internova parses, audits, and rates developer resumes, builds dynamic learning roadmaps, assesses future automation risks, and acts as an automated internship gatekeeper based on candidate readiness.

---

## 🔒 Note on Source Code

> [!IMPORTANT]
> **The source code for Internova is kept strictly PRIVATE and SECRET due to proprietary prompt structures, system architecture rules, and intellectual property constraints.** 
> 
> However, a fully functional production build is live and available for evaluation. You can test the end-to-end user workflow, upload sample resumes, and interact with the AI features here:
> 👉 **[Launch Live Application](https://mantrabareda.pythonanywhere.com/internova/)**

---

## 🖼️ Application Preview

[Insert Project Hero Banner or Animated GIF Here - e.g., assets/dashboard-preview.png]


---

## ✨ Core Features

*   **📄 AI-Driven Resume Audit & Scoring:** Upload limits enforce clean processing before feeding data to custom, structured system prompts that rate formatting, layout, impact, and modern keyword alignment.
*   **🗺️ Interactive AI Roadmaps & Adaptive Chat:** Generates a custom career pathway mapped to the user's current skill gaps. Chat history and contextual roadmaps persist across sessions.
*   **⚠️ Career AI-Risk Alignment:** A predictive tool that evaluates specific target sectors (Tech, Finance, Medical) and explicitly breaks down future automation risks alongside longevity forecasts.
*   **🎯 Intelligent Internship Finder (Gatekeeper Logic):** 
    *   *If Ready:* Evaluates current education levels (e.g., Student vs. B.Tech graduate) and leverages web-enabled AI to scrape, sort, and filter live internships tailored to their tier.
    *   *If Not Ready:* Dynamically blocks access, flags technical deficiencies, and enforces resume revision before allowing internship matching.
*   **🗣️ Multi-Genre Interview Prep Sandbox:** Generates dynamic Q&A pairs tailored across explicit categories: *Technical*, *Behavioral*, and *General Situational* interview sets.

---

## 🛠️ Tech Stack

### Backend Architecture
*   **Core Framework:** Python / Flask (Lightweight, robust routing, and secure upload streaming)
*   **Database Engine:** SQLite (Relational state tracking for persistent chat, roadmaps, and profile states)
*   **AI Orchestration:** Google Gemini API (Web-enabled grounding, text parsing, and complex reasoning)

### Frontend Showcase
*   **UI/UX:** Vanilla JavaScript (ES6+), Semantic HTML5, and Modern CSS3 (Zero heavy client-side frameworks for hyper-fast Initial Page Loads).

---

## 📐 System Architecture & Workflow

```text
       [User Resume Upload]
                 │
                 ▼
      [Flask File Validation]
                 │
                 ▼
     [Gemini API Parse & Grade]
                 │
        ┌────────┴────────┐
        ▼                 ▼
   [Score < 70%]     [Score ≥ 70%]
        │                 │
        ▼                 ▼
  Internship Locked  Internship Unlocked
        │                 │
        ▼                 ▼
 [Weakness Report]   [Scrape & Filter]
 [& AI Roadmaps  ]   [Tiered Openings]---

## 🧠 Technical Challenges & Engineering Solutions

### 1. Deterministic JSON Outputs from Non-Deterministic AI Model
*   **The Problem:** Gemini's raw completions would occasionally return conversational text wrappers, breaking the Flask backend JSON parser.
*   **The Solution:** Engineered strict system prompts enforcing structured JSON typography. Implemented aggressive server-side validation blocks that catch malformed strings and automatically fall back safely, guaranteeing a deterministic data pipeline into the SQLite database.

### 2. Mitigating Gemini API Timeouts via File Pre-filtering
*   **The Problem:** Processing large, image-heavy, or unoptimized document uploads routinely caused API timeouts and dropped server connections.
*   **The Solution:** Integrated strict client-side and server-size size validation layers directly into Flask. Pre-filtering the raw file parameters ensured maximum payload optimization, keeping response latencies within predictable bounds.

### 3. Session State & Context Persistence over Stateless HTTP
*   **The Problem:** Maintaining deep user state (historical career suggestions, chat context, and locked/unlocked feature configurations) across page reloads without bloated cookie architecture.
*   **The Solution:** Designed a lightweight relational schema using SQLite to cache real-time AI states, pairing them against explicit session tokens. This ensures users can exit their dashboard and pick up exactly where their career roadmap left off.

---

---

## 📸 Core Modules in Action

Below are visual previews of Internova's primary functional areas. *Ensure you have uploaded `dashboard.png`, `resume-analyzer.png`, and `ai-roadmap.png` into your root `/assets` folder.*

<p align="center">
  <img src="assets/dashboard.png" alt="Internova Application Dashboard - Overview" width="90%" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <br>
  <em>Figure 1: The centralized Internova dashboard, providing quick access to all career acceleration modules.</em>
</p>

<p align="center">
  <img src="assets/resume-analyzer.png" alt="Internova AI Resume Analyzer Interface" width="90%" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <br>
  <em>Figure 2: The Resume Audit interface, showcasing AI scoring and critical formatting feedback.</em>
</p>

<p align="center">
  <img src="assets/ai-roadmap.png" alt="Internova Interactive AI Career Roadmap" width="90%" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <br>
  <em>Figure 3: Dynamic AI-generated roadmap illustrating skill pathways and associated future automation risks.</em>
</p>

---
```
## 👤 Developer & Contact

*   **Developer:** Mantra Bareda
*   **Deployment Platform:** PythonAnywhere
*   **Live App:** [Internova Application](https://mantrabareda.pythonanywhere.com/internova/)

👤 Developer & Contact

  Developer: Mantra Bareda

  Deployment Platform: PythonAnywhere

  Live App: <a href="https://mantrabareda.pythonanywhere.com/internova">Internova Application</a>
