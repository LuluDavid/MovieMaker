FILENAME=test.mp4
IMAGE_NAME=movie_maker
CONTAINER_NAME=movie_container

all : build run clean

build : 
	sudo docker build -t ${IMAGE_NAME} .

run : 
	sudo docker run --name ${CONTAINER_NAME} ${IMAGE_NAME}
	sudo docker cp ${CONTAINER_NAME}:/${FILENAME} ./${FILENAME}

clean : 
	sudo docker rm ${CONTAINER_NAME}
	sudo docker rmi ${IMAGE_NAME}