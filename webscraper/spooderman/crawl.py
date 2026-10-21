from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
import requests, aiohttp, asyncio

class AsyncCrawler:
	def __init__(self,url,concurrency,pages):
		self.base_url = url
		self.base_domain = ".".join(urlsplit(self.base_url).netloc.split(".")[-2:])
		self.page_data = {}
		self.visited = set()
		self.lock = asyncio.Lock()
		self.max_concurrency = int(concurrency)
		self.semaphore = asyncio.Semaphore(self.max_concurrency)
		self.session = None
		self.max_pages = int(pages)
		self.should_stop = False
		self.all_tasks = set()

	async def __aenter__(self):
		self.session = aiohttp.ClientSession()
		return self

	async def __aexit__(self,exc_type, exc_val,exc_tb):
		await self.session.close()

	async def add_page_visit(self,normalized_url):
		async with self.lock:
			if self.should_stop == True:
				return False
			if len(self.visited) == self.max_pages:
				self.should_stop = True
				print("Reached maximum number of pages to crawl")
				return False
			if normalized_url in self.visited:
				return False
			self.visited.add(normalized_url)
			return True

	async def get_html(self,url):
		async with self.session.get(url) as resp:
			try:
				resp.raise_for_status()
			except aiohttp.ClientError as er:
				print(f"An error occurred: {er}")
				return
			if "text/html" not in resp.headers.get("Content-Type"):
				raise Exception(f"Content-type header is not text/html")
			else:
				return await resp.text()

	async def crawl_page(self,current_url=None):
		if self.should_stop == True:
			return
		if current_url == None:
			current_url = self.base_url
		current_domain = ".".join(urlsplit(current_url).netloc.split(".")[-2:])
		if current_domain != self.base_domain:
			return
		norm_current_url = normalize_url(current_url)
		not_visited = await self.add_page_visit(norm_current_url)
		if not_visited == False:
			return
		async with self.semaphore:
			html = await self.get_html(current_url)
			if html is None:
				return
			print(f"Extracting page data from {current_url}")
			data = extract_page_data(html,current_url)
			async with self.lock:
				self.page_data[norm_current_url] = data
		tasks = []
		for links in data["outgoing_links"]:
			task = asyncio.create_task(self.crawl_page(current_url=links))
			tasks.append(task)
			self.all_tasks.add(task)
		try:
			await asyncio.gather(*tasks)
		finally:
			for task in tasks:
				self.all_tasks.discard(task)

	async def crawl(self):
		await self.crawl_page(self.base_url)
		return self.page_data






async def crawl_site_async(url,concurrency,pages):
		async with AsyncCrawler(url,concurrency,pages) as crawler:
			return await crawler.crawl()

def normalize_url(url_link):
	norm_url = urlsplit(url_link)
	return norm_url.netloc + norm_url.path + norm_url.query + norm_url.fragment

def get_heading_from_html(html):
	soup = BeautifulSoup(html, "html.parser")
	h_tag = soup.find("h1")
	h2_tag = soup.find("h2")
	if isinstance(h_tag,Tag):
		return h_tag.get_text(html, strip=True)
	elif isinstance(h2_tag,Tag):
		return h2_tag.get_text(html, strip=True)
	else:
		return ""

def get_first_paragraph_from_html(html):
	soup = BeautifulSoup(html, "html.parser")
	main_tag = soup.find("main")
	p_tag = soup.find("p")
	if isinstance(main_tag, Tag):
		p_tag = soup.main.find("p")
		if p_tag is not None:
			return p_tag.get_text(html, strip=True)
		return ""
	elif isinstance(p_tag, Tag):
		return p_tag.get_text(html, strip=True)
	else:
		return ""

def get_urls_from_html(html, base_url):
	soup = BeautifulSoup(html, "html.parser")
	url_links = []
	for urls in soup.find_all("a"):
		if urls.get("href") is not None:
			abs_link = urljoin(base_url,urls.get("href"))
			url_links.append(abs_link)
	return url_links

def get_images_from_html(html, base_url):
	soup = BeautifulSoup(html, "html.parser")
	image_links = []
	for images in soup.find_all("img"):
		if images.get("src") is not None:
			image_links.append(urljoin(base_url,images.get("src")))
	return image_links

def extract_page_data(html,page_url):
	return {
		"url": page_url,
		"heading": get_heading_from_html(html),
		"first_paragraph": get_first_paragraph_from_html(html),
		"outgoing_links": get_urls_from_html(html,page_url),
		"image_urls": get_images_from_html(html,page_url),
	}
