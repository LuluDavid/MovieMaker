FILENAME=test.mp4
IMAGE_NAME=movie_maker
CONTAINER_NAME=movie_container

all : build run clean

build : 
	docker build -t ${IMAGE_NAME} .

run : 
	docker run --name ${CONTAINER_NAME} ${IMAGE_NAME}
	docker cp ${CONTAINER_NAME}:/${FILENAME} ./${FILENAME}

clean : 
	docker rm ${CONTAINER_NAME}
	docker rmi ${IMAGE_NAME}