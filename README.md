# MovieMaker

### Introduction

This repository is a util to concatenate few videos into a final 
video montage, which are all separated by simple transition frames.  

I introduced it as a docker image, which seemed a bit more appropriate
as moviepy's requirements were not that simple to install.

The transition frames are black-background images with white text
giving the title of the video, the date it was shot, and whatever 
complementary information that is needed about the video. This information
can be added in the **comment** field of a video. The simplest way to fill
this comment field is to open the video with VLC, then open :  
window -> information about the media  
And fill the *Description* field. As for me, I use it to store the location
where the video was shot.  

The code is quite simple to modify, you just need to go in main.py
and modify the initial_text or final_text field to change the intro/outro
text, plus a few other details like the length of the transition frames,
and so on.  

### How to use it

First, you need to install docker on your computer, see the installation
steps [here](https://docs.docker.com/get-docker/).  

Once it's done, you need to run the daemon, which I do opening Docker Desktop
on OSX.  

Then, just place the clips you want to merge in a folder on your computer, and 
in the Dockerfile, at the last line, in :
```dockerfile
COPY src/resources ./src/resources
ENTRYPOINT ["python3", "./src/build.py", "-r", "./src/resources/", "-o", "./test.mp4"]
```
Replace ```src/resources``` with whatever ```path/to/resources``` you stored your video in.  

Then, you can build the image with ```make build```, which will compute all dependencies.  

Finally, you can run the python script with ```make run```, which will compute the final video,
and copy it in ```MovieMaker/test.mp4``` (which can also be changed above).  

If  you want to clean the built images and containers, you can run ```make clean```. All of
these steps can be performed at once with ```make all```.  

### Further improvements

This small util is mainly built thanks to [moviepy](https://github.com/Zulko/moviepy).

Make clean will soon be more precise, as it discards all images and containers now.  
Also, it would be better to pass the resource folder, the output file, the intial and
final texts, and the length of the transition frames and crossfades as cli arguments,
probably with ```build-args```, this should be done soon.  

If you have any suggestion, feel free to contact me at davidlulu92@yahoo.fr or to submit
a pull request.