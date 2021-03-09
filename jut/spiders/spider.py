import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import JutItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class JutSpider(scrapy.Spider):
	name = 'jut'
	start_urls = ['https://jutlander.dk/om-jutlander-bank/nyt?PID=3733&page=1']
	page = 2
	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://jutlander.dk/om-jutlander-bank/nyt?PID=3733&page={self.page}'
		if self.page<100:
			self.page+=1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//span[@class="date"]/text()').get().split(' ')[0]
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="news-details"]//text()[not (ancestor::h1) and not (ancestor::span[@class="date"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=JutItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
