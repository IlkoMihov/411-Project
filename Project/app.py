from flask import Flask,redirect,url_for,render_template
from flask_dance.contrib.twitter import make_twitter_blueprint,twitter
from get_tweets import twitterInfo
import random


# initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs411'

# initialize a cache to store friends list results from api call
from flask.ext.cache import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# authorize with Twitter
twitter_blueprint = make_twitter_blueprint(api_key='FSYI0zkB071Ry7XDh1H6vnout',\
                                           api_secret='PYybNMYCabLM1xySQMsuhwvdY3nLaMBzGumgfXZCAjw4kpjy1V')

app.register_blueprint(twitter_blueprint,url_prefix='/twitter')

# api call to get friends list
# stores in cache
@cache.cached(timeout=50, key_prefix='all_comments')
def get_friends():
    # an api call can only retrieve 20 users.
    # the commented code retrieves all users
    '''
    cursor = '-1'
    friends = []
    while cursor != 0:
        print(cursor)
        api_path = 'https://api.twitter.com/1.1/friends/list.json?cursor=' + cursor
        friends_list = twitter.get(api_path).json()
        friends += [user['screen_name'] for user in friends_list['users']]
        cursor = friends_list['next_cursor_str']
    '''
    # api path to get friends list
    api_path = 'https://api.twitter.com/1.1/friends/list.json'
    # api call
    friends_list = twitter.get(api_path).json()
    return friends_list

# login with Twitter
# !!currently does not have logout functionality!!
@app.route('/')
def authorize():
    if twitter.authorized:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('twitter.login'))

@app.route('/twitter')
def main():
    # call get_friends() function to get friends list
    call_get_friends = get_friends()
    # filter data to get username and profile photo only
    friends = [{'username':user['screen_name'],'photo':user['profile_image_url_https']} \
                 for user in call_get_friends['users']]

    # stores list of profile photos
    profile_pictures = []
    # gets profile photo strings
    for friend in friends:
        if 'jpg' in friend['photo']:
            profile_pictures += [friend['photo'][:-11] + '.jpg']
        elif 'jpeg' in friend['photo']:
            profile_pictures += [friend['photo'][:-12] + '.jpeg']
    # get random choice from list of friends
    random_user = random.choice(friends)['username']
    # call twitterInfo class from get_tweets.py
    twitterClass= twitterInfo(random_user)
    # call function to get a random tweet
    chosen_tweet = twitterClass.search()
    print(random_user)
    # return index.html and pass variables containing profile photos and tweets
    return render_template('index.html',profile_pictures=profile_pictures,tweet = chosen_tweet)




if __name__ == '__main__':
    app.run()
