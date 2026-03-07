import feedparser
import smtplib
import schedule
import time
import json
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from config import OPENAI_API_KEY,EMAIL_SENDER,EMAIL_PASSWORD,EMAIL_RECEIVER

# -------- CONFIG --------
TOPIC = "UPL"  # keyword to filter articles, leave empty "" to get all articles
FEEDS = [
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
]
SEEN_ARTICLES_FILE = "seen_articles.json"
# ------------------------

client = OpenAI(api_key=OPENAI_API_KEY)

def load_seen_articles():
    if os.path.exists(SEEN_ARTICLES_FILE):
        with open(SEEN_ARTICLES_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen_articles(seen):
    with open(SEEN_ARTICLES_FILE, "w") as f:
        json.dump(seen, f)

def fetch_articles():
    all_entries = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
    return all_entries

def is_relevant(entry):
    if not TOPIC.strip():
        return True
    topic_lower = TOPIC.lower()
    title = entry.get("title", "").lower()
    description = entry.get("summary", "").lower()
    return topic_lower in title or topic_lower in description

def clean_text(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def analyze_merged(topic, titles, merged_description, links):
    links_text = "\n".join(f"- {l}" for l in links)
    prompt = f"""
You are a financial news analyst specializing in Indian markets.

Below are multiple news article descriptions about '{topic}', merged together. Based on all of them combined:

1. Write a concise 4-5 sentence summary covering the key themes across all articles.
2. Give an overall sentiment score from -10 to +10 where:
   -10 = extremely negative/bearish
   0   = neutral
   +10 = extremely positive/bullish

Format your response exactly like this:
SUMMARY: <your summary here>
SENTIMENT: <score> (<one word: Bearish / Slightly Bearish / Neutral / Slightly Bullish / Bullish>)
REASON: <one sentence explaining the sentiment score>

Article Titles:
{chr(10).join(f'- {t}' for t in titles)}

Merged Descriptions:
{merged_description}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print(f"Email sent: {subject}")

def check_news():
    print(f"Checking for new articles... (Topic filter: '{TOPIC}')")
    seen = load_seen_articles()
    articles = fetch_articles()

    # collect all new relevant articles first
    new_articles = []
    for entry in articles:
        link = entry.get("link", "")
        if link in seen:
            continue
        if is_relevant(entry):
            new_articles.append(entry)

        else:
            # mark irrelevant ones as seen so we skip them next time
            seen.append(link)

    if not new_articles:
        print("No new relevant articles found.")
        save_seen_articles(seen)
        return
    
    # merge all titles, descriptions and links
    titles = [clean_text(e.get("title", "No title")) for e in new_articles]
    descriptions = [clean_text(e.get("summary", "")) for e in new_articles]
    links = [e.get("link", "") for e in new_articles]

    merged_description = "\n\n".join(
        f"[Article {i+1}] {desc}" for i, desc in enumerate(descriptions) if desc
    )
    print("MERGED DESCRIPTION:", merged_description)
    print(f"Found {len(new_articles)} new articles about '{TOPIC}'. Analyzing...")

    try:
        
        analysis = analyze_merged(TOPIC, titles, merged_description, links)

        links_section = "\n".join(f"{i+1}. {l}" for i, l in enumerate(links))
        titles_section = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))

        body = f"""
MARKET NEWS DIGEST — {TOPIC}
{'='*40}
{len(new_articles)} new articles found

ARTICLES COVERED:
{titles_section}

LINKS:
{links_section}

{'='*40}
ANALYSIS:

{analysis}
"""
        print(body)
        """body = ANALYSIS:

SUMMARY: Analysts recommend buying NBCC for potential gains amid bearish market sentiment.
SENTIMENT: Slightly Bullish
REASON: Despite overall market bearishness, analysts see potential for gains in NBCC due to technical breakout.
"""
        send_email(f"[Market Digest] {TOPIC} — {len(new_articles)} new articles", body)

        # mark all as seen after successful email
        for link in links:
            seen.append(link)
        save_seen_articles(seen)
        print(f"Done. Digest sent for {len(new_articles)} articles.")

    except Exception as e:
        print(f"Error during analysis/email: {e}")

# run every 30 minutes
schedule.every(30).minutes.do(check_news)

print("News emailer started...")
check_news()

while True:
    schedule.run_pending()
    time.sleep(60)