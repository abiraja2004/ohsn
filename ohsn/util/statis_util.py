# -*- coding: utf-8 -*-
"""
Created on 7:53 PM, 2/19/16

@author: tw
The util for statistics

"""
import numpy as np
import math
import scipy.stats as stats


def z_test(list1, list2):
    # z-test for two lists
    n1, n2 = len(list1), len(list2)
    mu1, mu2 = np.mean(list1), np.mean(list2)
    s1, s2 = np.std(list1), np.std(list2)
    z = (mu1-mu2)/(np.sqrt(s1**2/n1 + s2**2/n2))
    from scipy.stats import norm
    pval = 2*(1 - norm.cdf(abs(z)))
    return n1, n2, round(z, 3), round(pval, 4)


def ks_test(list1, list2):
    d, p = stats.ks_2samp(list1, list2)
    return len(list1), len(list2), round(d, 3), round(p, 4)


def comm_stat(lista):
    # return the min, max, mean and std
    return round(np.amin(lista), 2), round(np.amax(lista), 2), round(np.mean(lista), 2), round(np.std(lista),2)


def mode(lst):
    # find the mode of a list
    return max(set(lst), key=lst.count)

def tau_coef(x1, x2):
    tau, p_value = stats.kendalltau(x1, x2)
    return (tau, p_value)


def pearson(x, y):
    # calculate the pearson correlation of two list
    n = len(x)
    avg_x = float(sum(x))/n
    avg_y = float(sum(y))/n
    diffprod = 0.0
    xdiff2 = 0.0
    ydiff2 = 0.0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff*ydiff
        xdiff2 += xdiff*xdiff
        ydiff2 += ydiff*ydiff
    return diffprod/math.sqrt(xdiff2*ydiff2)

if __name__ == '__main__':
    l1 = [1,2,6,7,8,10,3,4,5,9]
    l2 = [1,2,3,4,5,6,7,8,9,10]
    print z_test(l1, l2)
    print ks_test(l1, l2)
    print pearson(l1, l2)
    print stats.pearsonr(l1, l2)