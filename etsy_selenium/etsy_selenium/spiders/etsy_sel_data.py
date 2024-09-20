import scrapy
from scrapy import Selector
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from parsel import Selector
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import scrapy
import requests,json,time,threading,queue,os
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EtsySelDataSpider(scrapy.Spider):
    name = "etsy_sel_data"

    custom_settings = {'ROBOTSTXT_OBEY': False,
                       'RETRY_TIMES': 5,
                       'DOWNLOAD_DELAY': 0.4,
                       'FEED_URI': f'outputs/etsy_Data_{datetime.now().strftime("%d_%b_%Y_%H_%M_%S")}.csv',
                       'FEED_FORMAT': 'csv',
                       'FEED_EXPORT_ENCODING': 'utf-8',}

    def get_driver(self):
                # FRO FIRFOX
        # webdriver_service = Service(GeckoDriverManager().install())
        # options = webdriver.FirefoxOptions()
        # # options.add_argument("--headless")
        # driver = webdriver.Firefox(service=webdriver_service, options=options)
        # return driver

                # FOR GOOGLE CHROME
        # chrome_options = Options()
        # chrome_options.add_experimental_option("detach", True)
        # self.driver = webdriver.Chrome(options=chrome_options)
        # return self.driver

                # FOR UNDECTEDABLE CHOME

        options = uc.ChromeOptions()
        if not hasattr(options, 'headless'):
            options.headless = False
        driver = uc.Chrome(options=options)
        return driver


    def start_requests(self):
        url= 'https://quotes.toscrape.com/'
        yield scrapy.Request(url=url,callback=self.parse)
    def parse(self, response):
        item = dict()
        driver=self.get_driver()

        try:
            driver.get('https://www.etsy.com/search?q=phone+cases')
            time.sleep(15)
            while True:
                data=driver.page_source
                time.sleep(3)
                sel=Selector(text=data)
                links =sel.xpath("//div[contains(@class,'v2-listing-card')]/a/@href").getall()
                for each_link in links[:]:
                    driver.get(each_link)
                    time.sleep(5)
                    detail_page_data = driver.page_source
                    time.sleep(5)
                    sel_detail = Selector(text=detail_page_data)
                    item['detail_page']= each_link
                    item['title']= sel_detail.xpath('//h1[@class="wt-line-height-tight wt-break-word wt-text-body-01"]/text()').get('').strip()
                    item['rating']= sel_detail.xpath('//input[@name="rating"]/@value').get('').strip()
                    item['reviews']= sel_detail.xpath('//h2[contains(text(),"reviews")]/text()').get('').strip()
                    item['price']= "".join(sel_detail.xpath('//span[contains(text(),"Price:")]/following-sibling::text()').getall()).strip().replace(',','')
                    item['seller_name'] = sel_detail.xpath("//div[contains(text(),'by')]/a/text()").get('')
                    item['images']= ",".join(sel_detail.xpath('//div[contains(@class,"listing-page-image-carousel-component")]//ul[@data-carousel-pagination-list]//li/img/@data-src-delay').getall()).replace('il_75x75','il_794xN')
                    item['video_link'] = sel_detail.xpath("//video[@aria-label='Product video']//@src").get('')
                    item['designed_by'] = sel_detail.xpath("//div[contains(text(),'by')]/a/text()").get('')
                    item['link'] = sel_detail.xpath("//div[contains(text(),'by')]/a/@href").get('')
                    link= sel_detail.xpath("//div[contains(text(),'by')]/a/@href").get('')
                    driver.get(link)
                    time.sleep(7)
                    detail_sub_page_data = driver.page_source
                    time.sleep(7)
                    sel_sub_detail = Selector(text=detail_sub_page_data)
                    item['total_sales'] = sel_sub_detail.xpath(
                        "//a[contains(text(),'Sales')]/text() |  //span[contains(text(),'Sales')]/text() | //div[contains(text(),'Sales')]/text()").get(
                        '')
                    driver.back()
                    time.sleep(2)
                    yield item
                    driver.back()
                    time.sleep(3)

                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "(//div[@class='wt-action-group__item-container'][last()]//a[@class='wt-btn wt-btn--filled wt-action-group__item wt-btn--small wt-btn--icon'])[2]")
                    if next_button:
                        next_button.click()
                        time.sleep(4)
                    else:
                        break
                except Exception as e:
                    print("No more pages move to next url")
                    break

        except Exception as e:
            print(e)











