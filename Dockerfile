FROM tsutomu7/alpine-python-pandas
ADD . /autoapi
WORKDIR /autoapi

# alpine base image is lacking some repositories, frequently causing
# downtime when updating packages
# RUN cp apk_repositories /etc/apk/repositories
RUN apk update

RUN apk add gcc g++ make libffi-dev openssl-dev python3-dev build-base --update-cache
RUN apk add nodejs git postgresql postgresql-dev
RUN mkdir /ve
RUN pyvenv --system-site-packages /ve/std
RUN pip install -r /autoapi/requirements.txt
RUN npm install
CMD /autoapi/run_in_docker.sh
