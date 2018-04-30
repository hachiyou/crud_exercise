from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


@app.route('/')
def restaurantMenu():
    """ Display the first restaurant's menu list. """
    session = DBSession()  # Prevent Threading error.
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    """ Displaying a specific restaurant.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """
    session = DBSession()  # Prevent Threading error.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)


if __name == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
