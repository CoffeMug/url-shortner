import sqlite3
import os
from nose.tools import *
from url_shortner.url_shortner import *

DATABASE='mock_words.db'

#================================================================================
def setup_function():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE WORDS                                                                                     
       (id integer primary key autoincrement not null,                                                                 
        key           text,                                                                                            
        url           text,                                                                                            
        orig_url      text,                                                                                            
        dt            datetime default current_timestamp   );''')
    c = conn.cursor()
    with open('bin/normal_words_small.txt') as f:
        for line in f:
            c.execute("""INSERT INTO WORDS (key) VALUES (?)""", (line.rstrip('\n'),))
    f.close()
    conn.commit()
    conn.close()

def teardown_function():
    os.remove(DATABASE)
#================================================================================

def test_build_short_url():
    key='amin'
    result = build_short_url(key)
    assert_equal(result, "http://myurlshortner.com/amin/")
    
def test_url_to_words():
    url = "http://testurl.com/12/test/24"
    words = url_to_words(url)
    assert_equal(words, ['testurl','test'])

    url = "http://techcrunch.com/2012/12/28/pinterest-lawsuit/"
    words = url_to_words(url)
    assert_equal(words, ['techcrunch','pinterest','lawsuit'])

    # test url with whitespaces
    url = "  http://  testurl.com  "
    words = url_to_words(url)
    assert_equal(words, ['testurl'])

    # test url with www
    url = "http://www.testurl.com"
    words = url_to_words(url)
    assert_equal(words, ['testurl'])

    # test url with underscore
    url = "http://www.testurl_this_is_a_test.com"
    words = url_to_words(url)
    assert_equal(words, ['testurl', 'this', 'is', 'a', 'test'])

    # without http
    url = "www.testurl_this_is_a_test.com"
    words = url_to_words(url)
    assert_equal(words, ['testurl', 'this', 'is', 'a', 'test'])

def test_trim_url():
    url = "http://amin.co.uk/123/test"
    trimmed_url = trim_url(url)
    assert_equal(trimmed_url, "http://amin.co.uk/123/test")

    url = "  http: //a min.co. uk/1 23/te  st  "
    trimmed_url = trim_url(url)
    assert_equal(trimmed_url, "http://amin.co.uk/123/test")

    url = "  http: //w ww. a min.co. uk/1 23/te  st  "
    trimmed_url = trim_url(url)
    assert_equal(trimmed_url, "http://amin.co.uk/123/test")

@with_setup(setup_function, teardown_function)
def test_sql_select():
    words = ['amin', 'reza']
    sql = "SELECT key FROM words WHERE key=?"
    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [(u'amin',), (u'reza',)])

    words = ['jojo']
    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [])

    words = ['jojo','joachim']
    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [(u'joachim',)])

    words = ['reza']
    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [(u'reza',)])

@with_setup(setup_function, teardown_function)
def test_update_db():
    key = 'amin'
    orig_url = "http://www.amin.com"

    update_db(DATABASE, key, orig_url)

    sql = "SELECT key,orig_url FROM words WHERE key=?"
    words = ['amin']

    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [(key, orig_url)])

@with_setup(setup_function, teardown_function)
def test_already_in_db():
    key = 'joachim'
    orig_url = "http://www.swatch.com"

    update_db(DATABASE, key, orig_url)

    sql = "SELECT orig_url FROM words WHERE orig_url=?"
    words = [orig_url]
    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [(orig_url,)])

@with_setup(setup_function, teardown_function)
def test_pick_oldest_key():
    keys = ['joachim', 'reza', 'amin']
    
    for key in keys:
        update_db(DATABASE, key, 'http://test.com/' + key )
        time.sleep(2)
    
    result = pick_oldest_key(DATABASE)
    assert_equal(result, [('joachim',)])


@with_setup(setup_function, teardown_function)
def test_shorten_url():
    sql = 'SELECT key,url,orig_url FROM words WHERE key=?'
    words = ['nima', 'amin']
    orig_url = "http://nima_amin.com/1234"
    shorten_url(DATABASE, words, orig_url)

    result = sql_select(DATABASE, sql, words)
    assert_equal(result, [('amin', 'http://myurlshortner.com/amin/', 'http://nima_amin.com/1234')])

    sql = 'SELECT key,url,orig_url FROM words WHERE orig_url=?'
    words = ['swatch']
    orig_url = "http://www.swatch.se/"
    shorten_url(DATABASE, words, orig_url)

    result = sql_select(DATABASE, sql, ['http://www.swatch.se/'])
    assert_is_not(result, [])
    assert_equal(result[0][2], 'http://www.swatch.se/') 

    words = ['google']
    orig_url = "http://www.google.co.uk/"
    shorten_url(DATABASE, words, orig_url)

    words = ['digikala', 'niaz']
    orig_url = "http://www.niaz_digikala.ir/"
    shorten_url(DATABASE, words, orig_url)

    sql = 'SELECT key,url,orig_url FROM words WHERE orig_url=?'
    result = sql_select(DATABASE, sql, ['http://www.niaz_digikala.ir/'])
    assert_equal(result[0][0], 'amin')


