# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import re
import pandas as pd
import datetime as dt

class RatesSpider(scrapy.Spider):
    name = 'rates'
    allowed_domains = ['cbr.ru']

#    base_url = 'https://www.cbr.ru/hd_base/zcyc_params/zcyc/?DateTo='

    start_date = dt.date(2009, 1, 7)
    end_date = dt.date(2012, 1, 7)

    datelist = pd.date_range(start=str(start_date), end=str(end_date)).tolist()
    formatted_dates = [dt.datetime.strftime(date, '%d.%m.%Y') for date in datelist]
    print(formatted_dates)
    start_urls = ['https://www.cbr.ru/hd_base/zcyc_params/zcyc/?DateTo=' + date for date in  formatted_dates]
    print(start_urls)
#    start_urls = ['https://www.cbr.ru/hd_base/zcyc_params/zcyc/?DateTo=01.10.2018']

    # def start_requests(self):
    #     base_url = 'https://www.cbr.ru/hd_base/zcyc_params/zcyc/?DateTo='
    #
    #     datelist = pd.date_range(start=str(start_date), end=str(end_date)).tolist()
    #     formatted_dates = [datetime.datetime.strftime(date, '%d.%m.%Y') for date in datelist]
    #     urls = [base_url + date for date in  formatted_dates]
    #
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    #generating datelist

#    start_urls = ['https://www.cbr.ru/hd_base/zcyc_params/zcyc/?DateTo=01.10.2018']

    def parse(self, response):

        rates = response.xpath('//td').extract()
        parsed_rates = re.findall(pattern = "[0-9]{1,2}.[0-9]{2}", string = str(rates))
        date = response.url[-10:]

        if parsed_rates:
            yield {'Dates': dt.datetime.strptime(date, '%d.%m.%Y'),
            '0.25': parsed_rates[0],
            '0.50': parsed_rates[1],
            '0.75': parsed_rates[2],
            '1.00': parsed_rates[3],
            '2.00': parsed_rates[4],
            '3.00': parsed_rates[5],
            '5.00': parsed_rates[6],
            '7.00': parsed_rates[7],
            '10.00': parsed_rates[8],
            '15.00': parsed_rates[9]
               }

# scrapy crawl weather -o file.csv -t csv
