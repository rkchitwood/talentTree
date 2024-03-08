from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import and_, UniqueConstraint
bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    '''connects to database'''
    db.app=app
    db.init_app(app)
    db.drop_all()
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

class Profile(db.Model):
    '''table for profiles'''

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    linkedin_url = db.Column(db.Text, nullable = False, unique=True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    headline = db.Column(db.String(50), nullable = False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=False)
    __table_args__ = (
        UniqueConstraint('linkedin_url', 'organization_id'),
    )

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

# class Map(db.Model):
#     '''table for contact maps'''

#     __tablename__ = 'maps'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(50), nullable = False)
#     level = db.Column(db.Integer, db.ForeignKey('levels.id', ondelete='SET NULL', nullable=False))

#     #map-companies and map-levels