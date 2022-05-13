#!/usr/bin/python3
import os
import json
import html
import random
import string
import threading
import subprocess
from bottle import app, error, post, request, redirect, route, run, static_file
from beaker.middleware import SessionMiddleware

session_opts = {
  'session.type': 'file',
  'session.data_dir': './cfg/',
  'session.auto': True,
}
sapp = SessionMiddleware(app(), session_opts)
sess = request.environ.get('beaker.session')
 
ipfspath = '/usr/local/bin/ipfs'

with open('cfg/email.cfg', 'r') as ecf:
  email = ecf.read()

storageMax = ''
ipfs_id = ''
if os.path.exists('ipfs/config'):
  with open('ipfs/config', 'r') as ipcfg:
    ipconfig = ipcfg.read()
    jtxt = json.loads(ipconfig)
    ipfs_id = jtxt['Identity']['PeerID']
    storageMax = ''.join(filter(lambda i: i.isdigit(), jtxt['Datastore']['StorageMax']))

@route('/')
def index():
  htmlsrc = '<html><head>'
  htmlsrc += '<title>IPFS Podcast Node</title>'
  htmlsrc += '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
  htmlsrc += '<style>'
  htmlsrc += 'body { background-image: url("ipfspod.png"); background-repeat: no-repeat; background-position: 50% 50%; font-family: "Helvetica Neue",Helvetica,Arial,sans-serif; font-size: 14px; margin: 1em; } '
  htmlsrc += 'form { margin-top: 0.5em; width: fit-content; background-color: darkgray; border-radius: 10px; padding: 10px; box-shadow: 0px 0px 5px 1px black; opacity: 0.9; } '
  htmlsrc += 'form label { display: inline-block; width: 130px; text-align: right; } '
  htmlsrc += 'form input { margin: 4px; } '
  htmlsrc += 'form button { margin-left: 70%; white-space: nowrap; } '
  htmlsrc += 'form a { background-color: lightgray; padding: 5px; margin-right: 5px; font-weight: bold; border-radius: 10px; display: inline-block; font-size: 9pt; text-decoration: none; } '
  htmlsrc += 'button { clear: both; padding: 5px; float: right; } '
  htmlsrc += 'pre { border-radius: 20px; background-color: darkcyan; color: white; opacity: 0.6; padding: 10px; overflow: auto; height: 50%; display: flex; flex-direction: column-reverse; box-shadow: 0px 0px 5px 1px black; white-space: break-spaces; } '
  htmlsrc += 'div#links a { background-color: lightgray; margin: 4px; padding: 5px 13px; font-weight: bold; border-radius: 10px; display: inline-block; font-size: 9pt; text-decoration: none; } '
  htmlsrc += 'div#tmr { height: 3px; margin-bottom: 0.5em; background-color: lightblue; animation: tbar 60s linear; } '
  htmlsrc += '@keyframes tbar { 0% { width: 0%; } 90% { background-color: cornflowerblue; } 100% { width: 100%; background-color: red; } } '

  htmlsrc += '</style>'
  htmlsrc += '</head>'
  htmlsrc += '<body>'
  htmlsrc += '<h2>IPFS Podcasting Node</h2>'

  if ipfs_id != '':
    htmlsrc += '<label>IPFS ID : </label> <b>' + str(ipfs_id) + '</b><br/>'

  sess = request.environ.get('beaker.session')
  sess['csrf'] = ''.join(random.choice(string.ascii_letters) for i in range(12))
  sess.save()

  htmlsrc += '<form action="/" method="post">'
  htmlsrc += '<input id="csrf" name="csrf" type="hidden" value="' + sess['csrf'] + '" />'
  htmlsrc += '<label title="E-mail Address (optional)"><a href="https://ipfspodcasting.net/help/email" target="_blank">?</a>Node E-Mail : </label><input style="width: 190px;" id="email" name="email" type="email" placeholder="user@example.com" title="E-mail Address (optional)" value="' + email + '" />'
  if storageMax != '':
    htmlsrc += '<br/><label title="IPFS Datastore Limit">IPFS "StorageMax" : </label><input style="width: 50px; text-align: right;" id="storageMax" name="storageMax" type="number" min="1" max="999" pattern="[1-999]" required title="IPFS Datastore Limit" value="' + str(storageMax) + '" />GB'
  htmlsrc += '<button>Save Changes</button>'
  htmlsrc += '<div style="clear: both;"></div></form>'

  htmlsrc += '<h3>Log Messages</h3><pre>'
  with open('ipfspodcastnode.log', 'r') as pcl:
    logtxt = pcl.read()
    htmlsrc += html.escape(logtxt)
  htmlsrc += '</pre>'
  htmlsrc += '<div id="tmr"></div><div id="links"><a href="https://ipfspodcasting.net/Manage" target="_blank">Manage</a><a href="https://ipfspodcasting.net/faq" target="_blank">FAQ</a></div>'
  #<a id="ipfsui" href="http://umbrel.local:5001/webui" target="_blank">IPFS WebUI</a><a id="ipfspn" href="http://umbrel.local:5001/webui/#/pins" target="_blank">Pinned Files</a>
  htmlsrc += '<script>window.setTimeout( function() { window.location.reload(); }, 60000); </script>'
  #document.getElementById("ipfsui").href=window.location.href; document.getElementById("ipfsui").href=document.getElementById("ipfsui").href.replace("8675", "5001/webui"); document.getElementById("ipfspn").href=window.location.href; document.getElementById("ipfspn").href=document.getElementById("ipfspn").href.replace("8675", "5001/webui/#/pins");
  htmlsrc += '</body></html>'
  return htmlsrc

@post('/')
def do_email():
  csrf = request.forms.get('csrf')
  sess = request.environ.get('beaker.session')
  if csrf == sess['csrf']:
    global email
    email = request.forms.get('email')
    with open('cfg/email.cfg', 'w') as ecf:
      ecf.write(email)

    global storageMax
    storageMax = request.forms.get('storageMax')
    api_dstore = subprocess.run(ipfspath + ' config --json Datastore.StorageMax \'"' + storageMax + 'GB"\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  redirect('/')

@route('/ipfspod.png')
def server_static():
    return static_file('ipfspod.png', root='')

#run(host='0.0.0.0', port=8675, debug=True)
threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8675, app=sapp, debug=False)).start()
