from flask import render_template
from app import app, db

#handles page not found errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

#handles internal server errors
@app.errorhandler(500)
def internal_error(error):
    #reset the database to a clean state and ensures database remains in a consistent state even after an unhandled exception occurs. 
    #good practice for handling erros gracefully and preventing potential data integrity issues
    db.session.rollback()
    return render_template('500.html'), 500
