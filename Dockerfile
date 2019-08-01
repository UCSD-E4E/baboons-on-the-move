FROM jupyter/scipy-notebook
RUN python3 -m pip install opencv-python opencv-contrib-python scikit-image

WORKDIR /home/jovyan/baboon_tracking

ADD . $HOME/baboon_tracking/

# install baboon_tracking python package
USER root
RUN python3 setup.py install
USER jovyan

# expose port that jupyter operates on
EXPOSE 8888

CMD ['jupyter', 'notebook']
