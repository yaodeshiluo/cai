#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from collections import namedtuple
from scrapy.spider import Spider
from scrapy import Request
from cai.items import Cai500Item


class Cai500Spider(Spider):

    name = '500'
    start_urls = ['http://odds.500.com/index_history_2011-11-05.shtml']

    def __init__(self, **kwargs):
        super(Cai500Spider, self).__init__(**kwargs)
        # self.download_delay = 1
        self.base_next_odds_url = 'http://odds.500.com/fenxi1/ouzhi.php?id={id}&ctype=1&start={start}&r=1&style=0&guojia=0&chupan=1'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    @staticmethod
    def extract_node(node):
        return ''.join(node.xpath('string(.)').extract()).strip()

    def parse(self, response):
        query_date = ''.join(re.findall('\d{4}-\d{2}-\d{2}', response.url))
        field_names = ['', 'match_name', 'turn', 'match_time', 'home_side', 'score', 'guest_side', '', '', '', '', '', '', '', '', 'odds_urls']
        tr_to_tuple = namedtuple('tr_to_tuple', field_names, rename=True)
        for tr in response.xpath('//*[@id="main-tbody"]/tr'):
            item = Cai500Item()
            tds = tr.xpath('td')
            if len(tds) != 16:
                continue
            row = tr_to_tuple(*tds)
            item['match_name'] = self.extract_node(row.match_name)
            item['turn'] = self.extract_node(row.turn)
            item['match_time'] = self.extract_node(row.match_time)
            item['both_sides'] = [
                self.extract_node(row.home_side),
                self.extract_node(row.score),
                self.extract_node(row.guest_side),
            ]
            item['score'] = self.extract_node(row.score)
            item['query_date'] = query_date
            odds_url = ''.join(row.odds_urls.xpath(u'a[text()="欧"]/@href').extract())
            yield Request(odds_url, meta={'data': {'item': item}}, callback=self.parse_odds)
            break  # for test

    def parse_odds(self, response):
        item = response.meta['data']['item']

        # odds
        temp = {}
        for tr in response.xpath('//*[@id="datatb"]/tr'):
            _ = self._parse_odds_tr(tr)
            if _ is not None:
                temp.update(_)
        item['odds'] = temp

        # league_table
        league_table = []
        for tr in response.xpath('//*[@id="nav_jifen"]//tr'):
            tds = tr.xpath('td')
            if len(tds) != 3:
                continue
            league_table.append(map(self.extract_node, tds))
        item['league_table'] = league_table

        # other odds
        id = ''.join(re.findall('ouzhi-(\d*)\.shtml', response.url))
        start = 30
        next_odds_url = self.base_next_odds_url.format(start=start, id=id)
        yield Request(next_odds_url, meta={'data': {'item': item, 'start': start, 'id': id}}, callback=self.parse_next_odds)

    def parse_next_odds(self, response):
        item = response.meta['data']['item']
        if response.body:
            odds = item['odds']
            for tr in response.xpath('//tr[@xls="row"]'):
                _ = self._parse_odds_tr(tr)
                if _ is not None:
                    odds.update(_)

            id = response.meta['data']['id']
            start = response.meta['data']['start'] + 30
            next_odds_url = self.base_next_odds_url.format(start=start, id=id)
            yield Request(next_odds_url, meta={'data': {'item': item, 'start': start, 'id': id}}, callback=self.parse_next_odds)
        else:
            yield item

    def _parse_odds_tr(self, tr):
        tds = tr.xpath('td')
        if len(tds) != 7:
            return None
        ret = {}
        field_names = ['', 'company', 'odds_node', '', '', '', '']
        tr_to_tuple = namedtuple('tr_to_tuple', field_names, rename=True)
        row = tr_to_tuple(*tds)

        company = ''.join(re.findall('<span class="quancheng" style="display.*?">(.*?)</span>', row.company.extract()))
        odds_node = row.odds_node
        chupei_node, zhongpei_node = odds_node.xpath('table/tbody/tr')
        chupei = map(self.extract_node, chupei_node.xpath('td'))
        zhongpei = map(self.extract_node, zhongpei_node.xpath('td'))

        ret[company] = {
            'chupei': chupei,
            'zhongpei': zhongpei
        }
        return ret
