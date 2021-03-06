.PHONY: push, build, start, stop, dev-start, lint, gcp-upload, preprocess, train

-include .env

#note, containing grc.io tells docker push what address to push the image to
CONTAINER_NAME=slay-the-spire-ml

push: build
	docker tag $(CONTAINER_NAME):latest tensorduck/$(CONTAINER_NAME):latest
	docker push tensorduck/$(CONTAINER_NAME):latest

build:
	docker build -f Dockerfile -t $(CONTAINER_NAME):latest .

build-dev:
	docker build -f Dockerfile.scripts -t $(CONTAINER_NAME):dev .

start: build
	docker run --rm -p 8080:8080 --name $(CONTAINER_NAME) -dt $(CONTAINER_NAME):latest

stop:
	docker stop $(CONTAINER_NAME)

dev-start:
	PYTHONPATH=`pwd` streamlit run app.py

lint:
	black slayer
	isort slayer

preprocess: build-dev
	docker run --rm --name $(CONTAINER_NAME)_script -v $(PWD):/mnt -t $(CONTAINER_NAME):dev python /mnt/scripts/preprocess.py

train: build-dev
	docker run --rm --name $(CONTAINER_NAME)_script -v $(PWD):/mnt -t $(CONTAINER_NAME):dev python /mnt/scripts/train.py

preprocess-go:
	go run scripts/preprocess.go -cpuprofile cpu.profn