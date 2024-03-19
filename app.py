from flask import Flask, session, g, redirect, render_template, flash, jsonify, request
from flask_mail import Mail, Message
from secret import GMAIL_USERNAME, GMAIL_PASSWORD
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Organization, PendingUser, Company, Profile, Role, Function, Level, RoleFunction, Map
from sqlalchemy.exc import IntegrityError
from forms import FirstAdminForm, InviteUserForm, RegisterUserForm, LoginForm, CompanyForm, ProfileForm, MapForm
from seed import should_seed, seed_functions, seed_levels, seed_states, seed_countries
from security import generate_token, calculate_expiration
from datetime import datetime
from sqlalchemy import or_
import os

CURR_USER_KEY = "curr_user"
BASE_URL = 'https://talenttree.onrender.com'

app = Flask(__name__)

app.config['SECRET_KEY']='key'
debug=DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///talenttree'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = GMAIL_USERNAME
app.config['MAIL_PASSWORD'] = GMAIL_PASSWORD

mail = Mail(app)

with app.app_context():
    connect_db(app)

with app.app_context():
    if should_seed():
        seed_functions()
        seed_levels()
        seed_states()
        seed_countries()

def email_registration(email, token):
    '''sends email to pending user so that they can sign up using the token-embedded link'''

    msg = mail.send_message(
        'Time Sensitive: Welcome to talentTree!',
        sender = GMAIL_USERNAME,
        recipients = [email],
        body=f'''
Welcome to talentTree! Please click the following link within 24 hours to complete registration: 
{BASE_URL}/register/{token}
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
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''renders login form and handles submission'''
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email, password)
        if user:
            do_login(user)
            return redirect(f'/organizations/{user.organization_id}')
        else:
            form.email.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    '''logs out user'''
    do_logout()
    flash("Successfully logged out", 'success')
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def register_first_admin():
    '''displays form to register new admin-user and their organization and handles submit'''

    form = FirstAdminForm()
    if form.validate_on_submit():
        try:
            org = Organization(name=form.organization.data)
            db.session.add(org)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Organization already exists. Contact your admin for login information.", 'danger')
            return render_template('admin-register.html', form=form)
        try:
            user = User.registerAdmin(
                email=form.email.data,
                password=form.password.data,
                organization_id= Organization.query.filter_by(name=form.organization.data).first().id
                )
            db.session.add(user)
            db.session.commit()
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

    if not g.user or g.user.organization_id != org_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')    
        
    else:
        org = Organization.query.get_or_404(org_id)
        users = org.users
        companies = Company.query.filter_by(organization_id=g.user.organization_id).all()
        profiles = Profile.query.filter_by(organization_id=g.user.organization_id).all()
        return render_template('org-home.html', org=org, companies=companies, profiles=profiles, users=users)        
    
@app.route('/invite', methods=['GET', 'POST'])
def invite_users():
    '''returns a form allowing admin to invite others to their organization'''

    if not g.user or not g.user.is_admin:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    
    form = InviteUserForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            if User.query.filter_by(email=email).first():
                raise ValueError
            old_pending = PendingUser.query.filter_by(email=email).first()
            if old_pending:
                db.session.delete(old_pending)
                db.session.commit()
            is_admin = form.is_admin.data
            pending_user = PendingUser(
                email = email,
                pending_admin = is_admin,
                organization_id = g.user.organization_id,
                token = generate_token(),
                expiration = calculate_expiration()
            )
            db.session.add(pending_user)
            db.session.commit()
            email_registration(email, pending_user.token)
            flash(f'Successfully invited {email}', 'success')
            return redirect('/invite')
        except ValueError:
            flash("Username already taken", 'danger')
            return render_template('invite-user.html', form=form)   
    return render_template('invite-user.html', form=form)

