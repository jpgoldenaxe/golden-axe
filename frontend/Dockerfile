FROM node:16-slim

RUN npm install -g create-react-app react-scripts
COPY project /home/node/project
RUN chown -R node /home/node/project
USER node
ENV HOME /home/node
WORKDIR $HOME/project
RUN npm install
