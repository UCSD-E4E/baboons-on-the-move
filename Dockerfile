FROM jupyter/scipy-notebook
RUN python3 -m pip install opencv-python opencv-contrib-python scikit-image pika

WORKDIR /home/jovyan/baboon_tracking

ADD dist $HOME/baboon_tracking/

# install baboon_tracking python package
USER root
#RUN python3 setup.py install
RUN python3 -m pip install $(ls | grep .whl | head -1)

# expose port that jupyter operates on
EXPOSE 8888

CMD jupyter notebook --allow-root
