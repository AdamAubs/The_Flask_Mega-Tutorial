import os

basedir = os.path.abspath(os.path.dirname(__file__))

#inherits from the base class object which gains the basic functionality provided by object.
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #Sets location of the database with fall back
    #takes database URL from DATABASE_URL environment variable and if not defined
    #confige a database named app.db located in the main directory of the application, stored in basedir variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') #defines class attribute MAIL_SERVER and assign it the value of the environment variable named MAIL_SERVER
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) #defines a class attribute MAIL_PORT and assigns it the value of the variable named MAIL_PORT, converted to an integer.if not set or empty default to 25 
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None #checks if eviroment variable named MAIL_USE_TLS is set to any value. set -> true not set -> false
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') #if enviroment varible is not set it will default to None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') #if enviroment varible is not set it will default to None
    ADMINS = ['adamaubry2362@gmail.com'] #a list used to specify a list of email addresses that will receive error messages in case of application erros or exceptions
    
    POSTS_PER_PAGE = 3 #how many items will be displayed per page

    LANGUAGES = ['en', 'es']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
