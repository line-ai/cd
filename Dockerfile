FROM tensorflow/serving

ENV MODEL_BASE_PATH /models
ENV MODEL_NAME jade

ADD https://storage.googleapis.com/jade-big/model-48k.tar.gz /model.tar.gz
RUN tar -zxvf /model.tar.gz
RUN mkdir -p /models/jade
RUN mv 1 /models/jade

# Fix because base tf_serving_entrypoint.sh does not take $PORT env variable while $PORT is set by Heroku
# CMD is required to run on Heroku
COPY tfs.sh /usr/bin/tf_serving_entrypoint.sh
RUN chmod +x /usr/bin/tf_serving_entrypoint.sh
ENTRYPOINT []
CMD ["/usr/bin/tf_serving_entrypoint.sh"]