FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
ADD /config/requirements.txt /config/  
RUN pip install -r /config/requirements.txt
RUN mkdir /src;
RUN apt-get update
RUN wget http://download.osgeo.org/gdal/2.1.0/gdal-2.1.0.tar.gz && \
    tar -zxvf gdal-2.1.0.tar.gz && \
    cd gdal-2.1.0/  && \
    ./configure --prefix=/usr/ && \
    make && \
    make install && \
    cd swig/python/ && \
    python setup.py install
WORKDIR /src
RUN apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin

RUN apt-get update && apt-get upgrade -y