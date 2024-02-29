#models: organization, user, profile, company, level, function + PAST role table

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    '''connects to database'''
    db.app=app
    db.init_app(app)
    #db.drop_all()
    db.create_all()

class User(db.Model):
    '''table for users and hosts methods for registering and authenticating'''

    __tablename__='users'

    email = db.Column(db.String(100), nullable = False, primary_key=True)
    password = db.Column(db.String(255), nullable = False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='cascade'))
    is_admin = db.Column(db.Boolean, nullable = True)

    organization = db.relationship('Organization', backref='users')

    def __repr__(self):
        return f"<User {self.email}, {self.organization}>"

    @classmethod
    def registerAdmin(cls, email, password, organization_id):
        """register admin user with hashed password and returns user instance"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(email=email, password=hashed_utf8, organization_id=organization_id, is_admin=True)
    
    @classmethod
    def register(cls, email, password, organization_id):
        '''registers a user'''
    
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(email=email, password=hashed_utf8, organization_id=organization_id)
    
    @classmethod
    def authenticate(cls, email, password):
        """validates user information and returns instance of user or false"""

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
class PendingUser(db.Model):
    '''table for pending users awaiting official registration'''

    __tablename__ = 'pending_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    token = db.Column(db.String(10), nullable=False, unique=True)
    expiration = db.Column(db.DateTime, nullable=False)
    

class Organization(db.Model):
    '''table for organizations'''

    __tablename__='organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    #logo_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Organization #{self.id}: {self.name}>"
    
    #potential other cats: desc., addy, contact, industry, size, logo, data, socials


class Profile(db.Model):
    '''table for profiles'''

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    linkedin_url = db.Column(db.Text, nullable = False, unique=True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    headline = db.Column(db.String(50), nullable = False)
    primary_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    primary_role = db.relationship('Role', foreign_keys=[primary_role_id], backref='primary_profile', uselist=False)
    roles = db.relationship('Role', backref='profile', lazy='dynamic')
    functions = db.relationship('Function', secondary='roles', backref='profiles')
    companies = db.relationship('Company', secondary='roles', backref='profiles')
    levels = db.relationship('Level', secondary='roles', backref='profiles')

    def __repr__(self):
        return f"<Profile #{self.id}: {self.first_name} {self.last_name}, {self.linkedin_url}>"

class Role(db.Model):
    '''table for roles - past and present'''

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id', ondelete='SET NULL'), nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='SET NULL'), nullable = True)
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = True)
    is_primary = db.Column(db.Boolean, default=False)

    functions = db.relationship('Function', secondary='role-function', backref='roles')

    def __repr__(self):
        function_names = ', '.join(f.name for f in self.functions)
        if len(self.functions) == 1:
            function_names = function_names[:-2]
        return f"<Role #{self.id}: {self.level.name}, {function_names} at {self.company.name} from {self.start_date} to {self.end_date}>"
    
class RoleFunction(db.Model):
    '''table tying functions to their roles'''

    __tablename__ = 'role-function'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='SET NULL'), primary_key = True)
    function_id = db.Column(db.Integer, db.ForeignKey('functions.id', ondelete='SET NULL'), primary_key = True)


class Company(db.Model):
    '''table for companies'''

    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(50), unique=True, nullable = False)
    name = db.Column(db.String(30), nullable = False)
    api_company_id = db.Column(db.Integer, db.ForeignKey('api_companies.id'), nullable = True)

    profiles = db.relationship('Profile', secondary='roles', backref='companies')
    roles = db.relationship('Role', backref='company', lazy='dynamic')

    def __repr__(self):
        return f"<Company #{self.id}: {self.name}, {self.domain}>"


class Level(db.Model):
    '''table for levels of seniority'''

    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)

    roles = db.relationship('Role', backref='level', lazy='dynamic')

class Function(db.Model):
    '''table for job functions'''

    __tablename__ = 'functions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)

    roles = db.relationship('Role', backref='function', lazy='dynamic')
    
class Search(db.Model):
    '''table for searches'''

    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id', ondelete='SET NULL'), nullable=True)
    function_id = db.Column(db.Integer, db.ForeignKey('functions.id', ondelete='SET NULL'), nullable=True)

    company = db.relationship('Company', backref='searches')
    level = db.relationship('Level', backref='searches')
    function = db.relationship('Function', backref='searches')
    search_profiles = db.relationship('SearchProfile', backref='searches')
    
    def __repr__(self):
        return f"<Search #{self.id}: {self.level.name}, {self.function.name} for {self.company.name}>"

class SearchProfiles(db.Model):
    '''table for profiles belonging to a search'''

    __tablename__ = 'search_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='SET NULL'), nullable = True)
    search_id  = db.Column(db.Integer, db.ForeignKey('searches.id', ondelete='SET NULL'), nullable = True)

    #if chose to do library:
    #lib will only have id and description maybe author
    #lib roles, roles to find
    #display as grid, y axis companies x axis roles