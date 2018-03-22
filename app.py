# coding: utf-8

from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
from get_tweets import getTweet
import random


app = Flask(__name__)
app.debug = True
app.secret_key = 'cs411'

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='FSYI0zkB071Ry7XDh1H6vnout',
    consumer_secret='PYybNMYCabLM1xySQMsuhwvdY3nLaMBzGumgfXZCAjw4kpjy1V',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)

# initialize Cache module
from flask.ext.cache import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Call friends/list Twitter API and cache results
@cache.cached(timeout=50, key_prefix='all_comments')
def call_friends_list_api():
    resp = twitter.get('friends/list.json').data
    return resp


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/')
def index():
    # if user is authorized and logged in
    if g.user is not None:
        # call call_friends_list_api() function to get list of friends
        resp = call_friends_list_api()
        # filter result to get username and photo only
        friends = [{'username': user['screen_name'], 'photo': user['profile_image_url_https']} \
                   for user in resp['users']]
        # edit profile picture strings so we can display image in html
        for friend in friends:
            if 'jpg' in friend['photo']:
                friend['photo']= friend['photo'][:-11] + '.jpg'
            elif 'jpeg' in friend['photo']:
                friend['photo'] = friend['photo'][:-12] + '.jpeg'

        # get 4 random people from friends list
        four_choices = []
        while(len(four_choices) < 4):
            select = random.choice(friends)
            if select not in four_choices:
                four_choices += [select]
        # get list of their profile photos
        profile_pictures = [person['photo'] for person in four_choices]
        # choose one of the four random users to be the correct answer
        correct_answer = random.choice(four_choices)['username']
        # obtain a random tweet from the chosen user
        twitterClass = getTweet(correct_answer)
        chosen_tweet = twitterClass.search()
        # send data to templates/start.html
        return render_template('start.html', profile_pictures = profile_pictures,chosen_tweet=chosen_tweet,correct_answer=correct_answer)
    else:
        return render_template('index.html')



@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
