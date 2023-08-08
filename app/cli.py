from app import app
import os
import click

#decorator (@app.cli.group()) transforms translate() function into a command group within Flask's CLI
@app.cli.group()        #decorator applied to the translate function that uses the cli attribute from the FLask application instance 'app' to define a new command group
def translate():        #translate does not have any code in it because it is used to define the command group named translate
    """Translation and localization commands."""        #docstring that provides a brief description of the purpose of the command group
    pass 

@translate.command()
@click.argument('lang') #uses the @click.argument decorator to define the language code
def init(lang): #click then passes the value provided in the command to the handler function as an argument
    """Initialize a new language"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')
        

#updates the translation files based on the source code of application
@translate.command()
def update():
    """Update all languages"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'): #exctracts translatable messages from the application source code andd stores them in a .pot file named messages.pot
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'): #updates the translation files in app/translations directory based on the messages extracted in the previous step
        raise RuntimeError('update command failed')
    os.remove('messages.pot') #removes the temporary .pot file that was generated after updating the translations

#complies the translation files into a binary format that can be efficiently used by the application to display translated content.
@translate.command()
def compile():
    """Compile all languages"""
    if os.system('pybabel compile -d app/translations'): #compiles the translation files located in the app/translations directory into binary .mo files that the application can use to display translated content
        raise RuntimeError('compile command failed')

