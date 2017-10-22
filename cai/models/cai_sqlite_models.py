#!/usr/bin/env python
# -*- coding: utf-8 -*-
from peewee import *

db = SqliteDatabase('cai.sqlite')


class BaseModel(Model):

    class Meta:
        database = db


class Match(BaseModel):
    query_date = CharField()
    match_name = CharField()
    turn = CharField(null=True)
    match_time = CharField()
    both_sides = CharField()
    score = CharField()
    home_team_rank = IntegerField(null=True)
    guest_team_rank = IntegerField(null=True)
    home_team_points = IntegerField(null=True)
    guest_team_points = IntegerField(null=True)
    league_table = TextField(null=True)
    odds = TextField()

    class Meta:
        database = db
        indexes = (
            (('query_date', 'match_name', 'both_sides'), True),
        )
        db_table = 'match'


# class Odds(BaseModel):
#     team = CharField()
#     chupei = DecimalField()
#     zhongpei = DecimalField()
#     match = ForeignKeyField(Match, related_name='odds')
