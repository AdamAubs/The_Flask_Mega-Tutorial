from datetime import datetime
from time import time
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt


#Followers association table; used to create a many-to-many relationship between two instances of the User model
#notice that it is not declared as a model, rather its just a means of storing foregin_keys
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), #stores the ID of the user who is following another user
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')) #stores the ID of the user who is being followed by another user
)

#inherits from db.Model, a base class for all models from Flask SQLAlchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) #defines field as class variable, created as instances of the db.Column class
    username = db.Column(db.String(64), index=True, unique=True) 
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #Tells python how to print objects of this class
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #method of user class that returns the URL of the user's avatar image, scaled to the requested size in pixels
    def avatar(self, size):
        #generates MD5 hash with email then encodes the string as bytes before passing to hash function
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=retro&s={size}"
    
    #declars many-to-many relationship
    #followed represents the relationship attribute that will be used to access the users that the current user follows
    #allows a user to follow other users and be followed by other users (self-referential many-to-many relationship)
    #**the "c" attribute is shorthand for "followers.columns.follower_id" used to access the columns of the followers table conveniently
    followed = db.relationship(
        'User', #target model of the relationship, followed relationship will connect instances of the User class to other instances of the User class
        secondary=followers, #secondary configures the assocation table (followers) used for this relationship. relates followers to followed users
        primaryjoin=(followers.c.follower_id == id), #establishes the condition that links User instances with the followers table.
        secondaryjoin=(followers.c.followed_id == id), #establishes the condition for the reverse join from the followed relationship back to the User instance
        backref=db.backref('followers', lazy='dynamic'), #sets up the backreference from the User instances in the followed relationship to the User instances in the followers relationship
        lazy='dynamic')#defines the loading stategy for the relationship. dynamic mean the relationship will return a query object instead of automatically loading the data. allows for further refine before executing

    #follow method
    def follow(self, user):
        #checks if user is following the other user already
        if not self.is_following(user):
            #follows the user
            self.followed.append(user)
    #unfollow method
    def unfollow(self, user):
        if self.is_following(user):
            #remove the follow from the user
            self.followed.remove(user)
    #supporting method to make sure the requested action makes sense (notice how is_following is used in the above methods)
    def is_following(self, user):
        #prevents dupilicate followers 
        #issues query on followed relationship to check if a link between two users already exists
        #looks for items in the association table that have the left side foreign key set to the self user and the right side set to the user argument
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0 
    
    #Query 1: Join -> first argument is followers and the second argument is the join condition 
    #has database creates a temporary table that combines data from posts and followers tables. Merged according to the condition passed as argument
    #Query 2: filter -> selects the items in the joined table that have the follower_id set to this user. Keeping only the entries that have this user as a follower
    #Query 3: Order by -> sorts results with the timestamp field of the post in decending order (most recent shown first)
    def followed_posts(self):
        followed = Post.query.join( 
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id) #creates users own posts
        return followed.union(own).order_by(Post.timestamp.desc()) #return users posts and own posts
    
    #This method returns a JWT (JSON Web Token) token as a string, which is generated directly by the jwt.encode() function
    def get_reset_password_token(self, expires_in=600):
        #jwt.encode() function take 3 main arguments the payload 
        # 1.) dictionary containing the data that will be encoded into JWT token) 
        # 2.) the secret key that is used to sign the JWT token (located in app.config file)
        # 3.) the encryption algorithm HS256 used to generate the JWT token
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
    
    @staticmethod #a decorator that marks the following method as a static method. Belongs to the class rather than the instance of the class (self) no access to the instance attributes, but can be called on the class itself
    def verify_reset_password_token(token):
        try:
            #used to decode the token back into its original payload (dictionary used to generate the token)
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        #if token verification is successful the method atempts to retrieve the User object associated with the user ID extraccted from the toke
        #gets user based on their id from the database
        return User.query.get(id)
    
                    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


#load a user given the ID
#nessary for flask-login to work with database
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
