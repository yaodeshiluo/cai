# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import json
from cai.models.cai_sqlite_models import Match
from scrapy.exceptions import DropItem


class SavePipeline(object):
    def process_item(self, item, spider):
        search = {
            'query_date': item['query_date'],
            'match_name': item['match_name'],
            'both_sides': item['both_sides'],
        }
        old_item = Match.filter(**search)
        if len(old_item) == 0:
            m = Match(**item)
            m.save()
            logging.info('save: %s  %s  %s' % (search['query_date'], search['match_name'], search['both_sides']))
        else:
            old_item = old_item[0]
            to_update = self.get_to_update(old_item, item)
            if to_update:
                logging.info('update: %s  %s  %s' % (search['query_date'], search['match_name'], search['both_sides']))
                logging.info(to_update)
                Match.update(**to_update).where(Match.id == old_item.id).execute()
        return item

    @staticmethod
    def get_to_update(old_item, new_item):
        to_update = {}
        for key in new_item.fields.keys():
            old_value = getattr(old_item, key, None)
            new_value = new_item.get(key)
            if not old_value:
                if new_value:
                    to_update[key] = new_value
            else:
                if new_value:
                    if key == 'odds':
                        old_value = json.loads(old_value)
                        new_value = json.loads(new_value)
                        has_new = False
                        for k in new_value.keys():
                            if not old_value.get(k):
                                if new_value.get(k):
                                    old_value[k] = new_value[k]
                                    has_new = True
                        if has_new:
                            to_update[key] = json.dumps(old_value)

        return to_update


class FormatPipeline(object):
    def process_item(self, item, spider):
        self.common_formatter(item)
        for field in item.fields.keys():
            formatter = getattr(self, field + '_formatter', None)
            if formatter is not None:
                formatter(item)
        return item

    @staticmethod
    def score_formatter(item):
        score = item.get('score')
        if score and ':' not in score:
            del item['score']

    @staticmethod
    def both_sides_formatter(item):
        both_sides = item['both_sides']
        item['both_sides'] = ' VS '.join([both_sides[0], both_sides[-1]])

    @staticmethod
    def odds_formatter(item):
        odds = item['odds']
        item['odds'] = json.dumps(odds)

    @staticmethod
    def league_table_formatter(item):
        league_table = item.get('league_table')
        if league_table is not None:
            item['league_table'] = json.dumps(league_table)

    @staticmethod
    def common_formatter(item):
        for field in ['home_team_rank', 'guest_team_rank', 'home_team_points', 'guest_team_points']:
            if field in item:
                value = item[field]
                if not isinstance(value, basestring) or not value.isdigit():
                    del item[field]


class HandleFieldPipeline(object):
    def process_item(self, item, spider):
        for field in item.fields.keys():
            handler = getattr(self, field + '_handler', None)
            if handler is not None:
                handler(item)
        return item

    @staticmethod
    def league_table_handler(item):
        league_table = item.get('league_table', [])
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
