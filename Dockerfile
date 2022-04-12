### Build Stage
FROM --platform=$BUILDPLATFORM python:slim-buster AS build
WORKDIR /ipfs-podcasting
RUN apt-get update
RUN apt-get install -y wget
ARG TARGETARCH
RUN wget https://dist.ipfs.io/go-ipfs/v0.12.2/go-ipfs_v0.12.2_linux-$TARGETARCH.tar.gz
RUN tar xzf go-ipfs_v0.12.2_linux-$TARGETARCH.tar.gz
RUN cp go-ipfs/ipfs /usr/local/bin

### Bundle Stage
FROM --platform=$BUILDPLATFORM python:slim-buster AS bundle
WORKDIR /ipfs-podcasting
RUN apt-get update
RUN apt-get install -y wget net-tools
RUN pip3 install --no-cache-dir requests thread6 bottle
RUN mkdir /ipfs-podcasting/ipfs
ENV IPFS_PATH=/ipfs-podcasting/ipfs
COPY --from=build /usr/local/bin/ipfs /usr/local/bin
COPY *.py .
COPY *.png .
COPY cfg cfg
COPY ipfspodcastnode.log .
RUN chown -R 1000:1000 /ipfs-podcasting
USER 1000
ENTRYPOINT ["python", "ipfspodcastnode.py"]
EXPOSE 4001
EXPOSE 5001
#EXPOSE 8080
EXPOSE 8675
