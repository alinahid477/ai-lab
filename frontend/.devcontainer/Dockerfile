FROM node:23-bookworm

RUN npm install -g typescript

RUN useradd -m dev && echo "dev:dev" | chpasswd && adduser dev sudo
# Switch to 'dev' user
USER dev

# Set working directory
CMD ["/bin/bash"]