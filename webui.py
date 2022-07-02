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

ipfs_id = ''
if os.path.exists('ipfs/config'):
  with open('ipfs/config', 'r') as ipcfg:
    ipconfig = ipcfg.read()
    jtxt = json.loads(ipconfig)
    ipfs_id = jtxt['Identity']['PeerID']

@route('/')
def index():
  sess = request.environ.get('beaker.session')
  sess['csrf'] = ''.join(random.choice(string.ascii_letters) for i in range(12))
  sess.save()

  htmlsrc = '<html><head>'
  htmlsrc += '<title>IPFS Podcast Node</title>'
  htmlsrc += '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
  htmlsrc += '<link rel="icon" href="/favicon.png">'
  htmlsrc += '<style>'
  htmlsrc += 'body { background-image: url("ipfspod.png"); background-repeat: no-repeat; background-position: 50% 50%; font-family: "Helvetica Neue",Helvetica,Arial,sans-serif; font-size: 14px; margin: 1em; } '

  htmlsrc += '.nfo { border-radius: 20px; background-color: darkcyan; color: white; opacity: 0.6; padding: 10px; } '
  htmlsrc += 'label { display: inline-block; width: 65px; text-align: right; } '
  htmlsrc += 'form#ecfg { margin-bottom: 0; } '
  htmlsrc += 'form#ecfg input { margin: 4px; width: calc(100% - 150px); max-width: 200px; } '
  htmlsrc += 'form#frst button { background-color: pink; border-color: indianred; margin: 4px; padding: 3px 13px; font-weight: bold; border-radius: 10px; display: inline-block; font-size: 9pt; white-space: nowrap; } '
  htmlsrc += 'form#igc { display: inline-block; margin-left: 5px; } '
  htmlsrc += 'div.prog { height: 5px; background-color: gray; border-radius: 0.25rem; } '
  htmlsrc += 'div.prog div.used { height: 5px; background-color: lime; border-radius: 0.25rem; } '
  htmlsrc += 'pre { overflow: auto; height: 50%; display: flex; flex-direction: column-reverse; white-space: break-spaces; } '
  htmlsrc += 'div#links a { background-color: lightgray; margin: 4px; padding: 5px 13px; font-weight: bold; border-radius: 10px; display: inline-block; font-size: 9pt; text-decoration: none; } '
  htmlsrc += 'a.ppass, a.pwarn, a.pfail { padding: 3px 8px 1px 8px; border-radius: 8px; display: inline-block; font-size: 9pt; font-weight: bold; text-decoration: none; } '
  htmlsrc += 'a.ppass { background-color: lightgreen; color: green; } '
  htmlsrc += 'a.pwarn { background-color: palegoldenrod; color: darkorange; } '
  htmlsrc += 'a.pfail { background-color: pink; color: red; } '
  htmlsrc += 'div#tmr { height: 3px; margin-bottom: 0.5em; background-color: lightblue; animation: tbar 60s linear; } '
  htmlsrc += '@keyframes tbar { 0% { width: 0%; } 90% { background-color: cornflowerblue; } 100% { width: 100%; background-color: red; } } '

  htmlsrc += '</style>'
  htmlsrc += '</head>'
  htmlsrc += '<body>'

  htmlsrc += '<h2>IPFS Podcasting Node</h2>'
  htmlsrc += '<div class="nfo" style="background-color: #222; overflow: hidden;">'
  if ipfs_id != '':
    htmlsrc += '<div style="white-space: nowrap;"><label>IPFS ID : </label> <b>' + str(ipfs_id) + '</b></div>'
  htmlsrc += '<form id="ecfg" action="/" method="post">'
  htmlsrc += '<input id="csrf" name="csrf" type="hidden" value="' + sess['csrf'] + '" />'
  htmlsrc += '<label title="E-mail Address (optional)">E-Mail : </label><input id="email" name="email" type="email" placeholder="user@example.com" title="E-mail Address (optional)" value="' + email + '" />'
  htmlsrc += '<button>Update</button><br/>'
  htmlsrc += '</form>'

  htmlsrc += '<label>Network : </label> '

  httpstat = 'pfail'
  hstat = subprocess.run('timeout 1 bash -c "</dev/tcp/ipfspodcasting.net/80"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if hstat.returncode == 0:
    httpstat = 'ppass'
  htmlsrc += '<a class="' + httpstat + '" href="https://ipfspodcasting.net/Help/Network" title="Port 80 Status" target="_blank">HTTP</a> '

  httpsstat = 'pfail'
  hsstat = subprocess.run('timeout 1 bash -c "</dev/tcp/ipfspodcasting.net/443"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if hsstat.returncode == 0:
    httpsstat = 'ppass'
  htmlsrc += '<a class="' + httpsstat + '" href="https://ipfspodcasting.net/Help/Network" title="Port 443 Status" target="_blank">HTTPS</a> '
  
  peercnt = 0
  speers = subprocess.run(ipfspath + ' swarm peers|wc -l', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if speers.returncode == 0:
    peercnt = int(speers.stdout.decode().strip())
  if peercnt > 400:
    ipfsstat = 'ppass'
  elif peercnt > 100:
    ipfsstat = 'pwarn'
  else:
    ipfsstat = 'pfail'
  htmlsrc += '<a class="' + ipfsstat + '" href="https://ipfspodcasting.net/Help/Network" title="Port 4001 Status" target="_blank">IPFS <span style="font-weight: normal; color: #222;">- ' + str(peercnt) + ' Peers</span></a><br/>'

  repostat = subprocess.run(ipfspath + ' repo stat -s|grep RepoSize', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if repostat.returncode == 0:
    repolen = repostat.stdout.decode().strip().split(':')
    used = int(repolen[1].strip())
  else:
    used = 0
  df = os.statvfs('/')
  avail = df.f_bavail * df.f_frsize
  percent = round(used/(used+avail)*100, 1)

  if used < (1024*1024*1024):
    used = str(round(used/1024/1024, 1)) + ' MB'
  elif used < (1024*1024*1024*1024):
    used = str(round(used/1024/1024/1024, 1)) + ' GB'
  else:
    used = str(round(used/1024/1024/1024/1024, 2)) + ' TB'

  if avail < (1024*1024*1024):
    avail = str(round(avail/1024/1024, 1)) + ' MB'
  elif avail < (1024*1024*1024*1024):
    avail = str(round(avail/1024/1024/1024, 1)) + ' GB'
  else:
    avail = str(round(avail/1024/1024/1024/1024, 2)) + ' TB'

  htmlsrc += '<label>Storage : </label>'
  htmlsrc += '<div style="display: inline-block; margin-left: 5px; position: relative; top: 5px; width: calc(100% - 150px);">'
  htmlsrc += '<div class="prog"><div class="used" style="width: ' + str(percent) + '%; min-width: 4px;"></div></div>'
  htmlsrc += '<div style="display: flex; margin-top: 3px;"><span style="width: 33.3%; text-align: left;">' + str(used) + ' Used</span><span style="width: 33.3%; text-align: center;">' + str(percent) + '%</span><span style="width: 33.3%; text-align: right;">' + str(avail) + ' Available</span></div>'
  htmlsrc += '</div>'

  #don't allow gc while pinning (or already running)
  gctxt = ''
  gcrun = subprocess.run('ps x|grep -E "(repo gc|ipfs pin)"|grep -v grep', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if gcrun.returncode == 0:
    gctxt = gcrun.stdout.decode().strip()
  if gctxt == '':
    disabled = ''
    title = 'Run IPFS Garbage Collection'
  else:
    disabled = 'disabled="disabled"'
    title = 'Not available while pinning or GC already running...'

  htmlsrc += '<form id="igc" action="/" method="post">'
  htmlsrc += '<input id="csrf" name="csrf" type="hidden" value="' + sess['csrf'] + '" />'
  htmlsrc += '<input id="rungc" name="rungc" type="hidden" value="1" />'
  htmlsrc += '<button ' + disabled + ' title="' + title + '">Clean Up</button>'
  htmlsrc += '</form>'

  htmlsrc += '</div>'

  htmlsrc += '<h3 style="margin-bottom: 0;">Activity Log</h3>'
  htmlsrc += '<pre class="nfo" style="margin-top: 0;">'
  with open('ipfspodcastnode.log', 'r') as pcl:
    logtxt = pcl.read()
    htmlsrc += html.escape(logtxt)
  htmlsrc += '</pre>'

  htmlsrc += '<div id="tmr"></div>'

  htmlsrc += '<form id="frst" action="/" method="post" style="float: right;">'
  htmlsrc += '<input id="csrf" name="csrf" type="hidden" value="' + sess['csrf'] + '" />'
  htmlsrc += '<input id="reset" name="reset" type="hidden" value="1" />'
  htmlsrc += '<button title="Hard reset the IPFS app (when &quot;it\'s just not working&quot;)">Restart IPFS</button>'
  htmlsrc += '</form>'

  htmlsrc += '<div id="links"><a href="https://ipfspodcasting.net/Manage" target="_blank">Manage</a><a href="https://ipfspodcasting.net/faq" target="_blank">FAQ</a></div>'
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
    if request.forms.get('email') is not None:
      global email
      email = request.forms.get('email')
      with open('cfg/email.cfg', 'w') as ecf:
        ecf.write(email)
    if request.forms.get('reset') == '1':
      suicide = subprocess.run('kill 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if request.forms.get('rungc') == '1':
      gcrun = subprocess.run(ipfspath + ' repo gc --silent', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  redirect('/')

@route('/ipfspod.png')
def server_static():
    return static_file('ipfspod.png', root='')

@route('/favicon.png')
def server_static():
    return static_file('favicon.png', root='')

#run(host='0.0.0.0', port=8675, debug=True)
threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8675, app=sapp, debug=False)).start()
