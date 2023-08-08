from flask import render_template
from flask_mail import Message
from app import mail, app
from threading import Thread
from flask_babel import _

#send the email in the thread invoked via the Thread class in the last line of the send_email()
def send_async_email(app, msg):
    with app.app_context(): #app.app_context() creates application context making the application instance accessible via the current_app variable from Flask
        mail.send(msg)

#helper function that sends an email
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start() 
    #thread -> class from thrading module that represents a thread of execution
    #target -> required parameter for the thread class constructor specifying the fuction or method that the thread will execute when started, send_async_email in this case.
    #args -> optional parameter in for the Thread class constructor that allows you to pass arguments to the target function args should be a tuple containg the arguments to be passed in this case app and msg
    #start() -> start method is called on the Thread object to start the execution of the target function send_async_email in a seperate thread
    
#uses Flask's email functionality to send the email
#takes instance of the User class user as single parameter
def send_password_reset_email(user):
    token = user.get_reset_password_token() #calls the get_reset_token() method
    #calls the send_email function
    #uses _() function to call the best language returns the translated text
    send_email(_('[LarkinCoffeeShop] Reset Your Password'), #subject of the email
               sender=app.config['ADMINS'][0], #sender of the email. Uses the first email address defined in the ADMINS config
               recipients=[user.email], #users email (recipient)
               text_body=render_template('email/reset_password.txt', #renders an email template located @'email/reset_password.txt'
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html', #renders the HTML version the emails body located @'email/reset_password.html
                                         user=user, token=token))

