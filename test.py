import pandas as pd
import response
from response import query, rank_candidates
from collections import defaultdict
import math
from random import shuffle

response.DBNAME = 'data_test.db' # switch to a test db which will never be updated

behaviors = pd.read_csv('behaviors.tsv',sep='\t', header=None, nrows=100)
behaviors.columns = ['id','userId','time','history','candidates']
behaviors.time = pd.to_datetime(behaviors.time, format='%m/%d/%Y %I:%M:%S %p')
num = 10

def ndcg_cal(dk,topk):
    dcg_value = 0.
    idcg_value = 0.
    log_ki = []

    ddk = sorted(dk,reverse=True)

    for ki in range(0,min(topk,len(dk))):
        log_ki.append(math.log(ki+1,2) if math.log(ki+1,2) != 0. else 1.)
        dcg_value += dk[ki] / log_ki[ki]
        idcg_value += ddk[ki] / log_ki[ki]

    return dcg_value/idcg_value if idcg_value != 0 else 0

def evaluate(N,n):

    response.N = N
    response.n = n
    ndcg_m = 0
    ndcg_b = 0
    print('N=' + str(N) + ', n=' + str(n))

    for i,t in enumerate(behaviors.itertuples()):
        userId = t.userId
        date = str(t.time).split()[0]
        records = '' if isinstance(t.history,float) else t.history
        histories  = query("select NewsId, Category, `Sub-category` from news where NewsId in (" + ','.join(["'" + nid +"'" for nid in records.split()]) + ")")

        candidates, clicks = zip(*[tuple(c.split('-')) for c in t.candidates.split()])

        res_rand = [int(c) for c in clicks]
        shuffle(res_rand)

        clicks = {candidates[i] : int(clicks[i]) for i in range(len(clicks))}
        res = []

        candidates = query("""
            select n.NewsId, n.Category, n.`Sub-category`, n.title, n.Time, (select count(1) from history as h where h.newsId = n.NewsId) as cnt 
            from news as n where n.NewsId in (""" +   ','.join(["'" + nid +"'" for nid in candidates]) + """)""")

        if len(histories) == 0:
            res = sorted([(c[0],c[5]) for c in candidates],key=lambda x:x[-1],reverse=True)
        else:
            cands = defaultdict(list)
            for c in candidates:
                cands[(c[1],c[2])].append((c[0],c[5]))
            res = []
            ranked_cats = rank_candidates(userId,candidates,histories,date)

            for c in ranked_cats:
                l = cands[c[0]]
                if len(l) == 1:
                    res.append(l[0])
                else:
                    for x in sorted(l,key=lambda x:x[-1],reverse=True):
                        res.append(x)

        res = [clicks[r[0]] for r in res]

        ndcg_m_t = ndcg_cal(res,num)
        ndcg_b_t = ndcg_cal(res_rand,num)

        ndcg_m += ndcg_m_t
        ndcg_b += ndcg_b_t

        #print('model: ' + str(ndcg_m_t) + ' baseline: ' + str(ndcg_b_t))
        if i >= 100:
            break

    print('model all: ' + str(ndcg_m) + ' baseline all: ' + str(ndcg_b))

for n in [5,10]:
    for N in [10,20,30,40,50]:
        evaluate(N,n)





