# podcastnode

An Umbrel Docker App that provides IPFS storage and hosting for IPFSPodcasting.net (Crowd hosting & Self hosting of podcast episodes over IPFS). If you have an Umbrel device and would like to test...

SSH into your umbrel...

	ssh umbrel@umbrel.local
	
Create app directories & download/install docker-compose.yml...

	cd ~/umbrel
	mkdir -p apps/ipfs-podcasting/cfg
	mkdir -p apps/ipfs-podcasting/ipfs
	wget https://raw.githubusercontent.com/Cameron-IPFSPodcasting/podcastnode/main/docker-compose.yml -O apps/ipfs-podcasting/docker-compose.yml

Install the app...
	
	./scripts/app install ipfs-podcasting

You can browse the Web UI at http://umbrel.local:8657 and configure your email address to manage the node at https://ipfspodcasting.net/Manage You can also view the communication log to view activity.

![image](https://user-images.githubusercontent.com/103131615/163454574-e16e6d47-9c75-4174-be0b-901132cf9f17.png)

The app will not appear on your umbrel dashboard, but it will show Disk and memory usage with a broken image icon (because it's not an official app).

![image](https://user-images.githubusercontent.com/103131615/163454975-e0b52b3c-a6bf-42ce-920b-291091c00c0f.png)

To unstall the app (!!! This will delete your IPFS configuration and all the files in your IPFS repository !!!)...

	./scripts/app uninstall ipfs-podcasting


Other useful commands (from the "~/umbrel" directory)...

Stop the app...

	./scripts/app stop ipfs-podcasting

Download a new docker image...

	docker pull ipfspodcasting/podcastnode:v0.5

Start the app...

	./scripts/app start ipfs-podcasting

Launch a command shell to execute IPFS commands...

	docker exec -ti ipfs-podcasting_web_1 sh


*If your Umbrel is behind a firewall, you may need allow traffic to port 4001 (both tcp/upd source/destination ports from your Umbrel IP address).
