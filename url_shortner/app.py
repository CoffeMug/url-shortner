import web
import os
from url_shortner import *

DATABASE='words.db'

render = web.template.render('templates/')

urls = ('/', 'index',
        '/result', 'result')

os.system("bin/create_and_populate_db.py")

class index:
    def GET(self):
        return render.index()

    def POST(self):
        url = web.input()
        extracted_words = url_to_words(url.title)
        original_url = trim_url(url.title) 
        shorten_url(DATABASE, extracted_words, original_url)
        short_url = fetch_short_url(original_url)
        return render.result(short_url, original_url)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()


