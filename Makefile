.PHONY: all
all: docker-build docker-run

.PHONY: build
build:
	sudo python3 setup.py bdist_wheel	

.PHONY: docker-build
docker-build: build
	docker build -t ucsde4e/baboon_tracking .

.PHONY: docker-run
docker-run:
	docker-compose up

.PHONY: docker-push
docker-push:
	docker image push ucsde4e/baboon_tracking

.PHONY: push
push: docker-push

.PHONY: install
install:
	sudo python3 setup.py install
