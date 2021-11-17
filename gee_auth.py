# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *   It based on Google Earth Engine plugin by Gennadii Donchyts.          *
# *                                                                         *
# ***************************************************************************

import errno, json, os
from six.moves.urllib import parse
from six.moves.urllib import request
from six.moves.urllib.error import HTTPError


CLIENT_ID = ('517222506229-vsmmajv00ul0bs7p89v5m89qs8eb9359.'
             'apps.googleusercontent.com')
CLIENT_SECRET = 'RUP0RZ6e0pPhDzsqIJ7KlNd1'
SCOPES = [
    'https://www.googleapis.com/auth/earthengine',
    'https://www.googleapis.com/auth/devstorage.full_control'
]
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

def get_authorization_url(code_challenge):
  """Returns a URL to generate an auth code."""

  return 'https://accounts.google.com/o/oauth2/auth?' + parse.urlencode({
      'client_id': CLIENT_ID,
      'scope': ' '.join(SCOPES),
      'redirect_uri': REDIRECT_URI,
      'response_type': 'code',
      'code_challenge': code_challenge,
      'code_challenge_method': 'S256',
  })

def request_token(auth_code, code_verifier):
  """Uses authorization code to request tokens."""

  request_args = {
      'code': auth_code,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET,
      'redirect_uri': REDIRECT_URI,
      'grant_type': 'authorization_code',
      'code_verifier': code_verifier,
  }

  refresh_token = None

  try:
    response = request.urlopen(
        TOKEN_URI,
        parse.urlencode(request_args).encode()).read().decode()
    refresh_token = json.loads(response)['refresh_token']
  except HTTPError as e:
    raise Exception('Problem requesting tokens. Please try again.  %s %s' %
                    (e, e.read()))

  return refresh_token

def get_credentials_path():
  cred_path = os.path.expanduser('~/.config/earthengine/credentials')
  return cred_path


def write_token(refresh_token):
  """Attempts to write the passed token to the given user directory."""

  credentials_path = get_credentials_path()
  dirname = os.path.dirname(credentials_path)
  try:
    os.makedirs(dirname)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise Exception('Error creating directory %s: %s' % (dirname, e))

  file_content = json.dumps({'refresh_token': refresh_token})
  if os.path.exists(credentials_path):
    os.remove(credentials_path)
  with os.fdopen(
      os.open(credentials_path, os.O_WRONLY | os.O_CREAT, 0o600), 'w') as f:
    f.write(file_content)
