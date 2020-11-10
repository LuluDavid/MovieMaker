FILENAME=test.mp4
IMAGE_NAME=movie_maker
CONTAINER_NAME=movie_container

all : build run clean

clean : clean_container clean_image

build :
	sudo docker build -t ${IMAGE_NAME} .

run :
	sudo docker run --memory="10g" --memory-swap="10g" --name ${CONTAINER_NAME} ${IMAGE_NAME}
	sudo docker cp ${CONTAINER_NAME}:/${FILENAME} ./${FILENAME}

clean_container :
	sudo docker rm ${CONTAINER_NAME}

clean_image :
	sudo docker rmi ${IMAGE_NAME}

