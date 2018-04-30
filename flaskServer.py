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
    session = DBSession()  # Prevent threading error.
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
    session = DBSession()  # Prevent threading error.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """ Create a new menu.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
    """
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


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """ Edit a selected menu item.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
        menu_id (int): obtain from the URL builder
                             as the id of the menu to look up
    """
    session = DBSession()  # Prevent threading error.
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("menu item has been edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """ Delete the selected menu item.

    Arg:
        restaurant_id (int): obtain from the URL builder
                             as the id of the restaurant to look up
        menu_id (int): obtain from the URL builder
                             as the id of the menu to look up
    """
    session = DBSession()  # Prevent threading error.
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("menu item has been deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=deleteItem)


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


if __name == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
