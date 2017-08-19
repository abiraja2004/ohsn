# -*- coding: utf-8 -*-
"""
Created on 14:45, 04/04/17

@author: wt

Younger check again at: 2017-04-25 15:46:20+00:00
Random check again at: 2017-04-25 15:46:20+00:00
Fed check again at: 2016-09-29 14:57:39+00:00

"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import pymongo
from ohsn.util import db_util as dbt
from datetime import datetime
import numpy as np
import pandas as pd
import ohsn.util.io_util as iot
from lifelines.utils import datetimes_to_durations
import ohsn.util.graph_util as gt
import scipy.stats as stats

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


def diff_day(d2, d1):
    delta = d2 - d1
    return delta.days


def read_user_time(filename):
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    groups = [
         ('ED', 'fed', 'com', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('RD', 'random', 'scom', {'liwc_anal.result.WC': {'$exists': True}}),
         ('YG', 'younger', 'scom', {'liwc_anal.result.WC': {'$exists': True}})
    ]

    data = []
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)

        for user in com.find(filter_values, no_cursor_timeout=True):
            if 'status' in user:
                created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                scraped_at = user['scrape_timeline_at']
                last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                life_time = diff_day(last_post, created_at)
                average_time = float(life_time)/min(1, user['statuses_count'])
                longest_tweet_intervalb = user['longest_tweet_interval']

                observation_interval = diff_day(scraped_at, last_post)
                if (observation_interval-longest_tweet_intervalb) > 30:
                    death = 1
                else:
                    death = 0
                values = iot.get_fields_one_doc(user, fields)
                data.append([user['id_str'], created_at, last_post, scraped_at, average_time,
                             longest_tweet_intervalb, observation_interval, tag, death] + values)

    df = pd.DataFrame(data, columns=['uid', 'created_at', 'last_post', 'scraped_at', 'average_time',
                                     'longest_time_interval', 'observation_interval', 'group',
                                     'event'] + trimed_fields)
    df.to_csv(filename)

def active_days(user):
    # print user['id']
    ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    try:
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    status_count = abs(float(user['statuses_count']))
    friend_count = abs(float(user['friends_count']))
    follower_count = abs(float(user['followers_count']))
    friends_day = friend_count/days
    statuses_day = status_count/days
    followers_day = follower_count/days
    return[friend_count, status_count, follower_count,
           friends_day, statuses_day, followers_day,
           days]

def friends_active_days(user, f1_time):
    # print user['id']
    # ts = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    ts = f1_time
    try:
        tts = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    except KeyError:
        tts = ts
    delta = tts.date() - ts.date()
    days = delta.days+1
    return [days]


def read_user_time_iv(filename):
    # fields = iot.read_fields()
    fields = [
            'senti.result.whole.posm',
            'senti.result.whole.posstd',
            'senti.result.whole.negm',
            'senti.result.whole.negstd',
            'senti.result.whole.scalem',
            'senti.result.whole.scalestd',
            'senti.result.whole.N',
            'senti.result.prior.scalem',
            'senti.result.post.scalem',
        # 'liwc_anal.result.posemo',
        #       'liwc_anal.result.negemo',
        #       'liwc_anal.result.ingest',
        #       'liwc_anal.result.bio',
        #       'liwc_anal.result.body',
        #       'liwc_anal.result.health',
        #       'liwc_anal.result.death'
        #       'liwc_anal.result.anx',
        #       'liwc_anal.result.anger',
        #       'liwc_anal.result.sad'
              ]
    prof_names = ['friends_count', 'statuses_count', 'followers_count',
        'friends_day', 'statuses_day', 'followers_day', 'days']

    trimed_fields = ['-'.join(field.split('.')[-2:]) for field in fields]
    print trimed_fields
    groups = [
         ('ED', 'fed', 'com', 'fed', 'com_survival', {
                                                        'liwc_anal.result.WC': {'$exists': True},
                                                        'level': 1,
                                                        'senti.result.whole.N': {'$gt': 10}}),
         ('RD', 'random', 'scom', 'random', 'com_survival', {
                                                        'liwc_anal.result.WC': {'$exists': True},
                                                        'senti.result.whole.N': {'$gt': 10}}),
         ('YG', 'younger', 'scom', 'younger', 'com_survival', {
                                                            'liwc_anal.result.WC': {'$exists': True},
                                                            'senti.result.whole.N': {'$gt': 10}})
    ]

    data = []
    for tag, dbname, comname, dbname2, comname2, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        com2 = dbt.db_connect_col(dbname2, comname2)
        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net-all.graphml')
        gt.summary(network1)
        network1_gc = gt.giant_component(network1)
        gt.summary(network1_gc)
        '''Centralities Calculation'''
        eigen = network1_gc.eigenvector_centrality()
        pageranks = network1_gc.pagerank()
        indegree = network1_gc.authority_score()
        outdegree = network1_gc.hub_score()

        nodes = [int(v['name']) for v in network1_gc.vs]
        eigen_map = dict(zip(nodes, eigen))
        pagerank_map = dict(zip(nodes, pageranks))
        indegree_map = dict(zip(nodes, indegree))
        outdegree_map = dict(zip(nodes, outdegree))

        # print 'load liwc 2 batches: ' + tag.lower()+'-liwc2stage.csv'
        # liwc_df = pd.read_pickle(tag.lower()+'-liwc2stage.csv'+'.pick')

        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net.graphml')
        for user in com.find(filter_values, no_cursor_timeout=True):
            first_scraped_at = user['_id'].generation_time.replace(tzinfo=None)
            if 'status' in user:
                uid = user['id']
                u2 = com2.find_one({'id': uid})

                first_last_post = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                last_post = first_last_post
                first_statuses_count = user['statuses_count']
                second_statuses_count = first_statuses_count
                drop = 1
                if u2:
                    second_scraped_at = u2['_id'].generation_time.replace(tzinfo=None)
                    second_statuses_count = u2['statuses_count']
                    if 'status' in u2:
                        second_last_post = datetime.strptime(u2['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                        if first_scraped_at < second_last_post < second_scraped_at:
                            drop = 0
                            last_post = second_last_post


                created_at = datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                # life_time = diff_day(last_post, created_at)
                # average_time = float(life_time)/max(1, user['statuses_count'])

                longest_tweet_intervalb = user['longest_tweet_interval']
                u_timeline_count = user['timeline_count']

                values = iot.get_fields_one_doc(user, fields)
                level = user['level']

                # set users liwc changes
                # uvs = liwc_df[liwc_df.user_id == str(uid)].loc[:, trimed_fields]
                # # print uvs
                # if len(uvs) == 2:
                #     changes, priors, posts = [], [], []
                #     for name in trimed_fields:
                #         old = uvs.iloc[0][name]
                #         new = uvs.iloc[1][name]
                #         priors.append(old)
                #         posts.append(new)
                #         changes.append(new - old)
                #     liwc_changes = priors + posts + changes
                # else:
                #     liwc_changes = [None]*(len(trimed_fields)*3)
                u_centrality = eigen_map.get(user['id'], 0)
                u_pagerank = pagerank_map.get(user['id'], 0)
                u_indegree = indegree_map.get(user['id'], 0)
                u_outdegree = outdegree_map.get(user['id'], 0)

                # values.extend(liwc_changes)
                values.extend(active_days(user))

                '''Get friends' profiles'''
                exist = True
                try:
                    v = network1.vs.find(name=str(uid))
                except ValueError:
                    exist = False
                if exist:
                    # friends = set(network1.neighbors(str(uid))) # id or name
                    friends = set(network1.successors(str(uid)))
                    if len(friends) > 0:
                        friend_ids = [int(network1.vs[vi]['name']) for vi in friends] # return id
                        print uid in friend_ids
                        print len(friend_ids)
                        fatts = []
                        alive = 0
                        for fid in friend_ids:
                            fu = com.find_one({'id': fid, 'liwc_anal.result.WC':{'$exists':True},
                                               'senti.result.whole.N': {'$gt': 10}})
                            fu2 = com2.find_one({'id': fid})

                            if fu:
                                f1_time = fu['_id'].generation_time.replace(tzinfo=None)
                                # if eigen_map.get(fu['id'], 0) > 0.0001:
                                if True:
                                    fatt = iot.get_fields_one_doc(fu, fields)
                                    factive = [0]
                                    if fu2:
                                        f2_time = fu2['_id'].generation_time.replace(tzinfo=None)
                                        if 'status' in fu2:
                                            fsecond_last_post = datetime.strptime(fu2['status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                                            if f1_time < fsecond_last_post < f2_time:
                                                alive += 1
                                                factive = friends_active_days(fu2, f1_time)

                                    fatt.extend(factive)
                                    fatt.extend([eigen_map.get(fu['id'], 0), pagerank_map.get(fu['id'], 0),
                                                 indegree_map.get(fu['id'], 0), outdegree_map.get(fu['id'], 0)])
                                    fatts.append(fatt)

                        # thredhold = user['friends_count']*0.5


                        if len(fatts) > 0:
                            fatts = np.array(fatts)
                            fmatts = np.mean(fatts, axis=0)
                            values.extend(fmatts)
                            paliv = float(alive)/len(fatts)
                            data.append([user['id_str'], level, drop, created_at, first_last_post, second_last_post, last_post,
                                         first_scraped_at, second_scraped_at, first_statuses_count, second_statuses_count,
                             longest_tweet_intervalb, tag, u_centrality, u_pagerank,
                                         u_indegree, u_outdegree, u_timeline_count] +
                                        values + [len(fatts), paliv])

    df = pd.DataFrame(data, columns=['uid', 'level', 'dropout', 'created_at', 'first_last_post', 'second_last_post', 'last_post', 'first_scraped_at', 'second_scraped_at',
                                     'first_statuses_count', 'second_statuses_count','longest_time_interval',
                                     'group', 'u_eigenvector', 'u_pagerank', 'u_authority', 'u_hub',
                                     'u_timeline_count'] +
                                    ['u_'+field for field in trimed_fields] +
                                    # ['u_prior_'+field for field in trimed_fields] +
                                    # ['u_post_'+field for field in trimed_fields] +
                                    # ['u_change_'+field for field in trimed_fields] +
                                    ['u_'+field for field in prof_names] +
                                    ['f_'+tf for tf in trimed_fields] +
                                    ['f_days'] +
                                    ['f_eigenvector', 'f_pagerank', 'f_authority', 'f_hub', 'f_num', 'f_palive'])
    df.to_csv(filename)


def count_longest_tweeting_period(dbname, timename, comname):
    # get users' latest 10 tweets, and calculate the largest posting interval, counted by days.
    com = dbt.db_connect_col(dbname, comname)
    time = dbt.db_connect_col(dbname, timename)
    for user in com.find({'liwc_anal.result.WC': {'$exists': True}}, no_cursor_timeout=True):
        user_id = user['id']
        datas = []
        for tweet in time.find({'user.id': user_id}, {'id': 1, 'created_at': 1}).sort([('id', -1)]).limit(10):  # sort: 1 = ascending, -1 = descending
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            datas.append(created_at)
        # print user['id']
        # print datas
        diff = [((datas[i]-datas[i+1]).days) for i in xrange(len(datas)-1)]
        max_period = max(diff)
        # print max_period
        com.update({'id': user_id}, {'$set': {'longest_tweet_interval': max_period}}, upsert=False)

def user_statis():
    groups = [
         ('ED', 'fed', 'com', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('RD', 'random', 'scom', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1}),
         ('YG', 'younger', 'scom', {'liwc_anal.result.WC': {'$exists': True}, 'level': 1})
    ]

    data = []
    for tag, dbname, comname, filter_values in groups:
        com = dbt.db_connect_col(dbname, comname)
        network1 = gt.Graph.Read_GraphML(tag.lower()+'-net.graphml')
        gt.summary(network1)
        network1_gc = gt.giant_component(network1)
        gt.summary(network1_gc)

        users_time = iot.get_values_one_field(dbname, comname, 'id_str', filter_values)
        try:
            v = network1.vs.find(name=str(uid))
        except ValueError:
            exist = False
        if exist:
            friends = set(network1.successors(str(uid)))

def insert_timestamp(dbname, colname):
    com = dbt.db_connect_col(dbname, colname)
    for user in com.find():
        print user['_id'].generation_time


def cluster_hashtag(filepath= 'user-durations-iv-following-senti.csv'):
    # read hashtag networks for dropouts and non-dropouts
    df = pd.read_csv(filepath)
    df['f_ratio'] = df.f_num/df.u_friends_count
    datat = df[df['f_ratio']>0.01]
    data = datat[datat['group']=='ED']
    uids_nondropout = [int(uid) for uid in data[(data['dropout']==0)]['uid']]
    uids_dropout = [int(uid) for uid in data[(data['dropout']==1)]['uid']]
    print len(uids_nondropout), len(uids_dropout)
    net_nondropout = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', uids_nondropout)
    net_dropout = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', uids_dropout)
    net_nondropout.write_graphml('nondropout-tag.graphml')
    net_dropout.write_graphml('dropout-tag.graphml')


def tfidf_stat_dropout():
    #ranking tag with tfidf
    gall = gt.Graph.Read_GraphML('dropout-tag-emotion3-rank-all.graphml')
    voc = dict(zip(gall.vs['name'], gall.vs['user']))
    for i in ['nondropout-tag.graphml', 'dropout-tag.graphml']:
        g = gt.Graph.Read_GraphML(i)
        # Filter network
        nodes = g.vs.select(weight_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        nodes = g.vs.select(user_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        g.vs['tfidf'] = 0.0
        for v in g.vs:
            tf = float(v['user'])
            v['tfidf'] = tf/(voc[v['name']])
        g.write_graphml('tfidf'+i)


def compare_dropouts_withemotions(filepath= 'user-durations-iv-following-senti-TE.csv'):
    # out hashtags network for users with different emotions
    df = pd.read_csv(filepath)
    df['f_ratio'] = df.f_num/df.u_friends_count
    data = df[df['f_ratio']>0.01]
    datasub = data[data['group'].isin(['ED', 'YG'])]
    mean_edu_prior = np.mean(datasub[datasub.group=='ED']['u_prior_scalem'])
    mean_edf_prior = np.mean(datasub[datasub.group=='ED']['f_prior_scalem'])
    mean_ygu_prior = np.mean(datasub[datasub.group=='YG']['u_prior_scalem'])
    mean_ygf_prior = np.mean(datasub[datasub.group=='YG']['f_prior_scalem'])

    datasub['u_prior_scalem'] = np.where((datasub.u_prior_scalem==0.0) & (datasub.group=='ED'), mean_edu_prior, datasub['u_prior_scalem'])
    datasub['f_prior_scalem'] = np.where((datasub.f_prior_scalem==0.0) & (datasub.group=='ED'), mean_edf_prior, datasub['f_prior_scalem'])
    datasub['u_prior_scalem'] = np.where((datasub.u_prior_scalem==0.0) & (datasub.group=='YG'), mean_ygu_prior, datasub['u_prior_scalem'])
    datasub['f_prior_scalem'] = np.where((datasub.f_prior_scalem==0.0) & (datasub.group=='YG'), mean_ygf_prior, datasub['f_prior_scalem'])

    datasub['u_changes'] = (datasub.u_post_scalem - datasub.u_prior_scalem)/(datasub.u_prior_scalem)
    datasub['f_changes'] = (datasub.f_post_scalem - datasub.f_prior_scalem)/(datasub.f_prior_scalem)

    dropouts = datasub[(datasub.group=='ED') & (datasub.dropout==0)][['u_whole_scalem', 'u_changes', 'uid', 'u_eigenvector']]
    print len(dropouts)

    dropouts = dropouts.sort('u_eigenvector', ascending='True')

    print dropouts

    for i in xrange(2):
        start, end = i*len(dropouts)/2, (i+1)*len(dropouts)/2
        print start, end
        uidlist = []
        for uid in dropouts['uid'][start: end]:
            uidlist.append(int(uid))
        net_dropout = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', uidlist)
        net_dropout.write_graphml(str(i) + 'dropout-tag-centrality2-rank.graphml')
    uidlist = [int(uid) for uid in dropouts['uid']]
    net_dropout = gt.load_hashtag_coocurrent_network_undir('fed', 'timeline', uidlist)
    net_dropout.write_graphml('dropout-tag-centrality2-rank-all.graphml')


def tfidf_stat():
    #ranking tag with tfidf
    gall = gt.Graph.Read_GraphML('dropout-tag-centrality2-rank-all.graphml')
    voc = dict(zip(gall.vs['name'], gall.vs['user']))
    for i in xrange(2):
        g = gt.Graph.Read_GraphML(str(i) + 'dropout-tag-centrality2-rank.graphml')
        # Filter network
        nodes = g.vs.select(weight_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        nodes = g.vs.select(user_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        g.vs['tfidf'] = 0.0
        for v in g.vs:
            tf = float(v['user'])
            v['tfidf'] = tf/(voc[v['name']])
        g.write_graphml(str(i) + 'dropout-tag-centrality2-rank-tfidf.graphml')

def tag_similarity_group_conflit_all():
    # computer similarity of tags between whole group and
    from scipy import spatial
    # from sklearn.metrics.pairwise import cosine_similarity
    gall = gt.Graph.Read_GraphML('dropout-tag-emotion3-rank-all.graphml')
    gt.net_stat(gall)
    nodes = gall.vs.select(weight_gt=50)
    print 'Filtered nodes: %d' %len(nodes)
    gall = gall.subgraph(nodes)
    nodes = gall.vs.select(user_gt=50)
    print 'Filtered nodes: %d' %len(nodes)
    gall = gall.subgraph(nodes)
    gt.net_stat(gall)
    voc = dict(zip(gall.vs['name'], gall.vs['user']))
    gs = []
    # for i in xrange(3):
    #     g = gt.Graph.Read_GraphML(str(i) + 'dropout-tag-emotion3-rank.graphml')
    #     nodes = g.vs.select(weight_gt=10)
    #     print 'Filtered nodes: %d' %len(nodes)
    #     g = g.subgraph(nodes)
    #     nodes = g.vs.select(user_gt=10)
    #     print 'Filtered nodes: %d' %len(nodes)
    #     g = g.subgraph(nodes)
    #     gvoc = dict(zip(g.vs['name'], g.vs['user']))
    #     gs.append(gvoc)
    #
    # vockeys = set(voc.keys())
    # for gvoc in gs:
    #     glist = [gvoc.get(key, 0) for key in voc.keys()]
    #     print 1 - spatial.distance.cosine(glist, voc.values())
    #     # print cosine_similarity(glist, voc.values())
    #     gkeys = set(gvoc.keys())
    #     print 1.0*len(vockeys.intersection(gkeys))/len(vockeys.union(gkeys))


def tag_similarity_group_dropout_emotion():
    # computer similarity of tags between whole group and
    from scipy import spatial
    # from sklearn.metrics.pairwise import cosine_similarity

    ds = []
    for i in ['tfidfnondropout-tag.graphml', 'tfidfdropout-tag.graphml']:
        g = gt.Graph.Read_GraphML(i)
        nodes = g.vs.select(weight_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        nodes = g.vs.select(user_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        gvoc = dict(zip(g.vs['name'], g.vs['tfidf']))
        ds.append(gvoc)

    gs = []
    for i in xrange(2):
        g = gt.Graph.Read_GraphML(str(i) + 'dropout-tag-centrality2-rank-tfidf.graphml')
        nodes = g.vs.select(weight_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        nodes = g.vs.select(user_gt=50)
        print 'Filtered nodes: %d' %len(nodes)
        g = g.subgraph(nodes)
        gvoc = dict(zip(g.vs['name'], g.vs['tfidf']))
        gs.append(gvoc)

    for d in ds:
        dkeys = set(d.keys())
        for g in gs:
            gkeys = set(g.keys())
            print '-----------------'
            print '%.3f' %(1.0*len(dkeys.intersection(gkeys))/len(dkeys.union(gkeys)))

            allkeys = dkeys.union(gkeys)
            dlist = [d.get(key, 0) for key in allkeys]
            glist = [g.get(key, 0) for key in allkeys]
            print '%.3f' %(1 - spatial.distance.cosine(dlist, glist))



if __name__ == '__main__':

    # print diff_day(datetime(2010, 10,1), datetime(2010,9,1))
    # from lifelines.utils import k_fold_cross_validation
    # count_longest_tweeting_period('fed', 'timeline', 'com')
    # count_longest_tweeting_period('random', 'timeline', 'scom')
    # count_longest_tweeting_period('younger', 'timeline', 'scom')
    # read_user_time('user-durations-2.csv')
    read_user_time_iv('user-durations-iv-following-senti.csv')
    # cluster_hashtag()

    # insert_timestamp('fed2', 'com')
    # network1 = gt.Graph.Read_GraphML('coreed-net.graphml')
    # gt.summary(network1)
    # network1_gc = gt.giant_component(network1)
    # gt.summary(network1_gc)

    # compare_dropouts_withemotions()
    # tfidf_stat()
    # tag_similarity_group()
    # tfidf_stat_dropout()
    # tag_similarity_group_dropout_emotion()
    # tag_similarity_group_conflit_all()