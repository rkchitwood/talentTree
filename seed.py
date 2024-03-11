from models import db, Function, Level, State, Country

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

def seed_states():
    '''creates predefined US states'''
    
    us_states = [
        {'id': 'AL', 'name': 'Alabama'},
        {'id': 'AK', 'name': 'Alaska'},
        {'id': 'AZ', 'name': 'Arizona'},
        {'id': 'AR', 'name': 'Arkansas'},
        {'id': 'CA', 'name': 'California'},
        {'id': 'CO', 'name': 'Colorado'},
        {'id': 'CT', 'name': 'Connecticut'},
        {'id': 'DE', 'name': 'Delaware'},
        {'id': 'FL', 'name': 'Florida'},
        {'id': 'GA', 'name': 'Georgia'},
        {'id': 'HI', 'name': 'Hawaii'},
        {'id': 'ID', 'name': 'Idaho'},
        {'id': 'IL', 'name': 'Illinois'},
        {'id': 'IN', 'name': 'Indiana'},
        {'id': 'IA', 'name': 'Iowa'},
        {'id': 'KS', 'name': 'Kansas'},
        {'id': 'KY', 'name': 'Kentucky'},
        {'id': 'LA', 'name': 'Louisiana'},
        {'id': 'ME', 'name': 'Maine'},
        {'id': 'MD', 'name': 'Maryland'},
        {'id': 'MA', 'name': 'Massachusetts'},
        {'id': 'MI', 'name': 'Michigan'},
        {'id': 'MN', 'name': 'Minnesota'},
        {'id': 'MS', 'name': 'Mississippi'},
        {'id': 'MO', 'name': 'Missouri'},
        {'id': 'MT', 'name': 'Montana'},
        {'id': 'NE', 'name': 'Nebraska'},
        {'id': 'NV', 'name': 'Nevada'},
        {'id': 'NH', 'name': 'New Hampshire'},
        {'id': 'NJ', 'name': 'New Jersey'},
        {'id': 'NM', 'name': 'New Mexico'},
        {'id': 'NY', 'name': 'New York'},
        {'id': 'NC', 'name': 'North Carolina'},
        {'id': 'ND', 'name': 'North Dakota'},
        {'id': 'OH', 'name': 'Ohio'},
        {'id': 'OK', 'name': 'Oklahoma'},
        {'id': 'OR', 'name': 'Oregon'},
        {'id': 'PA', 'name': 'Pennsylvania'},
        {'id': 'RI', 'name': 'Rhode Island'},
        {'id': 'SC', 'name': 'South Carolina'},
        {'id': 'SD', 'name': 'South Dakota'},
        {'id': 'TN', 'name': 'Tennessee'},
        {'id': 'TX', 'name': 'Texas'},
        {'id': 'UT', 'name': 'Utah'},
        {'id': 'VT', 'name': 'Vermont'},
        {'id': 'VA', 'name': 'Virginia'},
        {'id': 'WA', 'name': 'Washington'},
        {'id': 'WV', 'name': 'West Virginia'},
        {'id': 'WI', 'name': 'Wisconsin'},
        {'id': 'WY', 'name': 'Wyoming'}
    ]
    
    states_objects = [State(id=state['id'], name=state['name']) for state in us_states]
    
    db.session.add_all(states_objects)
    db.session.commit()

def seed_countries():
    '''seeds US and UK'''
    countries = [
        Country(id='USA', name='The United States of America'),
        Country(id='GBR', name='The United Kingdom of Great Britain and Northern Ireland')
    ]

    db.session.add_all(countries)
    db.session.commit()

def should_seed():
    '''Check if there are any existing records in Function and Level tables'''
    
    function_count = Function.query.count()
    level_count = Level.query.count()
    state_count = State.query.count()
    country_count = Country.query.count()
    return function_count == 0 and level_count == 0 and state_count == 0 and country_count == 0