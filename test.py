import pandas as pd
import response
from response import query, rank_candidates
from collections import defaultdict

response.DBNAME = 'data_test.db'
response.N = 40
behaviors = pd.read_csv('behaviors.tsv',sep='\t', header=None, nrows=10)
behaviors.columns = ['id','userId','time','history','candidates']
behaviors.time = pd.to_datetime(behaviors.time, format='%m/%d/%Y %I:%M:%S %p')
num = 10

for i,t in enumerate(behaviors.itertuples()):
    userId = t.userId
    date = str(t.time).split()[0]
    histories  = query("select NewsId, Category, `Sub-category` from news where NewsId in (" + ','.join(["'" + nid +"'" for nid in t.history.split()]) + ")")
    if len(histories) == 0:
        res = sorted([(c[0],c[5]) for c in candidates],key=lambda x:x[-1],reverse=True)[:num]
        continue
    
    candidates, clicks = zip(*[tuple(c.split('-')) for c in t.candidates.split()])
    clicks = [int(c) for c in clicks]
    candidates = query("""
        select n.NewsId, n.Category, n.`Sub-category`, n.title, n.Time, (select count(1) from history as h where h.newsId = n.NewsId) as cnt 
        from news as n where n.NewsId in (""" +   ','.join(["'" + nid +"'" for nid in candidates]) + """)""")
    
    cands = defaultdict(list)
    for c in candidates:
        cands[(c[1],c[2])].append((c[0],c[5]))
    res = []
    ranked_cats = rank_candidates(userId,candidates,histories,date)
    
    cnt = 0
    for c in ranked_cats:
        if cnt >= num:
            break
        l = cands[c[0]]
        if len(l) == 1:
            res.append(l[0])
            cnt += 1
        else:
            for x in sorted(l,key=lambda x:x[-1],reverse=True):
                res.append(x)
                cnt += 1
                if cnt >= 5:
                    break

    print(res)
    if i >=2:
        break



