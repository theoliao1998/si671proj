import sqlite3 as sqlite

DBNAME = 'data.db'

def query(statement):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    res = cur.fetchall()
    conn.close()
    return res

def replace_user(userId):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    cur.execute("replace INTO users VALUES(?)",(userId,))
    conn.commit()
    conn.close()

def add_click(userId, newsId):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    cur.execute("replace INTO history VALUES(?,?)",(userId,newsId))
    conn.commit()
    conn.close()

def get_history(userId,date):
    res = query("select NewsId, Category, `Sub-category`, title, Time, URL from news where NewsId in (select newsId from history where userId='" + userId + "') and Time < '" + date + "' order by Time desc")
    if len(res) == 0:
        replace_user(userId)
    return res


