# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from peewee import InsertQuery
from cai.models.cai_sqlite_models import Match
from scrapy.exceptions import DropItem


class SavePipeline(object):
    def process_item(self, item, spider):
        # InsertQuery(Match, field_dict=item).upsert().execute()
        search = {
            'query_date': item['query_date'],
            'match_name': item['match_name'],
            'both_sides': item['both_sides'],
        }
        old_item = Match.get(**search)
        if old_item:
            to_update = self.get_to_update(old_item, item)
            Match.update(**to_update).where(id=old_item['id'])
        else:
            m = Match(**item)
            m.save()

    @staticmethod
    def get_to_update(old_item, new_item, just_complete=False):
        to_update = {}
        for key, new_value in new_item.iteritems():
            old_value = old_item.get(key)
            if not old_value:
                if new_value:
                    to_update[key] = new_value
            elif not just_complete:
                if new_value:
                    if key == 'odds':
                        old_value = json.loads(old_value)
                        new_value = json.loads(new_value)
                        old_value.update(SavePipeline.get_to_update(old_value, new_value, just_complete=True))
                        to_update[key] = json.dumps(old_value)
                    elif key == 'score':
                        if 'VS' not in new_value and new_item != old_value:
                            to_update[key] = new_value
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
    def both_sides_formatter(item):
        both_sides = item['both_sides']
        item['both_sides'] = ' '.join(both_sides)

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
