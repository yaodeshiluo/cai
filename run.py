# coding:utf-8
import sys
import logging
from datetime import timedelta, datetime
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from cai.spiders.Cai500Spider import Cai500Spider


logger = logging.getLogger()
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


def _get_argv_dict():
    ret = {}
    argv = sys.argv
    for each in argv[1:]:
        if '=' in each:
            k, v = each.split('=')
            ret[k] = v
    return ret


def get_start_urls():
    base_url = 'http://odds.500.com/index_history_%s.shtml'
    argv = _get_argv_dict()
    date_range = argv.get('date_range')
    fmt = '%Y-%m-%d'
    now = datetime.now()
    if date_range:
        date_range = map(lambda _: datetime.strptime(_, fmt), date_range.split(','))
        if len(date_range) == 1:
            date_range.append(now)
        if len(date_range) != 2:
            raise ValueError('invalid date_range')
        date_range.sort()
        start_date = date_range[0]
        end_date = date_range[1]
        while True:
            yield base_url % start_date.strftime(fmt)
            start_date += timedelta(days=1)
            if start_date.date() > end_date.date():
                break
    else:
        yield base_url % now.strftime(fmt)


if __name__ == '__main__':
    start_urls = get_start_urls()
    runner = CrawlerRunner(get_project_settings())
    dfs = set()
    d = runner.crawl(Cai500Spider, start_urls=start_urls)
    dfs.add(d)
    defer.DeferredList(dfs).addBoth(lambda _: reactor.stop())
    reactor.run()
