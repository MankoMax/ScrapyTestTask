import scrapy
from scrapy.http import Response
from scrapy_rental.items import RentalItem
import re
from typing import List, Optional


class KelmImmobilienSpider(scrapy.Spider):
    name = "kelm_immobilien"
    start_urls = ["https://kelm-immobilien.de/immobilien"]

    def parse(self, response: Response) -> scrapy.Request:
        for page in response.css("a.page-numbers::attr(href)").getall():
            yield scrapy.Request(response.urljoin(page), callback=self.parse_page)

        yield from self.parse_page(response)

    def parse_page(self, response: Response) -> scrapy.Request:
        for property in response.css("div.property.col-sm-6.col-md-4"):
            url = response.urljoin(property.css("a.thumbnail::attr(href)").get())
            yield scrapy.Request(url, callback=self.parse_property)

    def parse_property(self, response: Response) -> RentalItem:
        item = RentalItem()
        item['url'] = response.url
        item['title'] = response.css("h1::text").get().strip()
        item['status'] = response.css("li.data-vermietet .dd::text").get().strip() if response.css(
            "li.data-vermietet") else None
        item['pictures'] = self._extract_image_urls(response)
        item['rent_price'] = self._parse_price(response)
        item['description'] = self._extract_description(response)
        item['phone_number'] = response.css("div.dd.col-sm-7.p-tel.value a::text").get().replace(" ", "")
        item['email'] = response.css("div.dd.col-sm-7.u-email.value a::text").get()
        item['domain'] = self._extract_domain(response)

        yield item

    def _parse_price(self, response: Response) -> Optional[float]:
        # First, try to extract price from the price block
        price_str = response.css("li.data-kaltmiete .dd::text").get()
        if price_str:
            price = float(price_str.replace("EUR", "").replace(".", "").replace(",", ".").strip())
            return price

        # Then, try to extract price from the description
        description = self._extract_description(response)
        rent_price_match = re.search(r'(\d+[.,]?\d*)\s*€/pro\s*Monat', description)
        if rent_price_match:
            price = float(rent_price_match.group(1).replace(",", "."))
            return price

        return None

    def _extract_description(self, response: Response) -> str:
        elements = response.xpath(
            "//div[@class='panel-body']//p/text() | //div[@class='panel-body']//h3/text()").getall()

        description_parts = [text.strip() for text in elements if text.strip()]
        description = " ".join(description_parts)

        return description.strip()

    def _extract_image_urls(self, response: Response) -> List[str]:
        image_urls = []
        images = response.xpath('//div[@id="immomakler-galleria"]//img')

        for img in images:
            image_url = img.xpath('./@src').get()
            if image_url:
                image_url = image_url.rsplit("-", 1)[0] + ".jpg"
                image_urls.append(response.urljoin(image_url))

        return image_urls

    def _extract_domain(self, response: Response) -> str:
        domain_element = response.css('li.data-adresse .dd::text').get() if response.css(
            'li.data-adresse') else 'no_domain'

        domain_element = ''.join([i for i in domain_element if not i.isdigit()])

        return domain_element
