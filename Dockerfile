### Build Stage
#FROM --platform=$BUILDPLATFORM python:slim-buster AS build
#WORKDIR /ipfs-podcasting
#RUN apt-get update
#RUN apt-get upgrade -y
#RUN apt-get install -y wget apt-utils
#RUN wget https://dist.ipfs.io/ipfs-update/v1.8.0/ipfs-update_v1.8.0_linux-$TARGETARCH.tar.gz
#RUN tar xvzf ipfs-update_v1.8.0_linux-$TARGETARCH.tar.gz
#RUN ipfs-update/ipfs-update install latest

### Bundle Stage
FROM --platform=$BUILDPLATFORM python:slim-buster AS bundle
WORKDIR /ipfs-podcasting
#COPY --from=build /usr/local/bin/ipfs /usr/local/bin
RUN apt-get update
RUN apt-get install -y wget apt-utils
RUN pip3 install --no-cache-dir requests thread6 bottle
RUN mkdir /ipfs-podcasting/ipfs
ENV IPFS_PATH=/ipfs-podcasting/ipfs
ARG TARGETARCH
COPY ipfs-$TARGETARCH /usr/local/bin/ipfs
COPY *.py ./
COPY cfg cfg
COPY ipfspodcastnode.log .
#RUN /usr/local/bin/ipfs init
RUN chown -R 1000:1000 /ipfs-podcasting
USER 1000
ENTRYPOINT ["python", "ipfspodcastnode.py"]
EXPOSE 4001
EXPOSE 5001
#EXPOSE 8080
EXPOSE 8675
