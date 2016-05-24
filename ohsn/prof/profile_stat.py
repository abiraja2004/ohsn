# -*- coding: utf-8 -*-
"""
Created on 13:56, 18/02/16

@author: wt

Compare the difference from their prof information


"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ohsn.util import plot_util as plot
from ohsn.util import statis_util
import ohsn.util.io_util as io
import pickle
import numpy as np
import matplotlib.pyplot as plt


def liwc_feature_stat():
    fields = io.read_fields()
    # test_ids = np.array(pickle.load(open('test_ids.data', 'r')))
    # test_class = pickle.load(open('test_class.pick', 'r'))
    # test_class[test_class < 0] = 0
    # test_class = test_class.astype(bool)
    # targest_ids = test_ids[test_class]
    # print targest_ids.shape
    # pedsa = io.get_mlvs_field_values_uids('fed', targest_ids, 'liwc_anal.result.WC', 'liwc_anal.result')
    # fedsa = io.get_mlvs_field_values('fed', 'liwc_anal.result.WC', 'liwc_anal.result')
    # randomsa = io.get_mlvs_field_values('random', 'liwc_anal.result.WC', 'liwc_anal.result')
    # youngsa = io.get_mlvs_field_values('young', 'liwc_anal.result.WC', 'liwc_anal.result')
    # pickle.dump(fedsa, open('data/fedsa.pick', 'w'))
    # pickle.dump(randomsa, open('data/randomsa.pick', 'w'))
    # pickle.dump(youngsa, open('data/youngsa.pick', 'w'))
    # pickle.dump(pedsa, open('data/pedsa.pick', 'w'))
    fedsa = pickle.load(open('data/fedsa.pick', 'r'))
    randomsa = pickle.load(open('data/randomsa.pick', 'r'))
    youngsa = pickle.load(open('data/youngsa.pick', 'r'))
    pedsa = pickle.load(open('data/pedsa.pick', 'r'))
    print len(fedsa), len(randomsa), len(youngsa), len(pedsa)
    for field in fields:
        print '=====================', field
        keys = field.split('.')
        feds = io.get_sublevel_values(fedsa, keys[2])
        randoms = io.get_sublevel_values(randomsa, keys[2])
        youngs = io.get_sublevel_values(youngsa, keys[2])
        peds = io.get_sublevel_values(pedsa, keys[2])

        comm = statis_util.comm_stat(feds)
        print 'ED & ' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3]) + '\\\\'
        comm = statis_util.comm_stat(randoms)
        print 'Random &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        comm = statis_util.comm_stat(youngs)
        print 'Younger &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        comm = statis_util.comm_stat(peds)
        print 'PED &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        print '\\hline'

        z = statis_util.z_test(randoms, feds)
        print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, feds)
        print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(youngs, randoms)
        print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.z_test(feds, peds)
        print 'z-test(ED, PED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        print '\\hline'
        z = statis_util.ks_test(randoms, feds)
        print 'ks-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, feds)
        print 'ks-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, randoms)
        print 'ks-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(feds, peds)
        print 'ks-test(ED, PED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        plot.plot_pdf_mul_data([randoms, youngs, feds, peds],
                               ['--bo', '--r^', '--ks', '--g*'], field,
                               ['Random', 'Younger', 'ED', 'PED'], True, savefile='LIWC_'+keys[2]+'.pdf')
        # plot.plot_pdf_mul_data([randoms, youngs, feds],
        #                        ['--bo', '--r^', '--ks'], field,
        #                        ['Random', 'Younger', 'ED'], True, savefile='LIWC_'+keys[2]+'.pdf')


def profile_feature_stat():
    # 'favourites_count'
    fields = ['followers_count', 'friends_count', 'statuses_count']
    filter = {}
    fitranges = [[(200, 100000), (1000, 100000000), (800, 10000000)],
                     [(700, 10000), (800, 10000000), (800, 1000000)],
                     [(800, 100000), (20000, 10000000), (10000, 10000000)]]
    for i in range(len(fields)):
        field = fields[i]
        print '=====================', field
        feds = np.array(io.get_values_one_field('fed', 'scom', field, filter))+1
        randoms = np.array(io.get_values_one_field('random', 'scom', field, filter))+1
        youngs = np.array(io.get_values_one_field('young', 'scom', field, filter))+1

        comm = statis_util.comm_stat(feds)
        print 'ED & ' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3]) + '\\\\'
        comm = statis_util.comm_stat(randoms)
        print 'Random &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        comm = statis_util.comm_stat(youngs)
        print 'Younger &' + str(comm[0]) + ' & ' + str(comm[1]) \
              + ' & ' + str(comm[2])+ ' & ' + str(comm[3])+ '\\\\'
        print '\\hline'

        # z = statis_util.z_test(randoms, feds)
        # print 'z-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        # z = statis_util.z_test(youngs, feds)
        # print 'z-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$:' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        # z = statis_util.z_test(youngs, randoms)
        # print 'z-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
        #       + ' & z-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        z = statis_util.ks_test(randoms, feds)
        print 'ks-test(Random, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, feds)
        print 'ks-test(Younger, ED): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'
        z = statis_util.ks_test(youngs, randoms)
        print 'ks-test(Younger, Random): & $n_1$: ' + str(z[0]) + ' & $n_2$: ' + str(z[1]) \
              + ' & ks-value: ' + str(z[2])+ ' & p-value: ' + str(z[3])+ '\\\\'

        plot.plot_pdf_mul_data([feds, randoms, youngs], field, ['g', 'b', 'r'], ['s', 'o', '^'], ['ED', 'Random', 'Younger'],
                               linear_bins=False, central=False, fit=True, fitranges=fitranges[i], savefile=field+'.pdf')

def profile_feature_dependence():
    fields = ['friends_count', 'statuses_count', 'followers_count']
    for i in xrange(len(fields)):
        fi = fields[i]
        for j in xrange(i+1, len(fields)):
            fj = fields[j]
            print '=========================Dependence :', fi, fj
            ax = plt.gca()
            i = 0
            for db, color, mark, label in [('fed', 'g', 's', 'ED'),
                                           ('random', 'b', 'o', 'Random'),
                                           ('young', 'r', '^', 'Young')]:
                print '++++++++++++++++++++++++++Dependence :', fi, fj, db
                fivalue = np.array(io.get_values_one_field(db, 'scom', fi))
                fjvalue = np.array(io.get_values_one_field(db, 'scom', fj))
                fivalue += 1
                fjvalue += 1
                xmeans, ymeans = plot.mean_bin(fivalue, fjvalue)
                ax.scatter(xmeans, ymeans, s=50, c=color, marker=mark, label=label)
                fit_start = min(fivalue)
                fit_end = max(fivalue)
                # fit_start = np.percentile(fivalue, 2.5)
                # fit_end = np.percentile(fivalue, 97.5)
                xfit, yfit, cof = plot.lr_ls(xmeans, ymeans, fit_start, fit_end)
                ax.plot(xfit, yfit, c=color, linewidth=2, linestyle='--')
                ax.annotate(r'$k_y \propto {k_x}^{'+str(round(cof, 2))+'}$',
                 xy=(xfit[-15], yfit[-15]),  xycoords='data',
                 xytext=(28+(i)*10, -30-(i)*10), textcoords='offset points', fontsize=20,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                i += 1
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_ylabel(fj)
            ax.set_xlabel(fi)
            ax.set_xlim(xmin=1)
            ax.set_ylim(ymin=1)
            handles, labels = ax.get_legend_handles_labels()
            leg = ax.legend(handles, labels, loc=4)
            leg.draw_frame(True)
            plt.savefig(fi+'-'+fj+'.pdf')
            plt.clf()

if __name__ == '__main__':
    # liwc_feature_stat()
    profile_feature_stat()
    # profile_feature_dependence()

