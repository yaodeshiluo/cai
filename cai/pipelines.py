# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem

# query_date = Field()
# match_name = Field()
# turn = Field()
# match_time = Field()
# both_sides = Field()
# score = Field()
# league_table = Field()
# home_team_rank = Field()
# guest_team_rank = Field()
# home_team_points = Field()
# guest_team_points = Field()
# odds = Field()


class HandleFieldPipeline(object):
    def process_item(self, item, spider):
        for field in item.fields.keys():
            handler = getattr(self, field + '_handler', None)
            if handler is not None:
                handler(item)
        return item

    @staticmethod
    def league_table_handler(item):
        league_table = item['league_table']
        home_team, _, guest_team = item['both_sides']

        def get_rank_points_from_table(team):
            for row in league_table:
                row_rank, row_team, row_points = row
                if team in row_team or row_team in team:
                    return row_rank, row_points
            return None

        home_team_rank_points = get_rank_points_from_table(home_team)
        if home_team_rank_points:
            item['home_team_rank'], item['home_team_points'] = home_team_rank_points

        guest_team_rank_points = get_rank_points_from_table(guest_team)
        if guest_team_rank_points:
            item['guest_team_rank'], item['guest_team_points'] = guest_team_rank_points


class CheckPipeline(object):
    def process_item(self, item, spider):
        self.common_checker(item)
        for field in item.fields.keys():
            checker = getattr(self, field + '_checker', None)
            if checker is not None:
                checker(item)
        return item

    @staticmethod
    def both_sides_checker(item):
        both_sides = item['both_sides']
        assert isinstance(both_sides, (list, tuple)) and len(both_sides) == 3, DropItem('invalid both_sides')

    @staticmethod
    def common_checker(item):
        for field in ['query_date', 'match_name', 'match_time']:
            assert item.get(field), DropItem('invalid Field: %s' % field)
