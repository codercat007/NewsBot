# 📰 Indian Market News Summarizer

An autonomous Python bot that monitors Indian financial news RSS feeds, filters articles by topic, generates AI-powered summaries with sentiment scores, and delivers a digest straight to your inbox.

---

## ✨ Features

- 🔍 **Topic filtering** — only get articles relevant to stocks or companies you care about
- 🤖 **AI summarization** — merges all new articles and generates a concise digest using GPT
- 📊 **Sentiment scoring** — rates each digest from -10 (Bearish) to +10 (Bullish)
- 📧 **Email delivery** — sends a clean formatted digest to your inbox
- 🔁 **Autonomous** — runs every 30 minutes, only alerts you when new articles appear
- 💾 **No duplicates** — tracks seen articles so you never get the same news twice

---

## 📋 Prerequisites

Before you start, make sure you have:

- [Python 3.9+](https://www.python.org/downloads/) installed
- A Gmail account
- An OpenAI account with API credits ([platform.openai.com](https://platform.openai.com))

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/indian-market-news-summarizer.git
cd indian-market-news-summarizer
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Open `news_emailer.py` and fill in the CONFIG section at the top of the file:

```python
# -------- CONFIG --------
TOPIC = "NBCC"               # Stock or company name to filter by. Leave "" for all news.
FEEDS = [
    "https://economictimes.indiatimes.com/markets/rss.cms",
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.business-standard.com/rss/markets-106.rss",
]
EMAIL_SENDER   = "yourgmail@gmail.com"
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"   # Gmail App Password (see below)
EMAIL_RECEIVER = "yourgmail@gmail.com"   # Where to send the digest
OPENAI_API_KEY = "sk-..."                # Your OpenAI API key
# ------------------------
```

---

## 📬 Gmail App Password Setup

Gmail requires an **App Password** for programmatic email sending — your regular Gmail password will not work.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already on
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Type any name (e.g. `news emailer`) and click **Create**
5. Copy the 16-character password and paste it into `EMAIL_PASSWORD` **without spaces**

---

## 🔑 OpenAI API Key Setup

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** and create a new key
4. Add at least **$5 in credits** under Billing (required for API access)
5. Paste the key into `OPENAI_API_KEY` in the config

---

## ▶️ Running the Bot

```bash
python news_emailer.py
```

The bot will:
1. Run immediately on start and check for new articles
2. Print `No new relevant articles found.` if nothing new is available
3. Send you an email digest if new articles matching your topic are found
4. Automatically recheck every **30 minutes**

Keep the terminal open while running. To stop it, press `Ctrl+C`.

---

## 📧 Sample Email Output

```
MARKET NEWS DIGEST — NBCC
========================================
3 new articles found

ARTICLES COVERED:
1. NBCC shares rise 4% after government contract win
2. Record dates for NBCC dividend next week
3. Market Trading Guide: Buy NBCC on Monday for up to 11% gains

LINKS:
1. https://economictimes.indiatimes.com/...
2. https://economictimes.indiatimes.com/...
3. https://economictimes.indiatimes.com/...

========================================
ANALYSIS:

SUMMARY: NBCC has seen renewed investor interest this week driven by a
government infrastructure contract and an upcoming dividend announcement.
Analysts are recommending the stock as a technical buy with upside targets
of up to 11%. Broader market weakness has not dampened sentiment around
NBCC specifically, which continues to outperform its sector peers.

SENTIMENT: +7 (Bullish)
REASON: Multiple buy recommendations, a dividend announcement, and a
government contract win collectively point to strong near-term upside.
```

---

## 🗂️ Project Structure

```
indian-market-news-summarizer/
│
├── news_emailer.py        # Main script
├── requirements.txt       # Python dependencies
├── seen_articles.json     # Auto-generated: tracks articles already processed
└── README.md
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `feedparser` | Parses RSS feeds from news sources |
| `openai` | Calls GPT to summarize and score articles |
| `schedule` | Runs the check every 30 minutes automatically |
| `smtplib` | Built-in Python library for sending emails |

Install all at once:

```bash
pip install feedparser openai schedule
```

---

## 🛠️ Customization

**Change the topic:**
```python
TOPIC = "Infosys"   # any stock, company, or keyword
TOPIC = ""          # empty string = get ALL market news
```

**Change how often it checks:**
```python
schedule.every(30).minutes.do(check_news)   # default: 30 mins
schedule.every(1).hours.do(check_news)      # hourly
schedule.every().day.at("08:00").do(check_news)  # once a day at 8am
```

**Add more news feeds:**
```python
FEEDS = [
    "https://economictimes.indiatimes.com/markets/rss.cms",
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.business-standard.com/rss/markets-106.rss",
    "https://www.livemint.com/rss/markets",   # add any RSS feed URL
]
```

---

## ☁️ Running 24/7 (Optional)

To keep the bot running without leaving your laptop on, deploy it for free on [PythonAnywhere](https://www.pythonanywhere.com):

1. Sign up for a free account
2. Upload `news_emailer.py` and `requirements.txt`
3. Open a Bash console and run `pip install -r requirements.txt`
4. Run `python news_emailer.py` from the console

---

## ⚠️ Notes

- The `seen_articles.json` file is created automatically on first run. Do not delete it or you will receive duplicate emails for old articles.
- OpenAI API calls cost a fraction of a cent per digest. $5 in credits will last months at typical usage.
- RSS feeds are public and do not require authentication.

---

## 📄 License

MIT License — free to use, modify, and distribute.
