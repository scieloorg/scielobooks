FROM centos:7
ENV PYTHONUNBUFFERED 1

ARG BUILD_DATE
ARG VCS_REF
ARG WEBAPP_VERSION

ENV IMAGE_BUILD_DATE ${BUILD_DATE}
ENV IMAGE_VCS_REF ${VCS_REF}
ENV IMAGE_WEBAPP_VERSION ${WEBAPP_VERSION}

RUN yum -y update && \
    yum -y install epel-release  && \
    yum groupinstall -y "Development Tools"  && \
    yum install -y python-devel  && \
    yum install -y python-pip  && \
    yum install -y python-pillow-devel  && \
    yum install -y zlib zlib-devel  && \
    yum install -y libjpeg libjpeg-devel  && \
    yum install -y freetype freetype-devel  && \
    yum install -y giflib giflib-devel  && \
    yum install -y postgresql-devel  && \
    yum clean all

# Installing swftools
COPY deps/swftools-2013-04-09-1007 /tmp/swftools-2013-04-09-1007
RUN cd /tmp/swftools-2013-04-09-1007 && \
    ./configure && \
    make && \
    cp lib/python/*.so /usr/lib/python2.7/site-packages

# Installing APP
COPY . /app
COPY production-TEMPLATE.ini /app/production.ini

WORKDIR /app

RUN pip install --upgrade pip && \
    pip --no-cache-dir install -r /app/requirements.txt && \
    python setup.py install

EXPOSE 6543

CMD gunicorn --paste /app/production.ini
