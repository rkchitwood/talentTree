from models import db, Function, Level

def seed_functions():
    '''creates immutable functions'''
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
        Function(name='Customer Services')
    ]
    db.session.add_all(functions)
    db.session.commit()
    

def seed_levels():
    '''creates immutable levels'''

    chief = Level(name='Chief')
    president = Level(name='President')
    evp = Level(name='Executive Vice President')
    svp = Level(name='Senior Vice President')
    vp = Level(name='Vice President')
    director = Level(name='Director')
    manager = Level(name='Manager')
    associate = Level(name='Associate')
    analyst = Level(name='Analyst')
    junior = Level(name='Junior')

def should_seed():
    '''Check if there are any existing records in Function and Level tables'''
    function_count = Function.query.count()
    level_count = Level.query.count()
    return function_count == 0 and level_count == 0