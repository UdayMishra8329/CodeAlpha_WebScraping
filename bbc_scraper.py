
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time


class BBCNewsScraper:

    def __init__(self):
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
        }

        self.urls = [
            "https://www.bbc.com/news",
            "https://www.bbc.com/news/world",
            "https://www.bbc.com/news/business",
            "https://www.bbc.com/news/technology",
            "https://www.bbc.com/news/science_and_environment",
            "https://www.bbc.com/news/uk"
        ]

        self.articles = []

    def get_html(self, url):
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15
            )

            response.raise_for_status()
            return response.text

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_category(self, url):

        categories = [
            "world",
            "business",
            "technology",
            "science_and_environment",
            "uk",
            "sport"
        ]

        for cat in categories:
            if cat in url.lower():
                return cat.upper()

        return "GENERAL"

    def scrape_page(self, url):

        print(f"\nScraping: {url}")

        html = self.get_html(url)

        if not html:
            return

        soup = BeautifulSoup(html, "lxml")

        links = soup.find_all("a", href=True)

        count = 0

        for link in links:

            href = link["href"]

            if href.startswith("/"):
                href = "https://www.bbc.com" + href

            if "bbc.com/news" not in href:
                continue

            title = link.get_text(strip=True)

            if len(title) < 20:
                continue

            article = {
                "Title": title,
                "URL": href,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Summary": "",
                "Category": self.extract_category(href),
                "Scraped_At": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            self.articles.append(article)
            count += 1

        print(f"Collected {count} links")

    def clean_data(self):

        df = pd.DataFrame(self.articles)

        if len(df) == 0:
            return df

        df = df.drop_duplicates(subset=["URL"])
        df = df.drop_duplicates(subset=["Title"])

        df = df[df["Title"].str.len() > 20]

        return df.reset_index(drop=True)

    def save_data(self, df):

        df.to_csv(
            "bbc_news_articles.csv",
            index=False,
            encoding="utf-8"
        )

        df.to_json(
            "bbc_news_articles.json",
            orient="records",
            indent=2
        )

        try:
            df.to_excel(
                "bbc_news_articles.xlsx",
                index=False
            )
        except Exception as e:
            print("Excel export skipped:", e)

        print("\nFiles saved successfully")

    def show_stats(self, df):

        print("\n" + "=" * 60)
        print("SCRAPING RESULTS")
        print("=" * 60)

        print(f"Total Articles: {len(df)}")

        print("\nCategory Distribution:")
        print(df["Category"].value_counts())

        print("\nSample Data:")
        print(df.head())

    def run(self):

        print("=" * 60)
        print("BBC NEWS SCRAPER")
        print("=" * 60)

        for url in self.urls:
            self.scrape_page(url)
            time.sleep(2)

        df = self.clean_data()

        if len(df) == 0:
            print("No data collected.")
            return

        self.show_stats(df)
        self.save_data(df)

        print("\nScraping completed successfully!")
        print(f"Total unique articles: {len(df)}")


if __name__ == "__main__":
    scraper = BBCNewsScraper()
    scraper.run()

