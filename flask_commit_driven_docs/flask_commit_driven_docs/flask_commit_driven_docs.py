# all the imports
import yaml
import pprint
import getpass
import pymongo
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash  # noqa

app = Flask(__name__)  # create the application instance
app.config.from_object(__name__)  # load config from this very file

# load default config and override config from an environment variable
app.config.update(dict(
  DATABASE='flask_commit_driven_docs',
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='password',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)  # will load overridng config from filepath specified in FLASKR_SETTINGS

client = pymongo.MongoClient('localhost', 27017)


# Database functions

def connect_db():
  """Connects to the specific database."""
  return client[app.config['DATABASE']]


def get_db():
  """Opens a new database connection if there is none yet for the current application context."""
  if not hasattr(g, 'pymongo_db'):
    g.pymongo_db = connect_db()
  return g.pymongo_db


# View functions

@app.route('/')
def choose_docs():
  filenames = None
  if request.method == 'POST':
    filenames = get_commit_filenames((request.form['username'], request.form['password']))

    # db = get_db()
    # entries = db.entries.find()

  return render_template('show_entries.html', filenames=filenames)


# @app.route('/add', methods=['POST'])
# def add_entry():
#   if not session.get('logged_in'):
#     abort(401)
#   db = get_db()
#   db.entries.insert_one({'title': request.form['title'], 'text': request.form['text']})
#   flash('New entry was successfully posted')
#   return redirect(url_for('show_entries'))


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#   error = None
#   if request.method == 'POST':
#     if request.form['username'] != app.config['USERNAME']:
#       error = 'Invalid username'
#     elif request.form['password'] != app.config['PASSWORD']:
#       error = 'Invalid password'
#     else:
#       session['logged_in'] = True
#       flash('You were logged in')
#       return redirect(url_for('show_entries'))

#   return render_template('login.html', error=error)


# @app.route('/logout')
# def logout():
#   session.pop('logged_in', None)
#   flash('You were logged out')
#   return redirect(url_for('show_entries'))


def get_auth(config, **kwargs):
  if config['auth']['method'] == 'userpass':
    auth = (input("Username: "), getpass.getpass("Password: "))
  elif config['auth']['method'] == 'web_userpass':
    auth = (kwargs['username'], kwargs['password'])
  else:
    raise ValueError('Auth method {} is not valid.'.format(config['auth']['method']))

  return auth


def get_commit_filenames(auth, debug=0):
  with open("config.yaml") as file:
    config = yaml.load(file.read())

  root_url = "https://api.github.com/repos/{}/{}".format(config['git']['org'], config['git']['repo'])
  branch_url = "{}/branches/{}".format(root_url, config['git']['branch'])

  response = requests.get(branch_url, auth=auth).json()

  if debug & 1 and response.status_code != 200:
    print("ERROR - Response:")
    pprint.pprint(response)

  print("Latest commit sha: {}".format(response['commit']['sha']))

  response = requests.get(response['commit']['url'], auth=auth).json()

  if debug & 1 and response.status_code != 200:
    print("ERROR - Response:")
    pprint.pprint(response)

  # print("Files that changed:")
  # for file in response['files']:
  #   print(file['filename'])

  return response['files']
