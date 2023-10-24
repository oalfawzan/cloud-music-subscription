from flask import Flask, render_template, request, session, url_for, redirect
import boto3 
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = b'osama'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1',
aws_access_key_id='######',
aws_secret_access_key='######',
aws_session_token='######')

def query_login(email): 
#    if not dynamodb:
#       dynamodb = boto3.resource('dynamodb')
   table = dynamodb.Table('login')
   response = table.query(KeyConditionExpression=Key('email').eq(email))
   return response['Items']

def new_user(fullname, password, email):
    table = dynamodb.Table('login')
    response = table.put_item(
        Item={
        'email': email,
        'user_name': fullname,
        'password': password
        })

def subscribe(title, artist, year, image, email, username):
    # if not dynamodb:
    #     dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    subscription = {
        'title': title,
        'artist': artist,
        'year': year,
        'image': image
    }
    response = table.update_item(
        Key={'email': email, 'user_name': username},
        UpdateExpression='SET #subs = list_append(if_not_exists(#subs, :empty_list), :sub)',
        ExpressionAttributeNames={'#subs': 'subscriptions'},
        ExpressionAttributeValues={':sub': [subscription], ':empty_list': []},
        ReturnValues='UPDATED_NEW'
    )
    return response

def view_subs(email):
    # dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    response = table.query(
        KeyConditionExpression=Key('email').eq(email),
        ProjectionExpression='subscriptions'
    )
    items = response['Items']
    if not items:
        return []
    return items[0].get('subscriptions', [])

def remove_subscription(title, artist, year, email, username):
    # if not dynamodb:
    #     dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    subscription = {
        'title': title,
        'artist': artist,
        'year': year,
    }
    response = table.get_item(
        Key={
            'email': email,
            'user_name': username
        }
    )
    item = response.get('Item')
    subs = item.get('subscriptions')
    index = -1
    for i, sub in enumerate(subs):
        if all(sub[key] == subscription[key] for key in subscription):
            index = i
            break
    subs.pop(index)
    response = table.update_item(
        Key={
            'email': email,
            'user_name': username
        },
        UpdateExpression='SET #subs = :val',
        ExpressionAttributeNames={
            '#subs': 'subscriptions'
        },
        ExpressionAttributeValues={
            ':val': subs
        },
        ReturnValues='UPDATED_NEW'
    )
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = query_login(email)
        if account:
            msg = 'The email already exists!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            new_user(username, password, email)
            msg = 'You have successfully registered! You can now login'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        account = query_login(email)
        if account:
            if password == account[0]['password']:
                session['loggedin'] = True
                session['id'] = account[0]['email']
                session['username'] = account[0]['user_name']
                return redirect(url_for('index'))
            else:
                msg = 'Email or password is invalid!'
        else:
            msg = 'Email or password is invalid!'
    return render_template('login.html', msg=msg)

@app.route("/logout")
def logout():
    session['loggedin'] = False
    return render_template('login.html')

@app.route('/query')
def query():
    # dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    title = request.args.get('title')
    artist = request.args.get('artist')
    year = request.args.get('year')
    filter_expression = None
    if title and not artist and not year:
        filter_expression = Attr('title').contains(title)
    elif artist and not title and not year:
        filter_expression = Attr('artist').contains(artist)
    elif year and not title and not artist:
        filter_expression = Attr('year').eq(year)
    elif title and artist and not year:
        filter_expression = Attr('title').contains(title) & Attr('artist').contains(artist)
    elif title and year and not artist:
        filter_expression = Attr('title').contains(title) & Attr('year').eq(year)
    elif artist and year and not title:
        filter_expression = Attr('artist').contains(artist) & Attr('year').eq(year)
    elif title and artist and year:
        filter_expression = Attr('title').contains(title) & Attr('artist').contains(artist) & Attr('year').eq(year)
    else:
        no_results = 'No result is retrieved. Please query again.'
        if session['loggedin'] == False:
            msg = ''
            return render_template('home.html', msg=msg, no_results=no_results)
        elif session['loggedin'] == True:
            msg = 'Welcome Back, ' + session['username']
            return render_template('home.html', msg=msg, no_results=no_results)
    response = table.scan(FilterExpression=filter_expression)
    results = response['Items']
    if session['loggedin']:
        sub_list = view_subs(session['id'])
    for result in results:
        image_url = "https://s3905369.s3.amazonaws.com/" + result['artist'].replace(' ', '') + ".jpg"
        result['image_url'] = image_url
    if results:
        if session['loggedin'] == False:
            msg = ''
            return render_template('home.html', msg=msg, results=results)
        elif session['loggedin'] == True:
            msg = 'Welcome Back, ' + session['username']
            return render_template('home.html', msg=msg, results=results, sub_list=sub_list)
    else:
        no_results = 'No result is retrieved. Please query again.'
        if session['loggedin'] == False:
            msg = ''
            return render_template('home.html', msg=msg, no_results=no_results)
        elif session['loggedin'] == True:
            msg = 'Welcome Back, ' + session['username']
            return render_template('home.html', msg=msg, no_results=no_results, sub_list=sub_list)
        
@app.route('/subscribe', methods=['POST'])
def add_subscription():
    title = request.form['title']
    artist = request.form['artist']
    year = request.form['year']
    image = request.form['image']
    email = session['id']
    username = session['username']
    sub_list = view_subs(email)

    for sub in sub_list:
        if sub.get('title') == title and sub.get('artist') == artist and sub.get('year') == year:
            query_msg = 'You have already subscribed to this title!'
            msg = 'Welcome Back, ' + session['username']
            sub_list = view_subs(session['id'])
            return render_template('home.html', msg=msg, query_msg=query_msg, sub_list=sub_list)

    subscribe(title, artist, year, image, email, username)
    query_msg = 'You have subscribed successfully!'
    msg = 'Welcome Back, ' + session['username']
    sub_list = view_subs(session['id'])
    return render_template('home.html', msg=msg, query_msg=query_msg, sub_list=sub_list)

@app.route('/remove', methods=['POST'])
def remove():
    if request.method == 'POST':
        email = session['id']
        username = session['username']
        title = request.form['title']
        artist = request.form['artist']
        year = request.form['year']
        remove_subscription(title, artist, year, email, username)
        return redirect(url_for('index'))
    
@app.route('/', methods=["GET", "POST"])
def index():
    if 'loggedin' not in session:
        session['loggedin'] = False

    if session['loggedin']:
        sub_list = view_subs(session['id'])
        msg = 'Welcome Back, ' + session['username']
        return render_template('home.html', msg=msg, sub_list=sub_list)
    else:
        msg = ''
        return render_template('home.html', msg=msg)
    
if __name__ == '__main__':
  app.run(host="0.0.0.0")