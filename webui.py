#!/usr/bin/python3
import threading
from bottle import error, post, request, redirect, route, run, static_file

with open('cfg/email.cfg', 'r') as ecf:
  email = ecf.read()
  if email == '':
    email = 'user@example.com'

@route('/')
def index():
  html = '<html><body style="background-image: url(\'ipfspod.png\'); background-repeat: no-repeat; background-position: 50% 50%; font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; font-size: 14px; margin: 1em;">'
  html += '<h2>IPFS Podcasting Node</h2>'
  html += 'Enter your email to manage this node at <a href="https://ipfspodcasting.net/Manage" target="_blank">IPFSPodcasting.net</a>'
  html += '<form action="/" method="post" style="margin-top: 0.5em;">'
  html += '<label>Node E-Mail (optional) : </label> <input id="email" name="email" type="email" placeholder="user@example.com" required title="E-mail Address" value="' + email + '" /> <button>Update</button>'
  html += '</form>'
  html += '<hr/><h3>Log Messages</h3><pre style="border-radius: 20px; background-color: darkcyan; color: white; opacity: 0.6; padding: 10px; overflow: auto; height: 50%; display: flex; flex-direction: column-reverse; box-shadow: 0px 0px 5px 1px black;" >'
  with open('ipfspodcastnode.log', 'r') as pcl:
    html += pcl.read()
  html += '</pre>'
  html += '<a id="ipfsui" href="http://umbrel.local:5001/webui" target="_new">IPFS WebUI</a> | <a href="https://ipfspodcasting.net/faq" target="_new">IPFS Podcasting FAQ</a>'
  html += '<script>window.setTimeout( function() { window.location.reload(); }, 60000); document.getElementById("ipfsui").href=window.location.href; document.getElementById("ipfsui").href=document.getElementById("ipfsui").href.replace("8675", "5001/webui");</script>'
  html += '</body></html>'
  return html

@post('/')
def do_email():
  global email
  email = request.forms.get('email')
  with open('cfg/email.cfg', 'w') as ecf:
    ecf.write(email)
  redirect('/')

@route('/ipfspod.png')
def server_static():
    return static_file('ipfspod.png', root='')

#run(host='0.0.0.0', port=8675, debug=True)
threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8675, debug=False)).start()
