from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import and_, UniqueConstraint
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
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'))
    is_admin = db.Column(db.Boolean, nullable = True, default = False)

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
    def register(cls, email, password, organization_id, is_admin):
        '''registers a user'''
    
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(email=email, password=hashed_utf8, organization_id=organization_id, is_admin=is_admin)
    
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
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=False)
    token = db.Column(db.String(25), nullable=False, unique=True)
    expiration = db.Column(db.DateTime, nullable=False)
    pending_admin = db.Column(db.Boolean, nullable = True, default=False)
    

class Organization(db.Model):
    '''table for organizations'''

    __tablename__='organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"<Organization #{self.id}: {self.name}>"
        
class State(db.Model):
    '''table for US States'''

    __tablename__= 'states'

    id = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(30), unique=True)

class Country(db.Model):
    '''table for countries'''

    __tablename__ = 'countries'

    id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(56), unique=True)

class Profile(db.Model):
    '''table for profiles'''

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    linkedin_url = db.Column(db.Text, nullable = False, unique=True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    headline = db.Column(db.String(50), nullable = False)
    city = db.Column(db.String(50), nullable=True)
    state_id = db.Column(db.String(2), db.ForeignKey('states.id', ondelete='SET NULL'), nullable=True)
    country_id = db.Column(db.String(3), db.ForeignKey('countries.id', ondelete='SET NULL'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=False)
    __table_args__ = (
        UniqueConstraint('linkedin_url', 'organization_id'),
    )

    state = db.Relationship('State')
    country = db.Relationship('Country')

    def __repr__(self):
        return f"<Profile #{self.id}: {self.first_name} {self.last_name}, {self.linkedin_url}>"

    def primary_role(self):
        '''Returns the primary role of the profile'''
        return Role.query.filter_by(profile_id=self.id, is_primary=True).first()

class Function(db.Model):
    '''table for job functions'''

    __tablename__ = 'functions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)
        
class RoleFunction(db.Model):
    '''table tying functions to their roles'''

    __tablename__ = 'role_function'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='SET NULL'), primary_key = True)
    function_id = db.Column(db.Integer, db.ForeignKey('functions.id', ondelete='SET NULL'), primary_key = True)

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

    level = db.relationship('Level')
    profile = db.relationship('Profile')
    company = db.relationship('Company')
    functions = db.relationship('Function', secondary='role_function')

class Company(db.Model):
    '''table for companies'''

    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(30), nullable = False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=False)

    __table_args__ = (
        UniqueConstraint('domain', 'organization_id'),
    )

    employees = db.relationship('Profile', 
                               secondary='roles',
                               primaryjoin=and_(id == Role.company_id,
                                                Role.end_date == None), 
                               backref='current_company')
    alumni = db.relationship('Profile', 
                               secondary='roles',
                               primaryjoin=and_(id == Role.company_id,
                                                Role.end_date != None), 
                               backref='alumni_company')
    def __repr__(self):
        return f"<Company #{self.id}: {self.name}, {self.domain}>"

class Level(db.Model):
    '''table for levels of seniority'''

    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)

class Map(db.Model):
    '''table for contact maps'''

    __tablename__ = 'maps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id', ondelete='SET NULL'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'))

    functions = db.relationship('Function', secondary='function_map')
    companies = db.relationship('Company', secondary='company_map')
    level = db.relationship('Level')

    def generate_map_headers(self):
        '''returns the table headers for a contact map'''
        return [f'{self.level.name} {f.name} ' for f in self.functions]
    
    def generate_map_rows(self):
        '''returns rows for a map'''
        table = []
        for co in self.companies:
            row = [co]
            for function in self.functions:
                role = Role.query.filter(
                    Role.company_id == co.id,
                    Role.level_id == self.level_id,
                    Role.functions.any(Function.id == function.id),
                    Role.end_date == None
                ).first()
                if role:                                     
                    row.append(role.profile)
                else:
                    row.append(None)   
            table.append(row)
        return table

class FunctionMap(db.Model):
    '''table tying functions to contact maps'''

    __tablename__ = 'function_map'

    function_id = db.Column(db.Integer, db.ForeignKey('functions.id', ondelete='SET NULL'), primary_key = True)
    map_id = db.Column(db.Integer, db.ForeignKey('maps.id', ondelete='SET NULL'), primary_key = True)
    

class CompanyMap(db.Model):
    '''table tying companies to contact maps'''

    __tablename__ = 'company_map'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), primary_key = True)
    map_id = db.Column(db.Integer, db.ForeignKey('maps.id', ondelete='SET NULL'), primary_key = True)