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
@cache.cached(timeout=50, key_prefix='api_call')
def call_friends_list_api():
    # each api call gets the latest 20 following
    cursor = -1
    api_path = 'https://api.twitter.com/1.1/friends/list.json'
    resp = []
    for i in range(2):
        url_with_cursor = api_path + "?cursor=" + str(cursor)
        response_dictionary = twitter.get(url_with_cursor).data
        if 'errors' in response_dictionary:
            return render_template('error.html')
        cursor = response_dictionary['next_cursor']
        resp += [response_dictionary]
    return resp

#came with documentation code
@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']
#came with documentation code
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
        friends = []
        for obj in resp:
            # filter result to get username and photo only
            friends += [{'username': user['screen_name'], 'photo': user['profile_image_url_https']} \
                       for user in obj['users']]
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
        number_of_questions = ['one','two','three','four','five','six','seven','eight','nine','ten']

        # stores the authors of the tweets aka correct answers
        all_correct_answers = {}

        # store users and corresponding profile photos to dictionary
        users_and_photos = {}

        # fill in the "all_choices" list
        for question_number in number_of_questions:
            # get 4 random people from friends list
            three_choices = []
            while(len(three_choices) < 3):
                select = random.choice(friends)
                if select not in three_choices:
                    three_choices += [select]

            # create a list of their usernames
            users = [person['username'] for person in three_choices]
            # create a list of their profile pcitres
            profile_pictures = [person['photo'] for person in three_choices]

            for i in range(len(users)):
                users_and_photos[users[i]] = profile_pictures[i]

            # choose one of the three random users to be the correct answer
            correct_answer = random.choice(three_choices)['username']
            # save correct answer to all_correct_answers

            # call function from get_tweets.py
            twitterClass = getTweet(correct_answer)
            # this function on that file obtain a random tweet from the chosen user
            chosen_tweet = twitterClass.search()

            all_correct_answers[question_number] = {'tweet':chosen_tweet,'user':correct_answer}
            # this dictionary stores choices and answers information for each question
            question = {'photos':profile_pictures,'answer':correct_answer,'usernames':users,'chosen_tweet':chosen_tweet}
            # append to all_choices
            all_choices += [question]


        # session is a global dictionary
        # make dictionaries global
        session['correct_answers'] = all_correct_answers
        session['users_and_photos'] = users_and_photos



        # send data to start.html and load that template
        return render_template('start.html',one_img=all_choices[0]['photos'],one_tweet=all_choices[0]['chosen_tweet'],
                               one_users = all_choices[0]['usernames'],

                                two_img=all_choices[1]['photos'] ,two_tweet=all_choices[1]['chosen_tweet'],
                               two_users=all_choices[1]['usernames'],

                               three_img=all_choices[2]['photos'] ,three_tweet=all_choices[2]['chosen_tweet'],
                three_users = all_choices[2]['usernames'],

                               four_img=all_choices[3]['photos'], four_tweet=all_choices[3]['chosen_tweet'],
                               four_users=all_choices[3]['usernames'],

                               five_img=all_choices[4]['photos'], five_tweet=all_choices[4]['chosen_tweet'],
                               five_users=all_choices[4]['usernames'],

                               six_img=all_choices[5]['photos'], six_tweet=all_choices[5]['chosen_tweet'],
                               six_users=all_choices[5]['usernames'],

                               seven_img=all_choices[6]['photos'], seven_tweet=all_choices[6]['chosen_tweet'],
                               seven_users=all_choices[6]['usernames'],

                               eight_img=all_choices[7]['photos'], eight_tweet=all_choices[7]['chosen_tweet'],
                               eight_users=all_choices[7]['usernames'],

                               nine_img=all_choices[8]['photos'], nine_tweet=all_choices[8]['chosen_tweet'],
                               nine_users=all_choices[8]['usernames'],

                              ten_img=all_choices[9]['photos'], ten_tweet=all_choices[9]['chosen_tweet'],
                               ten_users=all_choices[9]['usernames'],

                               )
    else:
         return render_template('index.html')

