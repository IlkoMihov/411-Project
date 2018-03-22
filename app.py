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

# twitter credentials
twitter = oauth.remote_app(
    'twitter',
    consumer_key='FSYI0zkB071Ry7XDh1H6vnout',
    consumer_secret='PYybNMYCabLM1xySQMsuhwvdY3nLaMBzGumgfXZCAjw4kpjy1V',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)

# initialize Cache
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


@app.route('/',methods=['GET'])
def index():
    # if user is authorized and logged in
    if g.user is not None:
        # call call_friends_list_api() function to get list of friends
        resp = call_friends_list_api()
        # filter result to get username and photo only
        friends = [{'username': user['screen_name'], 'photo': user['profile_image_url_https']} \
                   for user in resp['users']]
        # small edit needed on profile picture links in order to display image in html
        for friend in friends:
            if 'jpg' in friend['photo']:
                friend['photo']= friend['photo'][:-11] + '.jpg'
            elif 'jpeg' in friend['photo']:
                friend['photo'] = friend['photo'][:-12] + '.jpeg'

        # provide user with 10 questions
        # the list "all_choices" will store 10 lists of four random users
        all_choices = []

        # fill with number of questions to be used
        # these strings will serve as dictionary keys
        number_of_questions = ['one','two','three']

        # stores the authors of the tweets aka correct answers
        all_correct_answers = {}

        # store users and corresponding profile photos to dictionary
        users_and_photos = {}

        # fill in the "all_choices" list
        for question_number in number_of_questions:
            # get 4 random people from friends list
            four_choices = []
            while(len(four_choices) < 4):
                select = random.choice(friends)
                if select not in four_choices:
                    four_choices += [select]
            # create a list of their usernames
            users = [person['username'] for person in four_choices]
            # create a list of their profile pcitres
            profile_pictures = [person['photo'] for person in four_choices]

            for i in range(len(users)):
                users_and_photos[users[i]] = profile_pictures[i]

            # choose one of the four random users to be the correct answer
            correct_answer = random.choice(four_choices)['username']
            # save correct answer to all_correct_answers
            all_correct_answers[question_number] = correct_answer


            # call function from get_tweets.py
            twitterClass = getTweet(correct_answer)
            # this function on that file obtain a random tweet from the chosen user
            chosen_tweet = twitterClass.search()

            # this dictionary stores choices and answers information for each question
            question = {'photos':profile_pictures,'answer':correct_answer,'usernames':users,'chosen_tweet':chosen_tweet}
            # append to all_choices
            all_choices += [question]


        # session is a global dictionary
        # make dictionaries global
        session['correct_answers'] = all_correct_answers
        session['users_and_photos'] = users_and_photos



        # send data to start.html and load that template
        return render_template('start.html',one_img=all_choices[0]['photos'],one_tweet=all_choices[0]['chosen_tweet'],\
                               one_users = all_choices[0]['usernames'], \
                                two_img=all_choices[1]['photos'] ,two_tweet=all_choices[1]['chosen_tweet'], \
                               two_users=all_choices[1]['usernames'], \
                               three_img=all_choices[2]['photos'] ,three_tweet=all_choices[2]['chosen_tweet'], \
                three_users = all_choices[2]['usernames'] )
    else:
         return render_template('index.html')

# user is routed here after quiz answers are submitted
@app.route('/results',methods = ['POST'])
def results():
    you_answered = {}

    user_selected_one = request.form['one_answer']
    user_selected_two = request.form['two_answer']
    user_selected_three = request.form['three_answer']


    you_answered['one'] = {'username':user_selected_one,'photo':session['users_and_photos'][user_selected_one]}
    you_answered['two'] = {'username':user_selected_two,'photo':session['users_and_photos'][user_selected_two]}
    you_answered['three'] = {'username':user_selected_three,'photo':session['users_and_photos'][user_selected_three]}


    number_of_questions = ['one','two','three']

    # calculate number of correct answers
    number_of_correct_answers = 0

    for q in number_of_questions:
        if you_answered[q]['username'] == session['correct_answers'][q]:
            number_of_correct_answers+=1


    return render_template('results.html',one_your_answer = you_answered['one']['photo'], \
                           one_correct_answer = session['users_and_photos'][session['correct_answers']['one']],\
                           two_your_answer=you_answered['two']['photo'], \
                           two_correct_answer=session['users_and_photos'][session['correct_answers']['two']],\
                           three_your_answer=you_answered['three']['photo'], \
                           three_correct_answer=session['users_and_photos'][session['correct_answers']['three']],\
                           number_of_correct_answers=number_of_correct_answers,
                           number_of_questions=len(number_of_questions)


                           )

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
