# ManageBac Analytics

An unofficial Python client for [ManageBac](https://managebac.com) — the IB school management platform — built by reverse-engineering the web interface, since no public API exists. Includes an attendance automation module and an NLP-powered sentiment analysis tool for class discussions.

---

## The Problem

ManageBac is the primary platform used by IB schools worldwide for managing classes, attendance, and student communications. Despite holding large amounts of structured data, it exposes no public API. Every interaction — checking attendance, reading notifications, fetching discussion posts — is locked behind a session-authenticated web interface with CSRF-protected forms.

This project solves that by building a fully programmatic Python client that handles authentication, session management, and data extraction, enabling automation and analysis that the platform itself does not support.

---

## Features

- **CSRF-token authentication** — extracts the hidden CSRF token from the login form server response and submits it with credentials to establish a persistent authenticated session
- **Session management** — reuses a single `requests.Session` across all requests, maintaining cookies and authentication state
- **Notification fetching** — extracts the bearer token embedded in the dashboard page and uses it to query ManageBac's internal notification API
- **Class discussion scraping** — parses discussion thread pages with BeautifulSoup to extract the body text of each post
- **Attendance read** — scrapes the attendance marks page to retrieve per-student status, period, and attendance record IDs
- **Attendance write** — submits attendance updates via authenticated PUT requests with CSRF headers, supporting both new records and updates to existing ones
- **Sentiment analysis** — runs TextBlob NLP on class discussion messages to score engagement as positive, neutral, or negative per class
- **Matplotlib visualisation** — renders a bar chart comparing average sentiment polarity across all analysed classes

---

## Tech Stack

- **Language:** Python 3
- **HTTP:** `requests` with session-based cookie management
- **Scraping:** `BeautifulSoup4`
- **NLP:** `TextBlob`
- **Visualisation:** `matplotlib`
- **Config:** environment variables or plaintext (configurable)

---

## Project Structure

```
managebac-analytics/
├── managebac.py               # Core ManageBac client — auth, scraping, attendance read/write
├── attendance.py              # Automated attendance polling loop — marks unmarked students present
├── sentiment.py               # NLP utilities — text cleaning and TextBlob sentiment classification
└── class_sentiment_analysis.py # Runs sentiment analysis across class discussions and plots results
```

---

## How It Works

### Authentication
1. `GET /sessions` — fetches the login page and extracts the hidden `authenticity_token` CSRF field
2. `POST /sessions` — submits credentials and CSRF token; session cookie is stored automatically by `requests.Session`
3. Login is verified by checking whether the response still contains `"Login</title>"` — if so, credentials were rejected

### Attendance Automation (`attendance.py`)
1. Polls each configured class on a fixed interval (default: every 5 minutes)
2. For each class, fetches the attendance marks page and extracts per-student records
3. For any student with `status == None` (not yet marked), submits a PUT request to mark them present
4. CSRF token is fetched fresh from the page meta tag before each write operation

### Sentiment Analysis (`class_sentiment_analysis.py`)
1. Authenticates and fetches all discussion posts for each configured class
2. Each message is cleaned (URLs, special characters stripped) and scored with TextBlob's polarity metric
3. Per-class average polarity is computed and plotted as a bar chart

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/candtk/managebac-analytics.git
cd managebac-analytics
```

**2. Install dependencies**
```bash
pip install requests beautifulsoup4 textblob matplotlib
python -m textblob.download_corpora
```

**3. Configure `attendance.py`**

Set your institution's subdomain, class IDs, and credentials:
```python
USEENVVARIABLES = True   # Recommended
DOMAINPREFIX = "yourschool"
classes = [YOUR_CLASS_ID]
```

With environment variables:
```bash
export EMAIL="your@email.com"
export PASSWORD="yourpassword"
python attendance.py
```

**4. Run sentiment analysis**
```bash
python class_sentiment_analysis.py
```

---

## License

MIT
