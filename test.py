from unittest import TestCase
from seed import seed_countries, seed_functions, seed_levels, seed_states, should_seed
from app import app, CURR_USER_KEY
from models import db, User, Organization, Company, Profile, Role, Map, Level, Function, RoleFunction
from flask import session

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///talenttree_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS']=['dont-show-deubg-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class AppTestCase(TestCase):
    '''tests views for model creation'''
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            db.drop_all()
            db.create_all()            
            if should_seed():
                seed_functions()
                seed_levels()
                seed_states()
                seed_countries()
    
    def setUp(self):
        '''cleanup and setup'''
        with app.app_context():
            RoleFunction.query.delete()
            Role.query.delete()
            Company.query.delete()
            Profile.query.delete()            
            User.query.delete()
            Organization.query.delete()                
            
            test_organization = Organization(name='test org')
            db.session.add(test_organization)
            db.session.commit()
            self.organization_id = test_organization.id

            test_user = User.registerAdmin(email='test@test.com', password='password', organization_id = self.organization_id)
            db.session.add(test_user)
            db.session.commit()
            self.email = test_user.email

            test_company = Company(name='Test Company', domain='http://www.faketestcompany.com/', organization_id=self.organization_id)
            db.session.add(test_company)
            db.session.commit()
            self.company_id = test_company.id

            test_profile = Profile(linkedin_url='https://www.linkedinfaketestprofile.com/',
                                   first_name='Test', 
                                   last_name='Jones',
                                   headline='CEO/COO at Test Company',
                                   country_id='USA',
                                   organization_id=self.organization_id
                                   )
            db.session.add(test_profile)
            db.session.commit()
            self.profile_id = test_profile.id

            test_role = Role(company_id=self.company_id, 
                             level_id=Level.query.filter_by(name='Chief').first().id,
                             profile_id = self.profile_id,
                             start_date = '01/01/2001',
                             is_primary = True                            
                             )
            db.session.add(test_role)
            db.session.commit()
            self.role_id = test_role.id


            functions = ['Executive', 'Operations']
            for f in functions:
                function_id = Function.query.filter_by(name=f).first().id
                role_function = RoleFunction(
                    role_id = self.role_id,
                    function_id = function_id
                    )
                db.session.add(role_function)
            db.session.commit()

            self.client = app.test_client()

    def tearDown(self):
        '''clean up any fouled transaction'''
        with app.app_context():
            db.session.rollback()

    def test_base(self):
        '''tests base route'''
        with self.client as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.email
            response = client.get('/')
            self.assertEqual(response.status_code, 302)
            response = client.get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn("test org Users", html)

    def test_signup(self):
        '''tests signup route'''
        with self.client as client:
            response = client.post('/signup', 
                                   data={'email' : 'secondtest@test.com', 'password' : 'password', 'confirm_password' : 'password', 'organization' : '2nd test org'}, 
                                   follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn("2nd test org Users", html)
            response = client.post('/signup', 
                                   data={'email' : 'third@test.com', 'password' : 'password', 'confirm_password' : 'password', 'organization' : '2nd test org'}, 
                                   follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertNotIn('2nd test org Users', html)





