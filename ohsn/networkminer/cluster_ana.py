# -*- coding: utf-8 -*-
"""
Created on 10:51, 06/06/17

@author: wt
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import ohsn.util.graph_util as gt
import ohsn.util.db_util as dbt
import ohsn.util.io_util as iot
import pandas as pd
import numpy as np
import pickle
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import ohsn.util.plot_util as plu


def net_attr(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''network statistics'''
    user_net = gt.Graph.Read_GraphML(filename)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    gt.summary(user_net)
    gt.net_stat(user_net)
    gt.net_stat(cluster1)
    gt.net_stat(cluster2)


def sentiment_quanti(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    # TODO analysis sentiment of different groups of users for hashtags
    print ''


def regression(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Regression for pro-ed and pro-recovery users'''
    user_net = gt.Graph.Read_GraphML(filename)
    cluster1 = user_net.subgraph(user_net.vs(cluster=0))
    cluster2 = user_net.subgraph(user_net.vs(cluster=1))
    cluster1_uid = cluster1.vs['name']
    cluster2_uid = cluster2.vs['name']
    fw = open('data/cluster-feature.data', 'w')
    # print cluster1_uid
    # print cluster2_uid

    com = dbt.db_connect_col('fed', 'com')
    fields = iot.read_fields()
    trimed_fields = [field.split('.')[-1] for field in fields]
    data = []
    for i, ulist in enumerate([cluster1_uid, cluster2_uid]):
        for uid in ulist:
            user = com.find_one({'id': int(uid), 'liwc_anal.result.WC': {'$exists': True}})
            if user:
                values = iot.get_fields_one_doc(user, fields)
                data.append([uid, i] + values)
                outstr = str(i) + ' '
                for j in xrange(len(values)):
                    outstr += str(j+1)+':'+str(values[j])+' '
                fw.write(outstr+'\n')
    df = pd.DataFrame(data, columns=['uid', 'label']+trimed_fields)
    df.to_csv('data/cluster-feature.csv')
    fw.close()


def assortative_test(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Test assortative of network in terms of cluster assignments'''
    g = gt.Graph.Read_GraphML(filename)
    raw_values = np.array(g.vs['cluster'])
    raw_assort = g.assortativity('cluster', 'cluster', directed=True)
    modu = g.modularity(g.vs['cluster'], weights='weight')
    print raw_assort, modu
    ass_list = list()
    for i in xrange(3000):
        np.random.shuffle(raw_values)
        g.vs["cluster"] = raw_values
        ass_list.append(g.assortativity('cluster', 'cluster', directed=True))
    ass_list = np.array(ass_list)
    amean, astd = np.mean(ass_list), np.std(ass_list)

    absobserved = abs(raw_assort)
    pval = (np.sum(ass_list >= absobserved) +
            np.sum(ass_list <= -absobserved))/float(len(ass_list))
    zscore = (raw_assort-amean)/astd
    if pval < 0.05:
        mark = '*'
    if pval < 0.01:
        mark = '**'
    if pval < 0.001:
        mark = '***'
    print ('Raw assort: %.3f, mean: %.3f std: %.3f z: %.3f, p: %.100f %s' %(raw_assort, amean, astd, zscore, pval, mark))


def interaction_ratio(filename='data/communication-only-fed-filter-hashtag-cluster.graphml'):
    '''Test interaction of different clusters of users, see political polariztion on twitter'''
    g = gt.Graph.Read_GraphML(filename)
    a = g.vs(cluster=0)
    b = g.vs(cluster=1)

    la = len(a)
    lb = len(b)

    sa = sum(g.es.select(_source_in = a)['weight'])
    sb = sum(g.es.select(_source_in = b)['weight'])

    aa = sum(g.es.select(_source_in = a, _target_in = a)['weight'])
    ab = sum(g.es.select(_source_in = a, _target_in = b)['weight'])
    ba = sum(g.es.select(_source_in = b, _target_in = a)['weight'])
    bb = sum(g.es.select(_source_in = b, _target_in = b)['weight'])

    eaa = float(sa)*(la)/(la+lb)
    eab = float(sa)*(lb)/(la+lb)
    eba = float(sb)*(la)/(la+lb)
    ebb = float(sb)*(lb)/(la+lb)

    print ('A: %d B: %d ' %(len(a), len(b)))
    print ('%d %d %d %d ' %(aa, ab, ba, bb))
    print ('%.2f %.2f %.2f %.2f ' %(eaa, eab, eba, ebb))
    print ('%.3f %.3f %.3f %.3f ' %(float(aa-eaa)/eaa, float(ab-eab)/eab, float(ba-eba)/eba, float(bb-ebb)/ebb))
    # print ('%.3f %.3f %.3f %.3f ' %(float(aa)/eaa, float(ab)/eab, float(ba)/eba, float(bb)/ebb))


def prominence(filename='data/communication-only-fed-filter-hashtag-cluster.graphml',
               tagfile='data/user-hash-vector.pick'
                ):
    # TODO calculate the prominence of hashtag
    g = gt.Graph.Read_GraphML(filename)
    user_tag = pickle.load(open(tagfile, 'r')) # {'uid': 'tag1 tag2 tag3'}

    uid_lable = dict(zip(g.vs['name'], g.vs['cluster']))
    clusterA, clusterB = [], []
    clusterA_user_no, clusterB_user_no = [], [] #count how many users have used a tag
    for uid in user_tag.keys():
        tag_list = user_tag[uid].split()
        if uid_lable[str(uid)] == 0:
            clusterA += tag_list
            clusterA_user_no += list(set(tag_list))
        elif uid_lable[str(uid)] == 1:
            clusterB += tag_list
            clusterB_user_no += list(set(tag_list))
        else:
            print 'not existing cluster'
    NA = len(clusterA)
    NB = len(clusterB)
    NALL = NA + NB

    Acounter = Counter(clusterA)
    Bcounter = Counter(clusterB)
    Allcounter = Counter(clusterA + clusterB) # counting how many times of a tag being used
    Allcounter_user = Counter(clusterA_user_no + clusterB_user_no) # counting how many users using a tag

    tags = set(Acounter.keys() + Bcounter.keys())
    valance = {}
    for tag in tags:
        '''Self defined values'''
        # if Allcounter.get(tag, 0) > 3 and Allcounter_user.get(tag, 0) > 3:
        #     fa = Acounter.get(tag, 0)
        #     fb = Bcounter.get(tag, 0)
        #     pa = float(fa)/NA
        #     pb = float(fb)/NB
        #     pall = pa + pb
        #     if pall > 0:
        #         v = ((pb - pa)/(pa + pb))
        #         if pb >= pa:
        #             v *= np.log(fb)
        #         else:
        #             v *= np.log(fa)
        #         valance[tag] = v
        #         print tag, fa, fb, v
        #     else:
        #         print tag, '-------------------------------------'
        '''PMI'''
        TALL = Allcounter.get(tag, 0)
        if TALL > 3 and Allcounter_user.get(tag, 0) > 3:
            fa = Acounter.get(tag, 0)
            fb = Bcounter.get(tag, 0)
            if fa>0:
                pmiA = np.log(float(fa*NALL)/(TALL*NA))/(-np.log(float(fa)/NALL))
                # pmiA = np.log(float(fa*NALL)/(TALL*NA))
            else:
                pmiA = 0
            if fb > 0:
                pmiB = np.log(float(fb*NALL)/(TALL*NB))/(-np.log(float(fb)/NALL))
                # pmiB = np.log(float(fb*NALL)/(TALL*NB))
            else:
                pmiB = 0
            value = pmiB - pmiA
            valance[tag] = value
            print tag, fa, fb, TALL, pmiA, pmiB, value
            # if fa > 0:
            #     pmiB = np.log(float(fa*NALL)/(TALL*NA))/(-np.log(float(fa)/NALL))
            # else:
            #     pmiB = 0
            # valance[tag] = pmiB

    # pickle.dump(valance, open('data/hashtag-valance.pick', 'w'))
    # valance = pickle.load(open('data/hashtag-valance.pick', 'r'))
    plu.plot_config()
    x = valance.values()
    # print np.min(x), np.percentile(x, 25), np.percentile(x, 50), np.percentile(x, 75), np.max(x)

    # bin = np.linspace(min(x), max(x), 100)
    sns.distplot(x)
    plt.xlabel(r'PI(h)')
    plt.ylabel('PDF')
    plt.show()

if __name__ == '__main__':
    # net_attr()
    # regression()
    # assortative_test()
    # interaction_ratio()
    prominence()