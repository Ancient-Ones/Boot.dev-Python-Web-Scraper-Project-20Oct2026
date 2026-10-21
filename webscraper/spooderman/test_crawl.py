import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data

class TestCrawl(unittest.TestCase):
	def test_normalize_url(self):
		input_url = "https://www.boot.dev/blog/path"
		actual = normalize_url(input_url)
		expected = "www.boot.dev/blog/path"
		self.assertEqual(actual, expected)

	def test_2_normalize_url(self):
		input_url = "www.boot.dev/blog/path"
		actual = normalize_url(input_url)
		expected = "www.boot.dev/blog/path"
		self.assertEqual(actual, expected)

	def test_3_normalize_url(self):
		input_url = "notaurl@alsonoturl.verynoturl"
		actual = normalize_url(input_url)
		expected = "notaurl@alsonoturl.verynoturl"
		self.assertEqual(actual, expected)

	def test_4_normalize_url(self):
		input_url = ""
		actual = normalize_url(input_url)
		expected = ""
		self.assertEqual(actual, expected)

	def test_5_normalize_url(self):
		input_url = "https://"
		actual = normalize_url(input_url)
		expected = ""
		self.assertEqual(actual, expected)

	def test_get_heading_from_html(self):
		input_html = ["<h1>Hello world!</h1>", "<h2>Hello world again!</h2>", "<h1>Hello world too!</h1><h2>Hello world only</h2>"]
		expected = ["Hello world!","Hello world again!","Hello world too!"]
		for i, input in enumerate(input_html):
			actual = get_heading_from_html(input)
			self.assertEqual(actual, expected[i])

	def test_2_get_heading_from_html(self):
		input_html = "<p>This is a paragraph.</p>"
		expected = ""
		actual = get_heading_from_html(input_html)
		self.assertEqual(actual, expected)

	def test_get_first_paragraph_from_html(self):
		input_first_paragraph = """<html><body>
        				<p>Outside paragraph.</p>
       					<main>
           				<p>This is the first paragraph.</p>
        				</main>
    					</body></html>"""
		expected = "This is the first paragraph."
		actual = get_first_paragraph_from_html(input_first_paragraph)
		self.assertEqual(actual, expected)

	def test_2_get_first_paragraph_from_html(self):
		input_first_paragraph = """<html><body>
					<p>Outside paragraph.</p>
					<main><h1>Test Title</h1></main>
					</body></html>"""
		expected = ""
		actual = get_first_paragraph_from_html(input_first_paragraph)
		self.assertEqual(actual, expected)


	def test_get_urls_from_html(self):
		input_url = "https://crawler-test.com"
		input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
		actual = get_urls_from_html(input_body, input_url)
		expected = ["https://crawler-test.com"]
		self.assertEqual(actual, expected)

	def test_2_get_urls_from_html(self):
		input_url = "https://crawler-test.com"
		input_body = "<html><body><p>This is a paragraph.</p></body></html>"
		expected = []
		actual = get_urls_from_html(input_body,input_url)
		self.assertEqual(actual, expected)

	def test_get_images_from_html(self):
		input_url = "https://crawler-test.com"
		input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
		actual = get_images_from_html(input_body, input_url)
		expected = ["https://crawler-test.com/logo.png"]
		self.assertEqual(actual, expected)

	def test_2_get_images_from_html(self):
		input_url = "https://crawler-test.com"
		input_body = "<html><body><p>This is a paragraph.</p></body></html>"
		expected = []
		actual = get_images_from_html(input_body,input_url)
		self.assertEqual(actual, expected)

	def test_both_get_images_url_from_html(self):
		inputs = "https://crawler-test.com"
		input_body = """<html><body><a href="https://crawler-test.com">
				<span>Boot.dev</span></a>
				<img src="/logo.png" alt="Logo"></body></html>"""
		expected = [["https://crawler-test.com"],["https://crawler-test.com/logo.png"]]
		actual = [get_urls_from_html(input_body,inputs), get_images_from_html(input_body,inputs)]
		for i,actuals in enumerate(actual):
			self.assertEqual(actuals,expected[i])

	def test_extract_page_data(self):
		input_url = "https://crawler-test.com"
		input_body = """<html><body><h1>Test Title</h1>
				<p>This is the first paragraph.</p>
				<a href="/link1">Link 1</a>
				<img src="/image1.jpg" alt="Image 1"></body></html>"""
		actual = extract_page_data(input_body, input_url)
		expected = {
			"url": "https://crawler-test.com",
			"heading": "Test Title",
			"first_paragraph": "This is the first paragraph.",
			"outgoing_links": ["https://crawler-test.com/link1"],
			"image_urls": ["https://crawler-test.com/image1.jpg"],
		}
		self.assertEqual(actual, expected)

	def test_2_extract_page_data(self):
		input_url = "https://crawler-test.com"
		input_body = """<html><body>
			<p>Outside paragraph.</p>
			<main></main></body></html>"""
		actual = extract_page_data(input_body, input_url)
		expected = {
		"url": "https://crawler-test.com",
		"heading": "",
		"first_paragraph": "",
		"outgoing_links": [],
		"image_urls": [],
		}
		self.assertEqual(actual, expected)

if __name__ == "__main__":
	unittest.main()
