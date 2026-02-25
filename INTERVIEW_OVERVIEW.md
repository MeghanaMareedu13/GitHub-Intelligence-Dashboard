# 🎙️ GitHub Intelligence Dashboard — Interview-Ready Project Overview

---

## 1. The 30-Second Elevator Pitch
> "I built an **Enterprise-Grade GitHub Intelligence Dashboard** that consumes the GitHub REST API to analyze developer profiles and technical breadth. This project isn't just a simple UI; it's a demo of **Resilient Software Engineering**. It features a custom API client with exponential backoff for rate limiting, a deterministic 'Project Health' scoring model, and high-performance data transformation using Pandas. It perfectly illustrates how I handle external data integration at scale."

---

## 2. Technical Highlights
- **Resilient API Implementation**: built a custom wrapper for `requests` that handles **403 Forbidden (Rate Limit)** errors by dynamically calculating wait times based on API headers.
- **Advanced Data Aggregation**: Synthesized thousand-line JSON objects into high-density analytical DataFrames to power Streamlit visualizations.
- **Deterministic Modeling**: Created a 'Health scoring' algorithm that evaluates repo maturity based on stars, forks, and last-push frequency.

---

## 3. Design Decisions
- **Modularity (Separation of Concerns)**: I separated the API Client (Networking), the Processor (Logic), and the App (UI). This ensures that if the UI changes (e.g., from Streamlit to React), the core engine remains untouched.
- **Security-First**: Implemented `.env` support for Personal Access Tokens (PATs) to ensure sensitive credentials are never hardcoded.

---

## 4. Sample Interview Q&A

### Q: "How did you handle GitHub's API rate limits?"
> "I implemented a middleware layer in my API client. Every request checks the `X-RateLimit-Remaining` header. If it hits zero, the client automatically calculates the reset time and puts the process into a strategic sleep mode. This prevents 403 errors and ensures the system is a 'Good Citizen' in the API ecosystem."

### Q: "Why use a custom Processor class instead of doing data logic in the UI?"
> "Maintenance and Scalability. By decoupling the data transformation logic from Streamlit, I can easily write unit tests for my 'Health Score' calculations without needing to spin up a web server. It's the **Single Responsibility Principle** in action."

---

*Prepared for Meghana Mareedu | Day 13 of the 30-Day Recruiter Attraction Challenge*
