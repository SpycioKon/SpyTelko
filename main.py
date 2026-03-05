import asyncio
from crawler import TelegramCrawler

GROUPS = [
   # "@group_tele_sample"
]

async def main():
    crawler = TelegramCrawler()
    await crawler.start()

    for group in GROUPS:
        print(f"Crawling: {group}")
        await crawler.crawl_group(group)

if __name__ == "__main__":
    asyncio.run(main())
