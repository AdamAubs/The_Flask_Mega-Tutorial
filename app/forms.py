from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l #wraps string in special object that triggers the translation to be performed later when the string is used

class LoginForm(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired()]) #validates username by ensuring the field is filled out using WTForms stock validator classes
    password = PasswordField(_l('password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))  #uses WTForms validtor function to rember user
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()]) #ensures user follow correct email structure using WTForms stock validator classes
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')] #ensures password are equal to one another (WTForms stock validtor class)
    )
    submit = SubmitField(_l('Register'))
    
    #custom validation takes form instance (self) and username (input) 
    #***REMEMBER*** when defineing method within a class, the self parameter needs to be included as the first parameter of the method. this indicates that the method belongs to the 
    #class and operates on an instance of the class
    
    #makes sure username and email are not in database 
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('User name already taken.'))
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Email is already in use'))

#New form class for profile about me form
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)]) #TextAreaField class is a milti-line box which the user can enter text. Length class is used to validate
    submit = SubmitField(_l('Submit'))
    
    #allows us to access the original username later when validating the form data
    def __init__(self, original_username, *args, **kwargs): #defines the constructor method for the EditProfileForm class, original_users is a parameter that we expect to be passed when creating an instance of the form
        super(EditProfileForm, self).__init__(*args, **kwargs) #calls the constrctor of the parent class 'FlaskForm' to initialize the forms basic functionality 
        self.original_username = original_username #sores the original_username parameter in an instance variable called original_username
        
    #checks if the original_username has changed, sends query to database checing if the username exists
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username'))

class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
