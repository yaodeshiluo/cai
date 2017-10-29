### 安装
scrapy和peewee(一个轻型orm)
```python
pip install scrapy
pip install peewee
```

### 操作指南
通过执行run.py文件可以操作抓取某些日期的相关数据，如

抓取当天的数据
```python
python run.py
```

抓取某个日期范围内(2010-01-01至2017-10-25)的数据
```python
python run.py date_range=2010-01-01,2017-10-25
```

抓取某一天的数据
```python
python run.py date_range=2017-10-25,2017-10-25
```

抓取某一天(2010-01-01)到今天的数据
```python
python run.py date_range=2010-01-01
```

### 抓取数据存放处
cai/models/cai.sqlite

### 抓取数据字段说明

| query_date | 赛事日期，格式:2010-01-01 |
| match_name | 赛事 |
| turn | 轮次 |
| match_time | 比赛时间 |
| both_sides | 对阵 |
| score | 比分 |
| home_team_rank | 主队赛前排名 |
| guest_team_rank | 客队赛前排名 |
| home_team_points | 主队赛前积分 |
| guest_team_points | 客队赛前排名 |
| league_table | 赛前积分榜(有些数据只能从析页面提取了两只队伍的积分和排名, 没有完整数据) |
| odds | 进入欧页面抓取的赔率信息,格式为{‘威廉希尔’,: { ‘chupei’: [2.5,3.3,2.8], ‘zhongpei’:[3.1,2.8,3.0] }, ‘立博’: { ‘chupei’: [2.1,3.3,2.9], ‘zhongpei’:[3.5,2.4,3.1] } … } |
