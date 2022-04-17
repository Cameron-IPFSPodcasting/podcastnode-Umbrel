#!/usr/bin/python3
import subprocess
import json
import requests
import time
import logging
import os

#bin Paths
ipfspath = '/usr/local/bin/ipfs'
wgetpath = '/usr/bin/wget'
wcpath = '/usr/bin/wc'

#Request payload
payload = { 'version': 0.5 }

#Basic logging to ipfspodcastnode.log
logging.basicConfig(format="%(asctime)s : %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename="ipfspodcastnode.log", filemode="w", level=logging.INFO)

#Create an empty email.cfg (if it doesn't exist)
if not os.path.exists('cfg/email.cfg'):
  with open('cfg/email.cfg', 'w') as ecf:
    ecf.write('')

#Start WebUI
import webui
logging.info('Starting Web UI')

#Init IPFS (if necessary)
if not os.path.exists('ipfs/config'):
  logging.info('Initializing IPFS')
  ipfs_init = subprocess.run(ipfspath + ' init', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#  Need to open up IPFS Web UI CORS with the Umbrel $HOST_IP
  HOST_IP = os.getenv('HOST_IP')
  api_cors = subprocess.run(ipfspath + ' config --json API.HTTPHeaders.Access-Control-Allow-Origin \'["http://' + HOST_IP + ':5001", "http://umbrel.local:5001", "http://localhost:3000", "http://127.0.0.1:5001", "https://webui.ipfs.io"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#  api_cors = subprocess.run(ipfspath + ' config --json API.HTTPHeaders.Access-Control-Allow-Origin \'["*"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  api_meth = subprocess.run(ipfspath + ' config --json API.HTTPHeaders.Access-Control-Allow-Methods \'["PUT", "POST"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  #Open the port on the $LOCAL_IP
  LOCAL_IP = os.getenv('LOCAL_IP')
  listen_addr = subprocess.run(ipfspath + ' config --json Addresses.API \'["/ip4/127.0.0.1/tcp/5001", "/ip4/' + LOCAL_IP + '/tcp/5001"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start IPFS
daemon = subprocess.run(ipfspath + ' daemon >/dev/null 2>&1 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
logging.info('Starting IPFS Daemon')
time.sleep(10)

#Get IPFS ID
with open('ipfs/config', 'r') as ipcfg:
  ipconfig = ipcfg.read()
  jtxt = json.loads(ipconfig)
  payload['ipfs_id'] = jtxt['Identity']['PeerID']
  logging.info('IPFS ID : ' + payload['ipfs_id'])

#Main loop
while True:
  #Read E-mail Config
  with open('cfg/email.cfg', 'r') as ecf:
    email = ecf.read()
    if email == '':
      email = 'user@example.com'
  payload['email'] = email

  #Check if IPFS is running, restart if necessary.
  payload['online'] = False
  diag = subprocess.run(ipfspath + ' diag sys', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if diag.returncode == 0:
    ipfs = json.loads(diag.stdout)
    payload['ipfs_ver'] = ipfs['ipfs_version']
    payload['online'] = ipfs['net']['online']
  if payload['online'] == False:
    #Start the IPFS daemon
    daemon = subprocess.run(ipfspath + ' daemon >/dev/null 2>&1 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('@@@ IPFS NOT RUNNING !!! Restarting Daemon @@@')

  #Request work
  logging.info('Requesting Work...')
  try:
    response = requests.post("https://IPFSPodcasting.net/Request", data=payload)
    work = json.loads(response.text)
    logging.info('Response : ' + str(work))
  except requests.ConnectionError as e:
    logging.info('Connection error during request : ' + str(e))

  if work['message'][0:7] != 'No Work':
    if work['download'] != '' and work['filename'] != '':
      logging.info('Downloading ' + str(work['download']))
      #Download any "downloads" and Add to IPFS
      hash = subprocess.run(wgetpath + ' -q --no-check-certificate "' + work['download'] + '" -O - | ' + ipfspath + ' add -q -w --stdin-name "' + work['filename'] + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      downhash=hash.stdout.decode().strip().split('\n')
      if hash.returncode == 0:
        #Get file size (for validation)
        size = subprocess.run(ipfspath + ' cat ' + downhash[0] + ' | ' + wcpath + ' -c', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        downsize=size.stdout.decode().strip()
        logging.info('Added to IPFS ( hash : ' + str(downhash[0]) + ' length : ' + str(downsize) + ')')
        payload['downloaded'] = downhash[0] + '/' + downhash[1]
        payload['length'] = downsize
      else:
        payload['error'] = hash.returncode

    if work['pin'] != '':
      #Directly pin if already in IPFS
      logging.info('Pinning hash (' + str(work['pin']) + ')')
      pin = subprocess.run(ipfspath + ' pin add ' + work['pin'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      if pin.returncode == 0:
        #Verify Success and return full CID & Length
        pinchk = subprocess.run(ipfspath + ' ls ' + work['pin'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pinchk.returncode == 0:
          hashlen=pinchk.stdout.decode().strip().split(' ')
          payload['pinned'] = hashlen[0] + '/' + work['pin']
          payload['length'] = hashlen[1]
        else:
          payload['error'] = pinchk.returncode
      else:
        payload['error'] = pin.returncode

    if work['delete'] != '':
      #Delete/unpin any expired episodes
      logging.info('Unpinned old/expired hash (' + str(work['delete']) + ')')
      delete = subprocess.run(ipfspath + ' pin rm ' + work['delete'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      payload['deleted'] = work['delete']

    #Report Results
    logging.info('Reporting results...')
    try:
      response = requests.post("https://IPFSPodcasting.net/Response", data=payload)
    except requests.ConnectionError as e:
      logging.info('Connection error during response : ' + str(e))

  else:
    logging.info('No work.')

  #wait 10 minutes then start again
  logging.info('Sleeping 10 minutes...')
  time.sleep(600)
