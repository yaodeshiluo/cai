# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy import Item
from scrapy import Field


class Cai500Item(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    query_date = Field()
    match_name = Field()
    turn = Field()
    match_time = Field()
    both_sides = Field()
    score = Field()
    league_table = Field()
    home_team_rank = Field()
    guest_team_rank = Field()
    home_team_points = Field()
    guest_team_points = Field()
    odds = Field()
