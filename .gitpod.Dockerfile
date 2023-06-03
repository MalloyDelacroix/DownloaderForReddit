FROM gitpod/workspace-full-vnc

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/

RUN sudo apt update -y
RUN sudo apt upgrade -y
RUN sudo apt install qtcreator -y
RUN pyenv install 3.8.16 -v
RUN /home/gitpod/.pyenv/versions/3.8.16/bin/python3.8 -m pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt