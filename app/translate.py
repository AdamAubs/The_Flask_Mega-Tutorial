
import json
import requests
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
            not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'centralus'}
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        '/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[
                {'Text': text}])
    print(r)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return r.json()[0]['translations'][0]['text']



# #takes the text to translate,the source  and the destination language codes as arguments.
# #returns a string with the translated text
# def translate(text, source_language, dest_language):
#     #checks if there is a key for the translation service
#     if 'MS_TRANSLATOR_KEY' not in app.config or \
#         not app.config['MS_TRANSLATOR_KEY']:
#             return _('Error: the translation service is not configured')
#     #authentication to use service
#     auth = {
#         'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'], 
#         'Ocp-Apim-Subscription-Region': 'centralus'
#     }
#     #sends HTTP request with POST method to the URL given as the first argument 
#     r = requests.post(
#         'https://api.cognitive.microsofttranslator.com/'
#         '/translate?api-version=3.0&from={}&to={}'.format(
#             source_language, dest_language), headers=auth, json=[{'Text': text}]) #path for the destination languages, text to translate needs to be given in JSON format
#     #if resquest is successful then the body of the ressponse has a JSON encoded string with the translation
#     if r.status_code != 200:
#         return _('Error: the translation service failed!')
#     return r.json()[0]['translations'][0]['text'] #use the json method from the response object to decode the JSON into a python string, and get the the first element from the list of translations
