.PHONY: all
all: build docker-build docker-run

.PHONY: build
build:
	sudo python3 setup.py bdist_wheel	

.PHONY: docker-build
docker-build:
	docker build -t anhdngo/baboon_tracking .

.PHONY: docker-run
docker-run:
	docker-compose up
