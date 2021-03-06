from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItemm, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask import make_response
import httplib2
import json
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def showLogin():
    """Display a login page with Google Plus Login Button."""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect to Google OAuth2 API and retrieve user data."""
    # Match the current state with the login state.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        reponse.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Use the authroization code to make a credentials object.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        reponse.headers['Content-Type'] = 'application/json'
        return response

    # Validate the access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Abort the app if there is an error
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        reponse.headers['Content-Type'] = 'application/json'
        return response

    # Validate the access token id against the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dump("Toeken's user ID does not match given user ID."),
            401)
        reponse.headers['Content-Type'] = 'application/json'
        return response
    # Validate the access token id against the app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dump("Toeken's client ID does not match app's."),
            401)
        print("Token's client ID does not match app's.")
        reponse.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Test to see if the login user is in the database or not.
    user_id = getUserID(login_session['email'])
    # If yes, simply add the id to the current session.
    # If not, call createUser to add the new user.
    login_session['user_id'] = user_id
    if user_id
    else createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa
    flash("you are now logged in as %s" % login_session['email'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect the current user."""
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)

    # If the status code is 200,
    # remove all the data from current login session.
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def showRestaurant():
    """Display home page and a list of restaurants."""
    session = DBSession()  # Prevent threading error.
    restaurants = session.query(Restaurant)
    if len(restaurants) == 0:
        return render_template('index_empty.html')
    if 'email' not in login_session:
        return render_template('publicrestaurants.html',
                               restaurants=restaurants)
    else:
        user = getUserInfo(restaurant.user_id)
        return render_template('index.html',
                               restlist=restaurants, user=user)


@app.route('/restaurants/new',
           methods=['GET', 'POST'])
def newRestaurant():
    """Create a new restaurant."""

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')
    session = DBSession()  # Prevent threading error.
    restaurant = Restaurant(name="")
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("New restaurant created.")
        return redirect(url_for('showRestaurant'))
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit',
           methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    """ Edit the name of a restaurant.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')

    session = DBSession()  # Prevent threading error.

    editedRestaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    # If the current user is not the owner of the selected restaurant, alert.
    if editRestaurant.user_id != login_session['user_id']:
        return '''<script>function myFunction()
{alert('You are not authorized to edit this restaurant.');}
</script><body onload='myfunction' '>'''

    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
        session.add(editedRestaurant)
        session.commit()
        flash("Restaurant has been renamed!")
        return redirect(url_for('showRestaurant'))
    else:
        return render_template(
            'editrestaurant.html',
            restaurant_id=restaurant_id,
            r=editedRestaurant)


@app.route('/restaurants/<int:restaurant_id>/delete',
           methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    """ Delete the selected restaurant.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')

    session = DBSession()  # Prevent threading error.

    deleteRestaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()

    # If the current user is not the owner of the selected restaurant, alert.
    if restaurantToDelete.user_id != login_session['user_id']:
        return '''<script>function myFunction()
{alert('You are not authorized to delete this restaurant.');}
</script><body onload='myfunction' '>'''

    if request.method == 'POST':
        # First find all the menus that belong to this restaurant
        # Delete them one by one
        deleteMenus = session.query(MenuItem).filter_by(
            restaurant_id=restaurant_id).all()

        for m in deleteMenus:
            session.delete(m)
            session.commit

        # Then delete the resturant itself.
        session.delete(deleteRestaurant)
        session.commit()
        flash("Restaurant has been deleted!")
        return redirect(url_for('showRestaurant'))
    else:
        return render_template('deleterestaurant.html',
                               r=deleteRestaurant)


@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    """ Displaying a specific restaurant.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """
    session = DBSession()  # Prevent threading error.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)

    creator = getUserInfo(restaurant.user_id)

    if ('email' not in login_session or creator.id != login_session['user_id']):  # noqa
        return render_template('publicmenu.html',
                               items=items,
                               restaurant=restaurant,
                               creator=creator)

    else:
        return render_template('menu.html',
                               items=items,
                               restaurant=restaurant,
                               creator=creator)


@app.route('/restaurants/<int:restaurant_id>/menu/new',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """ Create a new menu.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')

    session = DBSession()  # Prevent threading error.
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """ Edit a selected menu item.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
        menu_id (int): obtain from the URL builder
                             as the id of the menu to look up
    """

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')

    session = DBSession()  # Prevent threading error.
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()

    # If the current user is not the creator of the selected menu, alert.
    if editedItem.user_id != login_session['user_id']:
        return '''<script>function myFunction()
{alert('You are not authorized to edit this menu item.');}
</script><body onload='myfunction' '>'''

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("menu item has been edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html',
            restaurant_id=restaurant_id,
            menu_id=menu_id,
            item=editedItem)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """ Delete the selected menu item.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
        menu_id (int): obtain from the URL builder
                             as the id of the menu to look up
    """

    # If there is no email in the login session AKA no current login user.
    if 'email' not in login_session:
        return redirect('/login')

    session = DBSession()  # Prevent threading error.
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()

    # If the current user is not the creator of the selected menu, alert.
    if deleteItem.user_id != login_session['user_id']:
        return '''<script>function myFunction()
{alert('You are not authorized to edit this menu item.');}
</script><body onload='myfunction' '>'''

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("menu item has been deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=deleteItem)


@app.route('/restaurant/JSON')
def restaurantJSON():
    """ Display all restaurnts in JSON format."""
    session = DBSession()  # Prevent threading error.
    restaurant = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    """ Display all the menus of a restaurnt in JSON format.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """
    session = DBSession()  # Prevent threading error.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def singleMenuItemJSON(restaurant_id, menu_id):
    """ Display a specific menu of a restaurnt in JSON format.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
        menu_id (int): obtain from the URL builder
                             as the id of the menu to look up
    """
    session = DBSession()  # Prevent threading error.
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


def createUser(login_session):
    """Create a user."""
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Find the user using the ID."""
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Find the id of the user given the email."""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:  # noqa
        return None


if __name__ == '__main__':
    app.secret_key = "super_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
