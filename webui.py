#!/usr/bin/python3
import os
import json
import html
import threading
import subprocess
from bottle import error, post, request, redirect, route, run, static_file

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
  htmlsrc = '<html><head><title>IPFS Podcast Node</title><meta name="viewport" content="width=device-width, initial-scale=1.0" /></head>'
  htmlsrc += '<body style="background-image: url(\'ipfspod.png\'); background-repeat: no-repeat; background-position: 50% 50%; font-family: \'Helvetica Neue\',Helvetica,Arial,sans-serif; font-size: 14px; margin: 1em;">'
  htmlsrc += '<h2>IPFS Podcasting Node</h2>'

  if ipfs_id != '':
    htmlsrc += '<label>IPFS ID : </label> <b>' + str(ipfs_id) + '</b><br/>'

  htmlsrc += '<form action="/" method="post" style="margin-top: 0.5em;">'
  htmlsrc += '<label style="display: inline-block; width: 150px; text-align: right;">Node E-Mail (optional) : </label> <input id="email" name="email" type="email" placeholder="user@example.com" required title="E-mail Address" value="' + email + '" />'
  if storageMax != '':
    htmlsrc += '<br/><label title="IPFS Datastore Limit" style="display: inline-block; width: 150px; text-align: right;">IPFS "StorageMax" : </label> <input  style="width: 50px;" id="storageMax" name="storageMax" type="number" min="1" max="999" pattern="[1-999]" required title="IPFS Datastore Limit" value="' + str(storageMax) + '" /> GB'

  htmlsrc += '<br/><button>Save Changes</button>'
  htmlsrc += '</form>'
  htmlsrc += '<hr/><h3>Log Messages</h3><pre style="border-radius: 20px; background-color: darkcyan; color: white; opacity: 0.6; padding: 10px; overflow: auto; height: 50%; display: flex; flex-direction: column-reverse; box-shadow: 0px 0px 5px 1px black; white-space: break-spaces;" >'
  with open('ipfspodcastnode.log', 'r') as pcl:
    logtxt = pcl.read()
    htmlsrc += html.escape(logtxt)
  htmlsrc += '</pre>'
  htmlsrc += '<a id="ipfsui" href="http://umbrel.local:5001/webui" target="_new">IPFS WebUI</a> | <a href="https://ipfspodcasting.net/faq" target="_new">IPFS Podcasting FAQ</a>'
  htmlsrc += '<script>window.setTimeout( function() { window.location.reload(); }, 60000); document.getElementById("ipfsui").href=window.location.href; document.getElementById("ipfsui").href=document.getElementById("ipfsui").href.replace("8675", "5001/webui");</script>'
  htmlsrc += '</body></html>'
  return htmlsrc

@post('/')
def do_email():
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
threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8675, debug=False)).start()
