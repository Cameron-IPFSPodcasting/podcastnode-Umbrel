#!/usr/bin/python3
import threading
from bottle import error, post, request, redirect, route, run

with open('cfg/email.cfg', 'r') as ecf:
  email = ecf.read()
  if email == '':
    email = 'user@example.com'

@route('/')
def index():
  html = '<h2>IPFS Podcasting Node</h2>'
  html += '<form action="/" method="post">'
  html += '<label>Node E-Mail : </label> <input name="email" value="' + email + '" /> <button>Update</button>'
  html += '</form>'
  html += 'Enter your email to manage your node at <a href="https://ipfspodcasting.net/Manage" target="_blank">https://IPFSPodcasting.net/Manage</a>'
  html += '<hr/><h3>Log Messages <span style="font-size: 9pt;">(<a href="/">refresh</a>)</span></h3><pre style="border: 2px solid black; padding: 5px; overflow-y: auto; max-height: 50%; display: flex; flex-direction: column-reverse;" >'
  with open('ipfspodcastnode.log', 'r') as pcl:
    html += pcl.read()
  html += '</pre>'
  html += '<script>window.setTimeout( function() { window.location.reload(); }, 60000);</script>'
  return html

@post('/')
def do_email():
  global email
  email = request.forms.get('email')
  with open('cfg/email.cfg', 'w') as ecf:
    ecf.write(email)
  redirect('/')

#run(host='0.0.0.0', port=8675, debug=True)
threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8675, debug=False)).start()
