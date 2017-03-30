FROM amancevice/pandas:0.19-python3

# alpine base image is lacking some repositories, frequently causing
# downtime when updating packages
# RUN cp apk_repositories /etc/apk/repositories
RUN apk update

RUN apk add gcc g++ make libffi-dev openssl-dev python3-dev build-base --update-cache
RUN apk add nodejs git postgresql postgresql-dev
RUN mkdir /ve
RUN pyvenv --system-site-packages /ve/std

COPY requirements.txt /

RUN pip install -r /requirements.txt

# http://bitjudo.com/blog/2014/03/13/building-efficient-dockerfiles-node-dot-js/
COPY package.json /tmp/package.json
RUN cd /tmp && npm install
RUN mkdir -p /autoapi && cp -a /tmp/node_modules /autoapi/

COPY . /autoapi

WORKDIR /autoapi
CMD /autoapi/run_in_docker.sh