@app.route('/register/<token>', methods=['GET', 'POST'])
def token_registration(token):
    '''allows a new user to register from an emailed link and handles submission'''
    pending_user = PendingUser.query.filter_by(token=token).first()
    if pending_user:
        is_admin = pending_user.pending_admin
        org_id = pending_user.organization_id
        email = pending_user.email
        db.session.delete(pending_user)
        db.session.commit()
        current_time = datetime.now()

        if current_time <= pending_user.expiration:
            form = RegisterUserForm()
            if form.validate_on_submit():
                try:
                    password = form.password.data
                    new_user = User.register(
                        email =email, 
                        password = password, 
                        organization_id = org_id, 
                        is_admin = is_admin)
                    db.session.add(new_user)
                    db.session.commit()
                    do_login(new_user)
                except IntegrityError:
                    flash("Username already taken", 'danger')
                    return render_template('invite-user.html', form=form)
                return redirect(f'/organizations/{new_user.organization_id}')
            return render_template('user-register.html', form=form)
    flash("Invalid Token")
    return redirect('/')

@app.route('/companies/new', methods=['GET', 'POST'])
def show_and_handle_company_form():
    '''renders form to create new company and redirects to company on creation'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    form = CompanyForm()
    if form.validate_on_submit():
        try:
            name = form.name.data
            domain = form.domain.data
            new_co = Company(name=name, domain=domain, organization_id=g.user.organization_id)
            db.session.add(new_co)
            db.session.commit()
            return redirect(f'/companies/{new_co.id}')

        except IntegrityError:
                db.session.rollback()
                flash("Domain name already exists", 'danger')
                return render_template('company-form.html', form=form)
    return render_template('company-form.html', form=form)

@app.route('/companies/<int:co_id>')
def show_company(co_id):
    '''shows company details'''
    co = Company.query.get_or_404(co_id)
    if not g.user or g.user.organization_id != co.organization_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    else:
        employees = co.employees
        alumni = co.alumni
        return render_template('company-detail.html', company = co, employees=employees, alumni=alumni)

@app.route('/companies')
def list_companies():
    '''shows an org's list of companies'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    companies = Company.query.filter_by(organization_id=g.user.organization_id).all()
    org = Organization.query.get_or_404(g.user.organization_id)
    return render_template('companies.html', companies=companies, org=org)

@app.route('/profiles/new', methods=['GET', 'POST'])
def show_and_handle_profile_form():
    '''renders form to create new profile and redirects to profile on creation'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    form = ProfileForm()
    if form.validate_on_submit():
        try:
            valid_domain = Company.query.filter(
                (Company.domain == form.company.data) &
                (Company.organization_id == g.user.organization_id)
            ).first()
            if not valid_domain:
                form.company.errors.append('No company exists')
                return render_template('profile-form.html', form=form)
            new_profile = Profile(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                linkedin_url = form.linkedin_url.data,
                headline = form.headline.data,
                organization_id = g.user.organization_id,
                city = form.city.data,
                state_id=form.state.data if form.state.data != 'None' else None,
                country_id = form.country.data
            )
            db.session.add(new_profile)
            db.session.commit()
        except IntegrityError as e:
                db.session.rollback()
                flash("Error: {}".format(str(e)), 'danger')
                flash("Profile already exists", 'danger')
                return render_template('profile-form.html', form=form)
        try:
            new_role = Role(
                company_id = Company.query.filter_by(domain=form.company.data).first().id,
                level_id = Level.query.filter_by(name=form.level.data).first().id,
                profile_id = new_profile.id,
                start_date = form.start_date.data,
                end_date = None,
                is_primary = True
            )
            db.session.add(new_role)
            db.session.commit()
            functions = form.functions.data
            for f in functions:
                function_id = Function.query.filter_by(name=f).first().id
                role_function = RoleFunction(
                    role_id = new_role.id,
                    function_id = function_id
                    )
                db.session.add(role_function)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Problem creating role or functions", 'danger')
            return render_template('profile-form.html', form=form)
        return redirect(f'/profiles/{new_profile.id}')
    else:
        return render_template('profile-form.html', form=form)
            
@app.route('/profiles')
def list_profiles():
    '''lists all profiles in an organization'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    profiles = Profile.query.filter_by(organization_id=g.user.organization_id)
    org = Organization.query.get_or_404(g.user.organization_id)
    return render_template('profiles.html', profiles=profiles, org=org)

