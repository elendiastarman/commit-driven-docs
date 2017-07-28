# all the imports
import os
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
  DATABASE='commit_driven_docs',
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

@app.route('/', methods=['GET', 'POST'])
def choose_docs():
  chosen_docs = []

  if request.method == 'POST':
    files = get_commit_file_changes((request.form['username'], request.form['password']), debug=1)
    files = {file['filename']: file for file in files}

    db = get_db()
    mappings = db.mappings.find()

    for mapping in mappings:
      for code_file in mapping['code_files']:
        if code_file['filepath'] in files:
          chosen_doc = chosen_docs.setdefault(mapping['doc_path'], {})

          if 'code_files' not in chosen_doc:
            chosen_doc['code_files'] = []

          chosen_doc['code_files'].append({
            'filepath': code_file['filepath'],
            'patch': files[code_file['filepath']]['patch'],
            'status': files[code_file['filepath']]['status'],
          })

  return render_template('choose_docs.html', chosen_docs=chosen_docs)


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


def get_commit_file_changes(auth, debug=0):
  config_path = os.path.join(os.getcwd(), "..", "config.yaml")
  with open(config_path) as file:
    config = yaml.load(file.read())

  root_url = "https://api.github.com/repos/{}/{}".format(config['git']['org'], config['git']['repo'])
  branch_url = "{}/branches/{}".format(root_url, config['git']['branch'])

  response = requests.get(branch_url, auth=auth)
  content = response.json()

  if debug & 1 and response.status_code != 200:
    print("ERROR - Url: {}\n  Content:".format(branch_url))
    pprint.pprint(content)

  print("Latest commit sha: {}".format(content['commit']['sha']))

  commit_url = content['commit']['url']
  response = requests.get(commit_url, auth=auth)
  content = response.json()

  if debug & 1 and response.status_code != 200:
    print("ERROR - Url: {}\n  Content:".format(commit_url))
    pprint.pprint(content)

  # print("Files that changed:")
  # for file in response['files']:
  #   print(file['filename'])

  del auth  # don't keep username/password combo around
  return content['files']
