from flask import Flask, render_template, request, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from oauth import OAuthSignIn
from flask_security import LoginForm, Security, SQLAlchemyUserDatastore, RoleMixin, login_required
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user

import config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:yankees2@localhost/sync'
app.config['OAUTH_CREDENTIALS'] = {
	'facebook':{
	'id': '1241361279327169',
	'secret': '58e8c5b5284ae3a728bcb9eeede81308'
}}

#app.config['SECURITY_POST_LOGIN_VIEW'] = '/'

db = SQLAlchemy(app)

# role model
class Role(db.Model, RoleMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50)),
	description = db.Column(db.String(255))


# user model
class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(64), nullable=False, unique=True)
	email = db.Column(db.String(50))
	#password = db.Column(db.String(50))
	active = db.Column(db.Boolean)
	name = db.Column(db.String(50))



security = Security(app, SQLAlchemyUserDatastore(db, User, Role))
#Social(app, SQLAlchemyConnectionDatastore(db, Connection))


@app.route("/")
def index():
	return render_template('index.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#@app.route('/showLogIn')
#def showLogIn():
#	return render_template('login.html')

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, name=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


if __name__ == "__main__":
	app.run(debug=True)
