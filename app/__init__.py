from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

app = Flask(__name__)
app.config.from_object(Config)

#flask login initialized associates LoginManager with flask application (app)
login = LoginManager(app)
#allows flask-login to handle when users are not logged in
login.login_view = 'login'
login.login_message= _l('Please log in to access this page') 


#created db object to represent the database
db = SQLAlchemy(app)
#created migrate object to represent the migration engine
migrate = Migrate(app, db)

#create object of class Mail
mail = Mail(app)

#intialized bootstrap object
bootstrap = Bootstrap(app)

moment = Moment(app)

babel = Babel(app)

#imports various modules from the app package
from app import routes, models, errors

#set up email notifications for errors
if not app.debug: #if not in dev mode
    if app.config['MAIL_SERVER']: #check if MAIL_SERVER variable is set in app.config file
        auth = None 
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']: #sets up auth variable with the email server credentials
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']: #secure variable is set based on MAIL_USE_TLS. (Transport Layer Security) a cryptographic protocol used to secure communications over a computer network, most commonly the internet.
            secure = ()
        #(Simple Mail Transfer Protocol Handler) SMTPhandler is instantiated with the nessary parameters
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']), #email server settings
            fromaddr='no-reply@' + app.config['MAIL_SERVER'], #the sender
            toaddrs=app.config['ADMINS'], subject= 'Coffee Shope failure', #the recipients and subject of the email
            credentials=auth, secure=secure) #secure connection details
        mail_handler.setLevel(logging.ERROR) #only send emails with a severity level of ERROR or higher; no warnings
        app.logger.addHandler(mail_handler) #attaches mail_handlers to app.logger object from Flask
        
        if not os.path.exists('logs'): #Create logs dir if it dosen't exists
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/coffee_shop.log', maxBytes=10240, backupCount=10) #rotates the logs ensuring that the log files do not grow too large when application runs for long time. lim size to 10KB keep backup last 10
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')) #formates logs with timestamp, logging level, the message, and line number where log entry originated
        file_handler.setLevel(logging.INFO) #set logging level to INFO category diff. categories include(DEBUG, INFO, WARNING, ERROR, CRITICAL) in increasing level of severity
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Coffee shop startup')

#the decorated function is invoked for each request to select a language translation to use for that request
@babel.localeselector
def get_locale():
    #uses an attribute of Flask's request object called accept languages.
    #accept_languages provides a high level interface to work with the accept language header that clients send with a request
    #best_match() method compares the list of languages requested by the client aginst the languages the application supports and using the client provided weights finds the best language
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    # return 'es'

if __name__ == "__main__":
    app.run(debug=True)

