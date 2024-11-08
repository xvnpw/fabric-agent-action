FROM python:3.11

ENV FABRIC_VERSION=v1.4.94

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN wget -q -O fabric "https://github.com/danielmiessler/fabric/releases/download/${FABRIC_VERSION}/fabric-linux-amd64" && \
    chmod +x fabric && ./fabric && ./fabric -U

# using .dockeringore 
COPY . .
# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]