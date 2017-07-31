import collections
import json
import math
import sys

[inp] = sys.argv[1:]

results = json.load(open(inp))

cold = collections.defaultdict(list)
hot = collections.defaultdict(list)
for result in results:
    counts = set(result[k] for k in result if k.endswith('_count'))
    #assert len(counts) == 1, (counts, result)
    for k in result:
        if k.endswith('_cold_t'):
            cold[k[:-7]].append(float(result[k]))
        elif k.endswith('_hot_t'):
            hot[k[:-6]].append(float(result[k]))

def mean(l):
    return sum(v for v in l)/len(l)

def gmean(l):
    return math.exp(sum(math.log(v) for v in l)/len(l))

names = sorted(cold)
for i, name in enumerate(names):
    print name, mean(cold[name]), gmean(cold[name]), mean(hot[name]), gmean(hot[name])
    if i:
        print ' '*len(name),
        print mean(cold[name])/mean(cold[names[0]]), gmean(cold[name])/gmean(cold[names[0]]),
        print mean( hot[name])/mean( hot[names[0]]), gmean( hot[name])/gmean( hot[names[0]])
        rname = "%s/%s" % (names[0], names[i])
        for result in results:
            for name in names:
                cold[rname].append(float(result[names[0]+'_cold_t'])/result[names[i]+'_cold_t'])
                hot[rname].append( float(result[names[0]+'_hot_t'])/ result[names[i]+'_hot_t'])
        print ' '*len(name),
        print rname, mean(cold[rname]), mean(hot[rname]), gmean(cold[rname]), gmean(hot[rname])
        rname = "slow %s/%s" % (names[0], names[i])
        for result in results:
            for name in names:
                if max(result[names[0]+'_cold_t'], result[names[i]+'_cold_t']) >= 1000.0:
                    cold[rname].append(float(result[names[0]+'_cold_t'])/result[names[i]+'_cold_t'])
                if max(result[names[0]+'_hot_t'], result[names[i]+'_hot_t']) >= 1000.0:
                    hot[rname].append( float(result[names[0]+'_hot_t'])/ result[names[i]+'_hot_t'])
        print ' '*len(name),
        print rname, mean(cold[rname]), mean(hot[rname]), gmean(cold[rname]), gmean(hot[rname])
        rname = "very slow %s/%s" % (names[0], names[i])
        for result in results:
            for name in names:
                if max(result[names[0]+'_cold_t'], result[names[i]+'_cold_t']) >= 5000.0:
                    cold[rname].append(float(result[names[0]+'_cold_t'])/result[names[i]+'_cold_t'])
                if max(result[names[0]+'_hot_t'], result[names[i]+'_hot_t']) >= 5000.0:
                    hot[rname].append( float(result[names[0]+'_hot_t'])/ result[names[i]+'_hot_t'])
        print ' '*len(name),
        print rname, mean(cold[rname]), mean(hot[rname]), gmean(cold[rname]), gmean(hot[rname])
