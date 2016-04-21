# -*- coding: utf-8 -*-
"""
Created on 9:18 PM, 2/25/16
finanlize data of ED, RD, YG for dynamic monitor

@author: tw
"""

import sys
sys.path.append('..')
import pymongo
import util.db_util as dbt


def transform():
    db = dbt.db_connect_no_auth('rd')
    cols = db['com']
    db = dbt.db_connect_no_auth('drd')
    cold = db['com']
    cold.create_index([('id', pymongo.ASCENDING)], unique=True)
    for user in cols.find({'level': 3}, ['id', 'screen_name',
                               "description", "friends_count",
                               "followers_count", "statuses_count"]):
        cold.insert({'id': user['id'],
                     'screen_name':user['screen_name'],
                     'description': user['description'],
                     'friends_count': user['friends_count'],
                     'followers_count': user['followers_count'],
                     'statuses_count': user['statuses_count']})


def select_sub(dbname, colname, newcolname, timename, newtimename):
    db = dbt.db_connect_no_auth(dbname)
    com = db[colname]
    newcom = db[newcolname]
    newcom.create_index("id", unique=True)
    newcom.create_index([('level', pymongo.ASCENDING)],
                        unique=False)

    timeline = db[timename]
    newtimeline = db[newtimename]
    newtimeline.create_index([('user.id', pymongo.ASCENDING),
                              ('id', pymongo.DESCENDING)])
    newtimeline.create_index([('id', pymongo.ASCENDING)], unique=True)

    for user in com.find({'level':1}):
        newcom.insert(user)
        for tw in timeline.find({'user.id': user['id']}):
            newtimeline.insert(tw)


def get_users(dbname, level=1):
    user_set = set()
    db = dbt.db_connect_no_auth(dbname)
    cols = db['com']
    for user in cols.find({'level': {'$lte': level}}, ['id']):
        user_set.add(user['id'])
    return user_set


def test_common():
    eds, rds, ygs = get_users('fed'), get_users('rd', 100), get_users('yg', 100)
    # rds, ygs = get_users('rd'), get_users('yg')
    print eds.intersection(rds)
    print eds.intersection(ygs)
    print ygs.intersection(rds)


def test_timline():
    db = dbt.db_connect_no_auth('rd')
    cols = db['com']
    for user in cols.find({'timeline_count': {'$lt': 3200}}, ['id', 'timeline_count', 'statuses_count']):
        # print user
        if (user['statuses_count']-user['timeline_count']) > 100:
            print user['id']
            cols.update({'id': user['id']}, {'$set': {"timeline_count": 0,
                        'timeline_scraped_times': 0}}, upsert=False)


def select_non_common_user():
    eds = get_users('ded')
    rds = get_users('drd')
    db = dbt.db_connect_no_auth('yg')
    cols = db['com']
    db = dbt.db_connect_no_auth('dyg')
    cold = db['com']
    size = len(eds)-cold.count()
    for user in cols.find({'level': 3}, ['id', 'screen_name',
                               "description", "friends_count",
                               "followers_count", "statuses_count"]):
        if user['id'] not in eds and size > 0 and user['id'] not in rds:
            cold.insert({'id': user['id'],
                         'screen_name':user['screen_name'],
                         'description': user['description'],
                         'friends_count': user['friends_count'],
                         'followers_count': user['followers_count'],
                         'statuses_count': user['statuses_count']})
            size -= 1
        else:
            break


def remove_non_targeted_user():
    sets = get_users('dyg')
    db = dbt.db_connect_no_auth('yg')
    poidb = db['com']
    netdb = db['net']
    for user in poidb.find({}, ['id']):
        if user['id'] not in sets:
            poidb.delete_one({'id': user['id']})
            netdb.delete_many({'user': user['id']})
            netdb.delete_many({'follower': user['id']})

if __name__ == '__main__':
    # db = dbt.db_connect_no_auth('fed')
    # cols = db['com']
    # for user in cols.find({'level': {'$lte': 1}}, ['id', 'screen_name']):
    #     print user['screen_name']

    select_sub('fed', 'com', 'ccom', 'timeline', 'ctimeline')

