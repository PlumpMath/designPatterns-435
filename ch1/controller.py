# when user enter shorten URL, return full url using Redirect function
# Request is used for encapsulation HTTP request
# modules for request method, request attributes, associated informations
from flask import redirect
from flask import render_template
from flask import request
from flask import Flask
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

import models

# Flask app init
app = Flask(__name__, template_folder='views')


@app.route("/")
def index():
    """main page rendering"""
    return render_template('main_page.html')


@app.route('/shorten/')
def shorten():
    """ returns short_url of requested full_url"""
    # validate user input
    full_url = request.args.get('url')
    if not full_url: # there's no full_url(?)
        raise BadRequest()

    # model which returns short_url property and object
    url_model = models.Url.shorten(full_url)

    # pass data to view and call rendering method
    short_url = request.host + '/' + url_model.short_url
    return render_template('success.html', short_url=short_url)


@app.route('/<path:path>')
def redirect_to_full_url(path=''):
    """get short url and when matched full url exist, redirect user to it"""
    # model which returns full_url property and object
    url_model = models.Url.get_by_short_url(path)
    # return verifying model
    if not url_model:
        raise NotFound()

    return redirect(url_model.full_url)

if __name__ == "__main__":
    app.run(debug=True)