import scrapy

class malignant_spider(scrapy.Spider):
    name = "malignant"

    start_urls = [
        'https://www.chickensandmore.com/'  
    ]

    def parse(self, response):
        page = response.url.split('/')[-1]
        filename = 'malignant%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)