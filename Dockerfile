FROM python:3

# Install exiftool
RUN apt-get -y update && apt-get -y install exiftool ghostscript
RUN pip3 install pyexiftool setuptools argparse

# Install numpy using system package manager
RUN apt-get -y update && apt-get -y install ffmpeg imagemagick
# Last version of moviepy
RUN git clone https://github.com/Zulko/moviepy.git ./moviepy
RUN cd moviepy/ && pip3 install .
RUN cd .. && rm -rf moviepy

# Install some special fonts we use in testing, etc..
RUN apt-get -y install fonts-liberation
RUN apt-get install -y locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

# modify ImageMagick policy file so that Textclips work correctly.
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml
ADD src/main.py ./src/main.py
COPY src/resources ./src/resources
ENTRYPOINT ["python3", "./src/main.py", "-r", "./src/resources/", "-o", "./test.mp4"]
