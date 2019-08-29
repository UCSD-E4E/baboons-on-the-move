FROM jupyter/scipy-notebook
RUN python3 -m pip install opencv-python opencv-contrib-python scikit-image pika

WORKDIR /home/jovyan/baboon_tracking

# add whl and utils
ADD dist/*.whl $HOME/baboon_tracking/
ADD utils $HOME/baboon_tracking/utils/
ADD *.yml $HOME/baboon_tracking/

# install baboon_tracking python package
USER root
RUN python3 -m pip install $(ls | grep .whl | head -1)

# delete whl
RUN rm *.whl

# expose port that jupyter operates on
EXPOSE 8888

# add jupyter notebook files
ADD *.ipynb $HOME/baboon_tracking/

CMD jupyter notebook --allow-root --NotebookApp.token=ucsde4e
