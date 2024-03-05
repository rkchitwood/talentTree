from models import db, Function, Level

def seed_functions():
    '''creates predefined functions'''

    functions = [
        Function(name='Executive'),
        Function(name='Finance'),
        Function(name='Operations'),
        Function(name='Engineering'),
        Function(name='Product'),
        Function(name='Sales'),
        Function(name='Security'),
        Function(name='Marketing'),
        Function(name='Human Resources'),
        Function(name='Customer Services'),
        Function(name='Founder')
    ]
    db.session.add_all(functions)
    db.session.commit()

def seed_levels():
    '''creates predefined levels'''
    
    levels = [
        Level(name='Chief'),
        Level(name='President'),
        Level(name='Executive Vice President'),
        Level(name='Senior Vice President'),
        Level(name='Vice President'),
        Level(name='Associate Vice President'),
        Level(name='Head'),
        Level(name='Partner'),
        Level(name='Senior Director'),
        Level(name='Director'),
        Level(name='Associate Director'),
        Level(name='Senior Manager'),
        Level(name='Manager'),
        Level(name='Senior Associate'),
        Level(name='Associate'),
        Level(name='Senior Analyst'),
        Level(name='Junior')
    ]
    db.session.add_all(levels)
    db.session.commit()

def should_seed():
    '''Check if there are any existing records in Function and Level tables'''
    
    function_count = Function.query.count()
    level_count = Level.query.count()
    return function_count == 0 and level_count == 0