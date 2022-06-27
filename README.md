# podcastnode

An Umbrel Docker App that provides IPFS storage and hosting for IPFSPodcasting.net (Crowd/Self hosting of podcast episodes over IPFS).
If you have an Umbrel device and would like to participate, you can use the Web GUI or CLI:

## Install via Umbrel Web GUI

1. Login to Umbrel

2. Click on App store Icon

3. Click on IPFS Podcasting

4. Click install

## Install via Umbrel CLI

1. SSH into your umbrel:

  ```bash
  ssh umbrel@umbrel.local
  ```

2. Create app directories & download/install docker-compose.yml:

  ```bash
  cd ~/umbrel
  mkdir -p apps/ipfs-podcasting/cfg
  mkdir -p apps/ipfs-podcasting/ipfs
  wget https://raw.githubusercontent.com/Cameron-IPFSPodcasting/podcastnode/main/docker-compose.yml -O apps/ipfs-podcasting/docker-compose.yml
  ```

3. Install IPFS Podcasting

  ```bash
  ./scripts/app install ipfs-podcasting
  ```

4. You can browse the Web UI at <http://umbrel.local:8675/> and configure your email address to manage the node at <https://ipfspodcasting.net/Manage> You can also view the communication log to view activity.

![image](https://user-images.githubusercontent.com/103131615/163454574-e16e6d47-9c75-4174-be0b-901132cf9f17.png)

## Uninstall via Umbrel CLI

To uninstall the app (!!! This will delete your IPFS configuration and all the files in your IPFS repository !!!)...

  ```bash
  ./scripts/app uninstall ipfs-podcasting
  ```

## Other useful commands (from the "~/umbrel" directory)

### Stop the app

  ```bash
  ./scripts/app stop ipfs-podcasting
  ```

### Download a new docker image

  ```bash
  docker pull ipfspodcasting/podcastnode:v0.6
  ```

### Start the app

  ```bash
 ./scripts/app start ipfs-podcasting
  ```

### Launch a command shell to execute IPFS commands...

  ```bash
  docker exec -ti ipfs-podcasting_web_1 sh
  ```

*Note*: If your Umbrel is behind a firewall, you may need to adjust firewall rules and/or port-foward allow traffic to port 4001 (both tcp/upd source/destination ports from your Umbrel IP address).
