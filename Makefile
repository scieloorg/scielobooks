APP_VERSION := $(shell python setup.py --version)
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF := $(strip $(shell git rev-parse --short HEAD))
#IMAGE_FULLNAME := registry.scielo.org:5000/scieloorg/books-oai
IMAGE_FULLNAME := scieloorg/books-backoffice

clean:
	@ rm -f dist/*

build:
	@python setup.py bdist_wheel

build_image: clean build
	@docker build \
		-t $(IMAGE_FULLNAME):$(VCS_REF) \
		--build-arg WEBAPP_VERSION=$(APP_VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		--build-arg BUILD_DATE=$(BUILD_DATE) .
	@docker tag $(IMAGE_FULLNAME):$(VCS_REF) $(IMAGE_FULLNAME):latest
	@docker tag $(IMAGE_FULLNAME):$(VCS_REF) $(IMAGE_FULLNAME):$(APP_VERSION)

upload_image:
	@docker push $(IMAGE_FULLNAME)

.PHONY: clean build build_image upload_image
