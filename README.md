This is a comprehensive, industry-standard `README.md`. It includes professional badges, a clear project structure, technical challenges (which recruiters and engineers love to read), and a solid roadmap.

Copy the content below and overwrite your current `README.md`.

***

# 🚀 LinkedIn Insights API

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)

**LinkedIn Insights API** is an intelligent market research tool that automates the extraction and analysis of company data. It goes beyond simple scraping by integrating **Generative AI** to provide strategic business insights, SWOT analysis, and engagement metrics instantly.

---

## 🏗️ Architecture & Tech Stack

This project uses a microservices-ready architecture containerized with Docker.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **API Framework** | **FastAPI** | High-performance, async Python web framework. |
| **Browser Automation** | **Selenium / Chrome** | Headless browser with anti-detection protocols. |
| **Database** | **MongoDB (Motor)** | NoSQL storage for flexible schema handling of scraped data. |
| **Caching** | **Redis** | High-speed caching to prevent redundant scraping and rate limits. |
| **AI Intelligence** | **LangChain + OpenAI** | Generates summaries and strategic insights using `gpt-4o-mini`. |
| **Containerization** | **Docker Compose** | Orchestrates API, Database, and Cache services. |
| **CI/CD** | **GitHub Actions** | Automated build and environment checks. |

---

## ⚡ Key Features

*   **🔍 Advanced Scraping Pipeline:** Extracts deep data including Company Details, Recent Posts (Likes/Comments), and Employee Profiles.
*   **🧠 AI Strategic Analysis:** automatically generates business insights (Market Positioning, Target Audience, Growth Indicators) using LLMs.
*   **🛡️ Anti-Bot Evasion:** Implements robust session management using cookie persistence, User-Agent matching, and human-mimicking scroll behavior.
*   **🚀 Performance Optimization:** Implements a "Cache-First" strategy using Redis to serve data instantly for repeated requests.
*   **🔄 Resilience:** Automatic retries for network failures and smart handling of LinkedIn Auth Walls.
*   **📂 Media Handling:** Downloads and stores company profile images locally/containerized.

---

## 🔧 Engineering Challenges & Solutions

Building a stable LinkedIn scraper requires overcoming significant hurdles. Here is how this project handles them:

### 1. The Auth Wall & CAPTCHA Deadlock
*   **Problem:** LinkedIn detects headless browsers and triggers CAPTCHAs or forces a login ("Auth Wall"), which cannot be solved inside a headless Docker container.
*   **Solution:** We implemented a **Session Injection System**. Users generate a valid session cookie locally (solving CAPTCHAs manually once), and the Docker container injects this "blessed" cookie to bypass login screens entirely.

### 2. Rate Limiting & Quotas
*   **Problem:** Frequent requests trigger IP bans, and AI APIs have strict daily quotas.
*   **Solution:**
    *   **Redis Caching:** Identical requests within 24 hours are served from cache, hitting 0 scraping endpoints.
    *   **Database Archival:** Data is saved to MongoDB. If cache expires, we check DB before scraping live.
    *   **Model Optimization:** Switched from unstable experimental models to robust `gpt-4o-mini` for consistent performance.

### 3. Dynamic DOM Elements
*   **Problem:** LinkedIn changes CSS class names dynamically (e.g., specific React classes) causing scrapers to break.
*   **Solution:** The scraper uses **Heuristic Selectors** (searching for text patterns like "Followers" or "Industry") rather than relying solely on brittle CSS classes.

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   A valid OpenAI API Key
*   A LinkedIn Account

### 1. Clone & Configure
```bash
git clone https://github.com/yourusername/linkedin-insights-api.git
cd linkedin-insights-api

# Create env file from template
cp .env.example .env
```

**Edit your `.env` file:**
```ini
OPENAI_API_KEY=sk-proj-xxxx...
GEMINI_MODEL=gemini-1.5-flash  # (Legacy/Backup)
HEADLESS_MODE=True
```

### 2. Session Setup (Crucial Step)
To bypass the login screen inside Docker:
1.  Run the local helper script on your machine: `python get_cookies.py`
2.  Log in to LinkedIn manually in the window that opens.
3.  The script will save `linkedin_cookies.pkl`.
4.  Move this file to: `data/uploads/linkedin_cookies.pkl`

### 3. Run with Docker 🐳 (Recommended)
```bash
docker-compose up -d --build
```
This starts the API, MongoDB, and Redis.

### 4. Explore the API
Open your browser to the auto-generated Swagger documentation:
👉 **http://localhost:8000/docs**

---

## 📡 API Endpoints

### 1. Get Page Details
Scrapes data or retrieves from cache.
```http
GET /api/v1/pages/{company_name}?force_refresh=false
```

### 2. Get AI Insights
Generates a strategic summary using OpenAI.
```http
GET /api/v1/pages/{company_name}/ai-summary
```

### 3. Get Posts
Retrieves a paginated list of recent company updates.
```http
GET /api/v1/pages/{company_name}/posts
```

---

## 🗺️ Future Roadmap

*   [ ] **Proxy Rotation:** Integrate IP rotation (BrightData/Smartproxy) to scale scraping volume.
*   [ ] **Dashboard UI:** Build a Next.js frontend to visualize the data and AI charts.
*   [ ] **Sentiment Analysis:** Use NLP to analyze comments on posts to determine brand sentiment.
*   [ ] **Export Engine:** Generate PDF/CSV reports for stakeholders.
*   [ ] **Celery Workers:** Move scraping tasks to a background queue for better API response times.

---

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.