@app.route('/profiles/<int:profile_id>')
def show_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if not g.user or g.user.organization_id != profile.organization_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    primary_role = profile.primary_role()
    functions = primary_role.functions
    return render_template('profile.html', profile=profile, primary_role=primary_role, functions=functions)

@app.route('/api/companies/search')
def company_search():
    '''searches for companies by name and domain name and returns via JSON'''

    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')

    search_term = request.args.get('q')
    search_results = Company.query.filter(
        (Company.organization_id == g.user.organization_id) &
        (or_(Company.name.ilike(f'%{search_term}'), Company.domain.ilike(f'%{search_term}%')))
    ).all()

    response = [company.domain for company in search_results]
    return jsonify(response)

@app.route('/maps')
def list_maps():
    '''lists all maps in an organization'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    maps = Map.query.filter_by(organization_id=g.user.organization_id).all()
    org = g.user.organization
    return render_template('maps.html', maps=maps, org=org)

@app.route('/maps/new', methods=['GET', 'POST'])
def show_and_handle_map_form():
    '''renders form to create new map and redirects to map on creation'''
    if not g.user:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    form = MapForm()
    company_options = Company.query.filter_by(organization_id=g.user.organization_id)
    if form.validate_on_submit():
        try:
            new_map = Map(name=form.name.data, 
                          level_id=Level.query.filter_by(name=form.level.data).first().id, 
                          organization_id=g.user.organization_id)
            function_names = request.form.getlist('functions')
            new_map.functions = Function.query.filter(Function.name.in_(function_names)).all()
            company_ids = request.form.getlist('companies')
            new_map.companies = Company.query.filter(Company.id.in_(company_ids), Company.organization_id == g.user.organization_id).all()
            db.session.add(new_map)
            db.session.commit()
            return redirect(f'/maps/{new_map.id}')
        except IntegrityError:
            db.session.rollback()
            flash("Problem creating map", 'danger')
            return render_template('map-form.html', form=form, companies=company_options)
    else:
        return render_template('map-form.html', form=form, companies=company_options)
    
@app.route('/maps/<int:map_id>')
def show_map(map_id):
    '''displays a map of companies and their selected roles'''
    map = Map.query.get_or_404(map_id)
    if not g.user or map.organization_id != g.user.organization_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    
    headers = map.generate_map_headers()
    rows = map.generate_map_rows()
    return render_template('map-detail.html', map=map, headers=headers, rows=rows)

@app.route('/maps/<int:map_id>/edit', methods=['GET', 'POST'])
def edit_map(map_id):
    '''renders form to edit map and redirects to map on submit'''
    map = Map.query.get_or_404(map_id)
    if not g.user or g.user.organization_id != map.organization_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    form = MapForm(obj=map)
    function_names = [f.name for f in map.functions]
    company_options = Company.query.filter_by(organization_id=g.user.organization_id)
    selected_company_ids = [c.id for c in map.companies]
    if form.validate_on_submit():
        map.name = form.name.data
        map.level_id = Level.query.filter_by(name=form.level.data).first().id
        function_names = request.form.getlist('functions')
        map.functions = Function.query.filter(Function.name.in_(function_names)).all()
        company_ids = request.form.getlist('companies')
        map.companies = Company.query.filter(Company.id.in_(company_ids), Company.organization_id == g.user.organization_id).all()
        db.session.commit()
        return redirect(f'/maps/{map_id}')
    else:
        return render_template('map-edit.html', map=map, form=form, companies=company_options, function_names=function_names, selected_company_ids=selected_company_ids)
    
@app.route('/maps/<int:map_id>/delete', methods=['POST'])
def delete_map(map_id):
    '''deletes the map and redirects to maps'''
    map = Map.query.get_or_404(map_id)
    if not g.user.is_admin or map.organization_id != g.user.organization_id:
        flash("Access Unauthorized", 'danger')
        return redirect('/')
    else:
        db.session.delete(map)
        db.session.commit()
        return redirect('/maps')