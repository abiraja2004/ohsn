# -*- coding: utf-8 -*-
"""
Created on 16:00, 01/02/16

@author: wt

Conduct statistics on how much bio-information the data provides.
"""

from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import util.db_util as dbutil
import util.plot_util as plot


db = dbutil.db_connect_no_auth('echelon')
ed_poi = db['poi']

biolist =   ['text_anal.gw.value',
              'text_anal.cw.value',
              # 'text_anal.edword_count.value',
              'text_anal.h.value',
              'text_anal.a.value',
              'text_anal.lw.value',
              'text_anal.hw.value']
all_count = ed_poi.count({})


for name in biolist:
    print name ,ed_poi.count({name:{'$exists': True}}), ed_poi.count({name:{'$exists': True}})/float(all_count)

gws = []
cws = []
for user in ed_poi.find({'text_anal.gw.value':{'$exists': True},
                         'text_anal.cw.value':{'$exists': True}}):
    gws.append(user['text_anal']['gw']['value'])
    cws.append(user['text_anal']['cw']['value'])

#
# for user in ed_poi.find({'text_anal.cw.value':{'$exists': True}}):
#     gws.append(user['text_anal']['cw']['value'])

print min(gws), max(gws), len(gws)
print min(cws), max(cws), len(cws)
# plot.pdf_plot_one_data(gws, 'gw', 1, 1)
plot.pdf_plot_one_data(cws, 'cw', 1, 1)
# plot.plot_pdf_two_data(gws, cws, 'weight')