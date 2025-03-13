FROM debian:bookworm

RUN apt-get update -y
RUN apt install curl sudo -y

RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt install -y python3.11-venv
RUN python --version
# RUN curl -fsSL https://ollama.com/install.sh | sh


RUN apt-get update && apt-get install git -y
RUN useradd -m dev && echo "dev:dev" | chpasswd && adduser dev sudo

RUN mkdir -p /home/dev

# WORKDIR /home/dev
# COPY ./requirements.txt ./
# RUN ls -la
# RUN cat requirements.txt
# RUN pip install --no-cache-dir --user -r requirements.txt

COPY ./requirements.txt /home/dev/requirements.txt
COPY ./init.sh /home/dev/init.sh

USER dev


CMD [ "/home/dev/init.sh" ]