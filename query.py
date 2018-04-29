from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


def select_all_restaurant():
    """Return a list of restaurants stored in the database."""
    return session.query(Restaurant).all()


def add_restaurant(rname):
    """Add new restaurant to the database.

    Arg:
        rname (str): name of the restaurant
    """
    new_restaurant = Restaurant(name=rname)
    session.add(new_restaurant)
    session.commit()


def select_restaurant(r_id):
    """Return a single restaurant stored in the database that has the id.

    Arg:
        r_id (int): id of the restaurant
    Return:
        A single restaurant represented in Restaurant class
    """
    return session.query(Restaurant).filter_by(id=r_id).one()


def update_restaurant(r_id, new_name):
    """Change the name of a restaurant based on its id.

    Arg:
        r_id (int): id of the restaurant to be update
        new_name (str): new name of the restaurant
    Return:
        old_name: the old name of the restaurant
    """
    rest = select_restaurant(r_id)
    old_name = rest.name
    rest.name = new_name
    session.commit()
    return old_name


def delete_restaurant(r_id):
    """Remove a restaurant in the database that has the id.

    Arg:
        r_id (int): id of the restaurant to be removed
    Return:
        old_name (str): the name of the restaurant that was removed.
    """
    rest = select_restaurant(r_id)
    old_name = rest.name
    session.delete(rest)
    session.commit()
    return old_name
