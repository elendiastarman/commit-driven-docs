import yaml
import pprint
import getpass
import requests


def get_commits():
  with open("config.yaml") as file:
    config = yaml.load(file.read())

  if config['auth']['method'] == 'userpass':
    auth = (input("Username: "), getpass.getpass("Password: "))
  else:
    raise ValueError('Auth method {} is not valid.'.format(config['auth']['method']))

  root_url = "https://api.github.com/repos/{}/{}".format(config['git']['org'], config['git']['repo'])
  branch_url = "{}/branches/{}".format(root_url, config['git']['branch'])

  response = requests.get(branch_url, auth=auth).json()

  if response.status_code != 200:
    print("ERROR - Response:")
    pprint.pprint(response)

  print("Latest commit sha: {}".format(response['commit']['sha']))

  response = requests.get(response['commit']['url'], auth=auth).json()

  if response.status_code != 200:
    print("ERROR - Response:")
    pprint.pprint(response)

  print("Files that changed:")
  for file in response['files']:
    print(file['filename'])


if __name__ == '__main__':
  get_commits()
