#!/usr/bin/env python3
"""
Advanced BBC News Scraper
Scrapes BBC News website for article titles, full text, genre, and date.
Saves CSV in format:
SERIAL NUMBER | ARTICLE | TITLE | GENRE | DATE
"""

import csv
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.bbc.com/news"

def clean_text(text):
    """Cleans headline or article text"""
    text = re.sub(r"\s+", " ", text)  # remove extra whitespace
    text = text.strip()
    return text

def get_articles(url=BASE_URL):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    nav_skip = {"News", "Sport", "Weather", "Business", "Technology", "Health", "Culture", "Home"}

    for tag in soup.find_all(["h2", "h3"]):
        title = clean_text(tag.get_text())
        if len(title) > 15 and title not in nav_skip:
            link = tag.find_parent("a")
            article_text = ""
            genre = "News"
            if link and link.get("href"):
                href = link.get("href")
                full_url = href if href.startswith("http") else "https://www.bbc.com" + href
                try:
                    art_resp = requests.get(full_url, headers=headers)
                    art_soup = BeautifulSoup(art_resp.text, "html.parser")
                    p_tags = art_soup.find_all("p")
                    article_text = " ".join([clean_text(p.get_text()) for p in p_tags if len(p.get_text()) > 0])
                    # Assign genre based on URL
                    if "/sport/" in href:
                        genre = "Sport"
                    elif "/technology/" in href:
                        genre = "Technology"
                    elif "/health/" in href:
                        genre = "Health"
                except:
                    article_text = title
            if not article_text:
                article_text = title
            articles.append({
                "title": title,
                "article": article_text,
                "genre": genre
            })
    return articles

def save_csv(articles, filename="bbc_news_advanced.csv"):
    today = datetime.today().strftime("%Y-%m-%d")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SERIAL NUMBER", "ARTICLE", "TITLE", "GENRE", "DATE"])
        for i, art in enumerate(articles, start=1):
            writer.writerow([i, art["article"], art["title"], art["genre"], today])
    print(f"Saved {len(articles)} articles to {filename}")

if __name__ == "__main__":
    print("Scraping BBC News Advanced...")
    articles = get_articles()
    save_csv(articles)