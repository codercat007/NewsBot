import feedparser
import json
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from config import OPENAI_API_KEY, TELEGRAM_BOT_TOKEN

# -------- CONFIG --------
FEEDS = [
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "https://economictimes.indiatimes.com/prime/rssfeeds/69891145.cms",
    "https://economictimes.indiatimes.com/podcasts/rssfeeds/70700695.cms",
    "https://economictimes.indiatimes.com/magazines/rssfeeds/1466318837.cms",
    "https://economictimes.indiatimes.com/nri/rssfeeds/7771250.cms",
    "https://economictimes.indiatimes.com/opinion/rssfeeds/897228639.cms",
    "https://economictimes.indiatimes.com/jobs/rssfeeds/107115.cms",
    "https://economictimes.indiatimes.com/ai/rssfeeds/119215726.cms",
    "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "https://economictimes.indiatimes.com/wealth/rssfeeds/837555174.cms",
    "https://economictimes.indiatimes.com/small-biz/rssfeeds/5575607.cms",
    "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "https://economictimes.indiatimes.com/news/rssfeeds/1715249553.cms",
    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms"
]
# ------------------------

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_articles():
    all_entries = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
    return all_entries

def is_relevant(entry, topic):
    topic_lower = topic.lower()
    title = entry.get("title", "").lower()
    description = entry.get("summary", "").lower()
    return topic_lower in title or topic_lower in description

def clean_text(text):
    return re.sub(r'<[^>]+>', '', text).strip()
'''
def analyze_merged(topic, titles, merged_description):
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
'''
def analyze_merged(topic, titles, merged_description):
    prompt = f"""
Below are multiple news articles about '{topic}'. Read all of them and write a single cohesive summary covering the key points and themes across all articles in 4-5 sentences.

Article Titles:
{chr(10).join(f'- {t}' for t in titles)}

Article Descriptions:
{merged_description}

Write the short summary, no more than 4-5 sentences, covering all the topics mentioned in a concise and clear format under 4096 characters. It should be a short analytical paragraph with no more than 5 points to support analysis if needed.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the News Bot!\n\n"
        "Just type any specific topic name alone and I'll fetch the latest news and summarize it for you.\n\n"
        "Example: *Accenture* or *Tariffs* or *climate change*",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    if not topic:
        await update.message.reply_text("Please type a specific topic.")
        return

    await update.message.reply_text(f"🔍 Searching for news about *{topic}*...", parse_mode="Markdown")

    articles = fetch_articles()
    relevant = [e for e in articles if is_relevant(e, topic)]
    if len(relevant)>5:
        relevant = relevant[:5]  # limit to top 5 articles for analysis

    if not relevant:
        await update.message.reply_text(
            f"❌ No articles found about *{topic}* in the current news feeds.",
            parse_mode="Markdown"
        )
        return

    titles = [clean_text(e.get("title", "No title")) for e in relevant]
    descriptions = [clean_text(e.get("summary", "")) for e in relevant]
    links = [e.get("link", "") for e in relevant]

    merged_description = "\n\n".join(
        f"[Article {i+1}] {desc}" for i, desc in enumerate(descriptions) if desc
    )

    await update.message.reply_text(f"📊 Found {len(relevant)} articles. Analyzing...")

    try:
        analysis = analyze_merged(topic, titles, merged_description)

        titles_section = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
        links_section = "\n".join(f"{i+1}. {l}" for i, l in enumerate(links))

        response_text = (
            f"📰 *MARKET NEWS DIGEST — {topic}*\n"
            f"{'='*35}\n"
            f"{len(relevant)} articles found\n\n"
            f"*ARTICLES COVERED:*\n{titles_section}\n\n"
            f"*LINKS:*\n{links_section}\n\n"
            f"{'='*35}\n"
            f"*ANALYSIS:*\n\n{analysis}"
        )

        # Telegram has a 4096 char limit per message, split if needed
        if len(response_text) <= 4096:
            await update.message.reply_text(response_text, parse_mode="Markdown")
        else:
            # send analysis separately if too long
            header = (
                f"📰 *MARKET NEWS DIGEST — {topic}*\n"
                f"{len(relevant)} articles found\n\n"
                f"*ARTICLES COVERED:*\n{titles_section}\n\n"
                f"*LINKS:*\n{links_section}"
            )
            await update.message.reply_text(header, parse_mode="Markdown")
            await update.message.reply_text(f"*ANALYSIS:*\n\n{analysis}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error during analysis: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot is running...")
    app.run_polling()