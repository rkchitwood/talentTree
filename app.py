from flask import Flask, session, g, redirect, render_template, flash
from flask_mail import Mail, Message
from secret import GMAIL_USERNAME, GMAIL_PASSWORD
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Organization
from sqlalchemy.exc import IntegrityError
from forms import FirstAdminForm
from seed import should_seed, seed_functions, seed_levels

CURR_USER_KEY = "curr_user"
REGISTER = '/users/new/register'

app = Flask(__name__)

app.config['SECRET_KEY']='key'
debug=DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///talenttree'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL']  = True
app.config['MAIL_USERNAME'] = GMAIL_USERNAME
app.config['MAIL_PASSWORD'] = GMAIL_PASSWORD

mail = Mail(app)

with app.app_context():
    connect_db(app)

with app.app_context():
    if should_seed():
        seed_functions()
        seed_levels()

def email_registration(email, token):
    '''sends email to pending user so that they can sign up using the token-embedded link'''

    msg = mail.send_message(
        'Time Sensitive: Welcome to talentTree!',
        sender = GMAIL_USERNAME,
        recipients = [email],
        body=f'''
        Welcome to talentTree! Please click the following link
        to complete registration: 
        {REGISTER}/{token}
        '''
    )

def email_confirm_registration(email):
    '''sends email to new user verifying successful signup'''

    msg = mail.send_message(
        'Registration Successful',
        sender = GMAIL_USERNAME,
        recipients = [email],
        body=f'''
        Welcome to talentTree!

        Thank you for joining talentTree, we hope you enjoy our product.
        For your records, your username is:

        {email}

        Thank you again!
        -the talentTree team
        '''
    )

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.email


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.route('/')
def home():
    '''displays info page or redirects to user's org home'''

    if g.user:
        return redirect(f'/organizations/{g.user.organization_id}')
    else:
        return render_template('home.html')

@app.route('/register/admin', methods=['GET', 'POST'])
def register_first_admin():
    '''displays form to register new admin-user and their organization and handles submit'''

    form = FirstAdminForm()
    if form.validate_on_submit():
        try:
            org = Organization(name=form.name.data)
            db.session.add(org)
            db.session.commit()
        except IntegrityError:
            flash("Organization already exists. Contact your admin for login information.", 'danger')
            return render_template('admin-register.html', form=form)
        try:
            user = User.registerAdmin(
                email=form.email.data,
                password=form.password.data,
                organization_id= Organization.query.filter_by(name=form.organization.data).first().id
                )
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('admin-register.html', form=form)
        do_login(user)
        email_confirm_registration(user.email)
        return redirect(f'/organizations/{org.id}')
    else:
        return render_template('admin-register.html', form=form)
    
@app.route('/organizations/<int:org_id>')
def org_homepage(org_id):
    '''displays an organization's homepage'''
    
    if g.user and g.user.organization_id == org_id:
        #access granted
        org = Organization.query.get_or_404(org_id)
        searches = org.searches
        users = org.users
        return render_template('org-home.html', org=org, searches=searches, users=users)


    else:
        #access denied
        flash("Access Unauthorized", 'danger')
        return redirect('/')
