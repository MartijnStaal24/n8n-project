FROM docker.n8n.io/n8nio/n8n:latest

USER root

# Installeer Python en pip
RUN apk add --update python3 py3-pip py3-pandas py3-scikit-learn py3-numpy

USER node