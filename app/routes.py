from flask import render_template, flash, redirect, url_for, request, g,jsonify
from app.models import User, Post
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.translate import translate
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #creating an instance of the PostForm() class. form instance will be used to validate and proccess data submitted
    form = PostForm()
    #check if the form data is valid after being submitted
    if form.validate_on_submit():
        try:
            language = detect(form.post.data) #trys to detect the language submitted and if it does saves it 
        except LangDetectException:
            language = '' #if the language cannot be detected save language as an empty string
        #creates an instance of the Post() class having the forms post data, current user and language as arguments for the body author and type of language in the post
        post = Post(body=form.post.data, author=current_user, language=language)
        #add the newly created post to the database
        db.session.add(post)
        #commit any changes made
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index')) #Good practice to redirect although the page will subsquently already render the template when returned. (POST/redirect/GET pattern)
                                         #By redirecting, it avoids inserting duplicate posts when a user inadvertently refreshes the page after submitting a web form
    #accesses arguments given in query string using Flask's request args object (determines the page)
    page = request.args.get('page', 1, type=int)
    #gets all the followed posts for the current user using the followed_posts() method created in the User class. 
    #uses the Flask SQLAlechemy paginate() method to retrieve only the desired page of results. 
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    
   #find the next page and prevous pages using more of flask SQLAlchemy Pagination attributes
   #**interesting** you can add any keyword argument to url_for() function and if those arguments are not referenced in the URL directly, then Flask will incle them
   #in the URL as query arguments
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html',title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    #check if the user is authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #instantiated login form object 
    form = LoginForm()
    #accepts and validates data submitted by the user
    if form.validate_on_submit():
        #checks database for username
        user = User.query.filter_by(username=form.username.data).first()
        #checks if the password exists or is wrong
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        #if username and password are correct call the login_user function
        #anypage after will now have the current_user variable set to the logged in user now
        login_user(user, remember=form.remember_me.data)
        #get all the info the client sent with the request 
        next_page = request.args.get('next')
        #Ensures that the page only redirects when the URL is relative which prevents from being redirected to a differnt site 
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    #make sure the user is not already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #creates instance of RegistrationForm class defined in forms.py. allows permission to access the form fields and data,
    #as well as the forms validation methods
    form = RegistrationForm()
    #use validate_on_submit method to check if form has been subbmited and if it passses all the validation rules set in the form class
    if form.validate_on_submit():
        #Creates user object with data provided by the user in the form fields
        user = User(username=form.username.data, email=form.email.data)
        #sets users password using the set_password method
        user.set_password(form.password.data)
        #adds new user to the database session
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        #redirect user to login to test newly created account
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)

#uses dynamic component to tell flask to accept any text in <username> portion of the URL
@app.route("/user/<username>")
@login_required #this view function is only accessible to logged in users
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    #**backslashes improve readability**
    #pagination links generated by the url_for() need the extra username argument because they are pointing back the user profile page which has this username as a dynamic component of the URL
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
        
    form = EmptyForm() #instantiates EmptyForm object
    return render_template('user.html', user=user, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

#executed before any view function is called; updates the last seen attribute of the authenticated user
@app.before_request
def before_request():
    #checks if the user is authenticated
    if current_user.is_authenticated:
        #updates the last_seen attribute of the current user.
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #creates instance of EditProfileForm() from forms.py essentially allowing access to the forms data
    form = EditProfileForm(current_user.username)
    #checks if the the form is valid and has been submitted (validate_on_submit() returns true)
    if form.validate_on_submit():
        #updates the username attribute of the current_user object with the data submitted in the form's username field
        current_user.username = form.username.data
        #updates the about_me attribute of the current_user object with the data submitted in the form's about_me field
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved'))
        return redirect(url_for('edit_profile'))
    #if the form is not being submitted aka a GET request; pre-populate the fields with the data stored in the database (opposite of what was done above)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route("/unfollow/<username>", methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_("User %(username)s not found.", username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot un-follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_("You are not following %(username)s.", username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

#allows users so see all posts created not just posts by user they follow
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    #**NOTICE** that index.html template is bing re-used only the form is not being passed because I don't want users to be able to write blog posts here 
    return render_template('index.html', title=_('Explore'), posts=posts.items)

@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    #check if the user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('index')) #if logged in then no point in using password reset functionality
    #create an instance of the ResetPasswordRequestForm() class
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #When the form is valid and submitted, look up user and send a password reset email
        if user: 
            send_password_reset_email(user) #helps perferom sending password reset email
        flash(_('Check your email for the instructions to reset your password'))#message is flashed even if the email provided by the user is unknown. This helps prevent clients from figuring out if a user is a member or not
        return redirect(url_for("login"))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #determine who the user is by invoking the token verification method in the User class. this method will return the user if the token is valid or None if not
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    #create an instance of the ResetPasswordForm meaning getting the second form in which the new password is requested
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data) #invoke the set_password() method of the User class to change the password
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

#**note** An asynchronous (or Ajax) request is similar to the routes and view function created in the application thus far, the only difference is that instead of returning HTML or a redirect,
#it just returns data, formatted as XML or more commonly JSON.

#translation view function invokes the Microsoft Translator API and then returns the translated text in JSON format
@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
                            #invoke the translate() function passing the three arguments directly from the data that was submitted with the request
    return jsonify({'text': translate(request.form['text'], #request.form attribute is a dictionary that Flask exposes with all the data that has included in the submission
                                      request.form['source_language'],
                                      request.form['dest_language'])})
                    #the result is incorporated into a single key dictionary under the key text and dictionary is passed as an argument to Flask's jsonify() function which converts the 
                    #dictionary to a JSON formatted payload
                    #the return value from jsonify() is the HTTP response that is going to be sent back to the client
