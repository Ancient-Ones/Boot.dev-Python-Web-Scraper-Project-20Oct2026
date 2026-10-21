from crawl import crawl_site_async
from json_report import write_json_report
import sys, asyncio

async def main():
	if len(sys.argv) > 4:
		print("too many arguments provided")
		sys.exit(1)
	else:
		crawled_pages = await crawl_site_async(sys.argv[1], sys.argv[2], sys.argv[3])
		write_json_report(crawled_pages)
		print(f"Report created")

if __name__ == "__main__":
    asyncio.run(main())
