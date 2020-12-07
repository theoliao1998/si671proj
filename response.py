import sqlite3 as sqlite
from history import get_history
import numpy as np
import math
from collections import defaultdict


DBNAME = 'data.db'
N = 20
n = 5
rate = 0.8
num = 5
cache = {}
cats = {}

def query(statement):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    res = cur.fetchall()
    conn.close()
    return res

def get_candidates(date):
    return query("select n.NewsId, n.Category, n.`Sub-category`, n.title, n.Time, n.URL, (select count(1) from history as h where h.newsId = n.NewsId) as cnt  from news as n where n.Time = '" + date + "'")

def get_score(userId,category,subcategory,date):
    if (userId,category,subcategory) in cache:
        return cache[(userId,category,subcategory)]

    #print(cats)
    if (category,subcategory) not in cats[userId]:
        return 0

    cnts = query("""
    select count(1) as cnt, a.time from (
    select (select CAST ((julianday('""" + date+ """') - julianday(n.Time))/(365/12) AS INTEGER)
    from news as n where n.NewsId = h.newsId) as time from history as h where h.userId = '""" + userId +"""' 
    and h.newsId in (select n.NewsId from news as n where n.Category='""" + category + """' and n.`Sub-category`='""" + subcategory + """' 
    and n.Time < '""" + date + """') ) as a group by a.time
    """)
    #print('done')
    res = 0
    for c in cnts:
        res += c[0] * math.pow(rate,c[1])
    #res = int(round(res))
    cache[(userId,category,subcategory)] = res
    return res

def get_sum_score(userId,date):
    if userId in cache:
        return cache[userId] 
    
    cnts = query("""
    select count(1) as cnt, a.time from (
    select (select CAST ((julianday('""" + date+ """') - julianday(n.Time))/(365/12) AS INTEGER)
    from news as n where n.NewsId = h.newsId) as time from history as h where h.userId = '""" + userId +"""' 
    and h.newsId in (select n.NewsId from news as n where n.Time < '""" + date + """') ) as a group by a.time
    """)
    #print('done')
    res = 0
    for c in cnts:
        res += c[0] * math.pow(rate,c[1])
    #res = int(round(res))
    if res == 0:
        res = 1
    cache[userId] = res 
    return res

def norm(vector):
    return math.sqrt(sum(x * x for x in vector))    

def get_cosine_similarity(vec_a, vec_b):
    norm_a = norm(vec_a)
    norm_b = norm(vec_b)
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    s = norm_a * norm_b
    return dot / (norm_a * norm_b) if s != 0 else 0

def add_cats(users, date):
    for uid in users:
        res = query("""select DISTINCT n.Category, n.`Sub-category` from news as n where n.NewsId in (select newsId from history where userId='""" + uid + """')
        and n.Time < '""" + date +"""'
        """)
        cats[uid] = set(res)

def rank_candidates(userId, candidates, histories, date):
    if len(histories) == 0:
        return None

    cache.clear()
    cats.clear()

    cats_cand = {(c[1],c[2]) for c in candidates}
    cats_viewed = {(h[1],h[2]) for h in histories}
    users = [x[0] for x in query("select userId from users where userId!='" + userId + "' order by RANDOM()  LIMIT " + str(N-1))]
    add_cats(users,date)
    users.append(userId)
    cats[userId] = cats_viewed

    scores_cand = {c : [get_score(u, c[0], c[1], date) for u in users] for c in cats_cand}
    #print(scores_cand)
    scores_cand = {k: np.array([100 * x / get_sum_score(users[i],date) for i,x in enumerate(scores_cand[k])]) for k in scores_cand}
    #print(scores_cand)
    scores_viewed = {c : [get_score(u, c[0], c[1], date) for u in users] for c in cats_viewed}
    scores_viewed = {k: np.array([100 * x / get_sum_score(users[i],date) for i,x in enumerate(scores_viewed[k])]) for k in scores_viewed}
    preds = []
    for cat in cats_cand:
        sim = sorted([(c,get_cosine_similarity(scores_cand[cat],scores_viewed[c])) for c in cats_viewed],key=lambda x:x[1],reverse=True)
        if len(sim) > n:
            sim = sim[:n] 
        mu = (sum([sum(scores_viewed[k]) for k in scores_viewed]) + sum(scores_cand[cat])) / (len(users) * (len(scores_viewed) + 1))
        bx = (scores_cand[cat][-1] + sum([scores_viewed[k][-1] for k in scores_viewed])) / (1 + len(scores_viewed)) - mu
        bi = {k : sum(scores_viewed[k]) / len(users) - mu for k in scores_viewed}
        bi[cat] = sum(scores_cand[cat]) / len(users) - mu
        pred = 0
        for s in sim:
            bxj = mu + bx + bi[s[0]]
            pred += s[1] * (scores_viewed[s[0]][-1] - bxj)

        s = sum([s[1] for s in sim])
        pred = (pred / s) if s != 0 else 0 +  mu + bx + bi[cat]
        preds.append((cat,pred))
    
    return sorted(preds, key=lambda x:x[1], reverse=True)



def get_response(userId,date):
    candidates = get_candidates(date)
    histories = get_history(userId,date)

    if len(histories) == 0:
        res = sorted(candidates,key=lambda x:x[-1],reverse=True)[:num]
        return res
    
    cands = defaultdict(list)
    for c in candidates:
        cands[(c[1],c[2])].append(c)
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
                if cnt >= num:
                    break

    return res

# print(query("select power(0.8,3)"))