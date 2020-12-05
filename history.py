import sqlite3 as sqlite

DBNAME = 'data.db'

def query(statement):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    res = cur.fetchall()
    conn.close()
    return res

def get_history(userId,date):
    res = query("select NewsId, Category, `Sub-category`, title, Time from news where NewsId in (select newsId from history where userId='" + userId + "') and Time < '" + date + "' order by Time desc")
    return res