# user is routed here after quiz answers are submitted
@app.route('/results',methods = ['POST'])
def results():
    you_answered = {}

    # get answers that user selected

    user_selected_one = request.form['one_answer']
    user_selected_two = request.form['two_answer']
    user_selected_three = request.form['three_answer']
    user_selected_four = request.form['four_answer']
    user_selected_five = request.form['five_answer']
    user_selected_six = request.form['six_answer']
    user_selected_seven = request.form['seven_answer']
    user_selected_eight = request.form['eight_answer']
    user_selected_nine = request.form['nine_answer']
    user_selected_ten = request.form['ten_answer']

    # get answers that user selected
    you_answered['one'] = {'username':user_selected_one,'photo':session['users_and_photos'][user_selected_one]}
    you_answered['two'] = {'username':user_selected_two,'photo':session['users_and_photos'][user_selected_two]}
    you_answered['three'] = {'username':user_selected_three,'photo':session['users_and_photos'][user_selected_three]}
    you_answered['four'] = {'username':user_selected_four,'photo':session['users_and_photos'][user_selected_four]}
    you_answered['five'] = {'username':user_selected_five,'photo':session['users_and_photos'][user_selected_five]}
    you_answered['six'] = {'username':user_selected_six,'photo':session['users_and_photos'][user_selected_six]}
    you_answered['seven'] = {'username':user_selected_seven,'photo':session['users_and_photos'][user_selected_seven]}
    you_answered['eight'] = {'username':user_selected_eight,'photo':session['users_and_photos'][user_selected_eight]}
    you_answered['nine'] = {'username':user_selected_nine,'photo':session['users_and_photos'][user_selected_nine]}
    you_answered['ten'] = {'username':user_selected_ten,'photo':session['users_and_photos'][user_selected_ten]}

    number_of_questions = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

    # calculate number of correct answers
    number_of_correct_answers = 0
    for q in number_of_questions:
        if you_answered[q]['username'] == session['correct_answers'][q]['user']:
            number_of_correct_answers+=1

    # calculate score and message to user
    score = number_of_correct_answers / len(number_of_questions)
    if score >= .8:
        results_msg = 'Awesome job!'
    elif score >=.6:
        results_msg = 'Not bad!'
    else:
        results_msg = 'Better luck next time!'

    # get all the correct answers from global dictionary
    one_correct_answer = session['users_and_photos'][session['correct_answers']['one']['user']]
    two_correct_answer = session['users_and_photos'][session['correct_answers']['two']['user']]
    three_correct_answer = session['users_and_photos'][session['correct_answers']['three']['user']]
    four_correct_answer = session['users_and_photos'][session['correct_answers']['four']['user']]
    five_correct_answer = session['users_and_photos'][session['correct_answers']['five']['user']]
    six_correct_answer = session['users_and_photos'][session['correct_answers']['six']['user']]
    seven_correct_answer = session['users_and_photos'][session['correct_answers']['seven']['user']]
    eight_correct_answer = session['users_and_photos'][session['correct_answers']['eight']['user']]
    nine_correct_answer = session['users_and_photos'][session['correct_answers']['nine']['user']]
    ten_correct_answer = session['users_and_photos'][session['correct_answers']['ten']['user']]


    return render_template('results.html',
                           number_of_correct_answers=number_of_correct_answers,
                           number_of_questions=len(number_of_questions),
                           results_msg=results_msg,

                           one_your_answer = you_answered['one']['photo'],
                           one_correct_answer = one_correct_answer,
                           one_tweet = session['correct_answers']['one']['tweet'],

                           two_your_answer=you_answered['two']['photo'],
                           two_correct_answer=two_correct_answer,
                           two_tweet=session['correct_answers']['two']['tweet'],

                           three_your_answer=you_answered['three']['photo'],
                           three_correct_answer=three_correct_answer,
                           three_tweet=session['correct_answers']['three']['tweet'],

                           four_your_answer=you_answered['four']['photo'],
                           four_correct_answer=four_correct_answer,
                           four_tweet=session['correct_answers']['four']['tweet'],

                           five_your_answer=you_answered['five']['photo'],
                           five_correct_answer=five_correct_answer,
                           five_tweet=session['correct_answers']['five']['tweet'],

                           six_your_answer=you_answered['six']['photo'],
                           six_correct_answer=six_correct_answer,
                           six_tweet=session['correct_answers']['six']['tweet'],

                           seven_your_answer=you_answered['seven']['photo'],
                           seven_correct_answer=seven_correct_answer,
                           seven_tweet=session['correct_answers']['seven']['tweet'],

                           eight_your_answer=you_answered['eight']['photo'],
                           eight_correct_answer=eight_correct_answer,
                           eight_tweet=session['correct_answers']['eight']['tweet'],

                           nine_your_answer=you_answered['nine']['photo'],
                           nine_correct_answer=nine_correct_answer,
                           nine_tweet=session['correct_answers']['nine']['tweet'],

                           ten_your_answer=you_answered['ten']['photo'],
                           ten_correct_answer=ten_correct_answer,
                           ten_tweet=session['correct_answers']['ten']['tweet'],

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
