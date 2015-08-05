import re
import sqlite3
import random 
import time
import datetime
from urlparse import urlparse

URL_SHORT = "http://myurlshortner.com/"
DOMAIN_SEPARATORS = "[, .]+"
WORD_SEPARATORS = "[, \-\/.!?_:]+"

def url_to_words(url):
    normal_url = trim_url(url)
    parsed_url = urlparse(normal_url)
    split_domain = filter(None, re.split(DOMAIN_SEPARATORS, parsed_url[1])) 
    words = filter(None, re.split(WORD_SEPARATORS, split_domain[0] + parsed_url[2]))
    extracted_words = [item for item in words if not item.isdigit()]
    return extracted_words

def trim_url(url):
    whitespace_less_url = url.replace(" ","")
    trimmed_url = whitespace_less_url.replace("www.", "")
    if not trimmed_url.startswith('http'):
        trimmed_url = '%s%s' % ('http://', trimmed_url)
    return trimmed_url

def shorten_url(db, words, orig_url):
    if already_in_db(db, orig_url):
       return

    sql = 'SELECT key,url,orig_url FROM words WHERE key=?'   
    result = sql_select(db, sql, words)

    if result:
        for item in result: 
            if item[2] == None:
                key = item[0] 
                update_db(db, key, orig_url)
                return
        key = pick_random_key(db, words, orig_url)
        update_db(db, key, orig_url)    
        return
    # there is no free key as part of url or it might already assigned
    else:
        key = pick_random_key(db, words, orig_url)
        update_db(db, key, orig_url)    

def pick_random_key(db, words, orig_url):
    sql = 'SELECT key,url,orig_url FROM words WHERE key IS NOT ? and orig_url IS NULL'   
    available_keys = sql_select(db, sql, words) 

    if available_keys: 
       key_list = random.choice(available_keys)
       return key_list[0]
    else:
       key_list = pick_oldest_key(db)
       return key_list[0][0] 

def pick_oldest_key(db):
    sql = 'SELECT key FROM words as a WHERE a.[dt] = (SELECT min([dt]) FROM words)'
    conn = sqlite3.connect(db)
    c = conn.cursor()    
    result = [] 
    try:
        c.execute(sql)
        for row in c:
            result.append(row)
    except sqlite3.OperationalError, msg:
        print msg 
    finally:
        conn.close()
    return result

def update_db(db, key, orig_url):
    short_url = build_short_url(key)
    sql = 'UPDATE words SET url=?, orig_url=?, dt=?  WHERE key=?'
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    try:
        c.execute(sql, (short_url, orig_url, datetime.datetime.now(), key))
        conn.commit()
    except sqlite3.OperationalError, msg:
        print msg 
    finally:
        conn.close()

def already_in_db(db, orig_url):
    sql = 'SELECT orig_url FROM words WHERE orig_url=?'   
    url = []
    url.append(orig_url)
    result = sql_select(db, sql, url)
    return result

def sql_select(db, sql, words):
    conn = sqlite3.connect(db)
    c = conn.cursor()    
    result = [] 
    try:
        for word in words:
            t = (word,)  
            c.execute(sql, t)
            for row in c:
                result.append(row)
    except sqlite3.OperationalError, msg:
        print msg 
    finally:
        conn.close()
    return result

def fetch_short_url(original_url):
    sql = 'SELECT url FROM words WHERE orig_url=?'   
    conn = sqlite3.connect('words.db')
    c = conn.cursor()    
    t = (original_url,)
    result = []  
    try:
        c.execute(sql, t)
        for row in c: result.append(row)
    except sqlite3.OperationalError, msg:
        print msg 
    finally:
        conn.close()
    return result[0][0]

def build_short_url(key):
    return URL_SHORT + key + "/"



