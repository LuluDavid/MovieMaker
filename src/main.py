from os.path import isfile
from moviepy import *
from datetime import datetime, timedelta
from moviepy.video.fx import resize
from moviepy.video.fx import fadein, fadeout
from collections import OrderedDict
import multiprocessing

text_duration = 5
gmt = 2
line_break = 2*"\n"
crossfade_duration = 0  # TODO: it is deprecated for the moment

# Text stuff
text_size = 70
font = "Arial"
initial_text_duration = 7
end_text_duration = 7


def main(files, output_file):
    data, max_size = pre_process(files)
    print("Final video width : ", max_size[0], ", height : ", max_size[1])
    # Initial clip
    title = "Le Zoo, que s'est-il passé en 3 ans ?"
    init = initial_clip(title, initial_text_duration, max_size)
    builder = [init]
    time = initial_clip.end - crossfade_duration
    builder, time = process(data, time, builder, max_size)
    print("DONE")
    # Add the ending text
    end_text = "À bientôt pour le retour des héros"
    final = final_clip(end_text, time, end_text_duration, max_size)
    builder.append(final)
    final_video = CompositeVideoClip(builder)
    # Output the final video
    threads = multiprocessing.cpu_count()
    print("Outputting the final video with CPU (", threads, "threads)")
    final_video.write_videofile(output_file,
                                threads=threads,
                                fps=24,
                                codec='libx264',
                                audio_codec='aac',
                                temp_audiofile='temp-audio.m4a',
                                remove_temp=True)


def pre_process(files):
    # Compute max width and height
    data = OrderedDict()
    max_ratio = 0
    max_height = 0
    print("PRE-PROCESSING...")
    for file in files:
        if is_video_file(file):
            # TODO: get from database
            date = "2000:01:01 00:00:00"
            location = ""
            name = ""
            beginning = 0
            ending = 10
            clip = VideoFileClip(file, fps_source="tbr").subclip(beginning, ending)
            try:
                date = datetime.strptime(date, "%Y:%m:%d %H:%M:%S") + timedelta(hours=gmt)
            except ValueError:
                print("Ignoring", file, "(null date)")
                continue
            # Build desc
            desc = name + location + line_break + date.strftime("%d/%m/%Y %H:%M")
            width, height = clip.size
            # Seems that moviepy does not compute the resolution
            # for the rotated clip, thus rotate it manually
            if clip.rotation % 180 == 90:
                clip = resize(clip, (height, width))
                width, height = clip.size
            # Register the rotated video
            data[date] = (clip, desc)
            # Maximize the size of the video to the screen
            ratio = width / height
            if max_ratio < ratio:
                max_ratio = ratio
            if max_height < height:
                max_height = height
    # Sort by date
    data = OrderedDict(sorted(data.items()))
    max_width = int(max_height * max_ratio)
    max_size = (max_height, max_width)
    return data, max_size


def process(data, time, builder, max_size):
    max_width = max_size[0]
    for k, pair in data.items():
        clip, desc = pair
        print("Processing " + clip.filename + "...")
        width, height = clip.size
        # Compute transition clip
        transition_text = TextClip(text=desc, bg_color="black", color='white', method='caption', font_size=text_size,
                                   font=font, size=max_size).with_duration(text_duration).with_start(time)
        transition = transition_text.fx(fadein, crossfade_duration).fx(fadeout, crossfade_duration)
        time = transition.end - crossfade_duration
        # Resize and compute main clip
        ratio = compute_ratio(width, height, max_size)
        clip = resize(clip, ratio).with_start(time)
        width = clip.size[0]
        # If it doesn't fill the total width, center it
        clip = clip.with_position(((max_width - width) / 2, 0))
        clip = clip.fx(fadein, crossfade_duration).fx(fadeout, crossfade_duration)
        time = clip.end - crossfade_duration
        # Add it to the video
        builder.append(transition)
        builder.append(clip)
    return builder, time


def is_video_file(file):
    return file.endswith(".mp4") | file.endswith(".m4v") \
           | file.endswith(".gif") | file.endswith(".mov") & isfile(file)


def compute_ratio(w, h, max_size):
    max_width = max_size[0]
    max_height = max_size[1]
    width_ratio = max_width/w
    height_ratio = max_height/h
    return min(width_ratio, height_ratio)


def initial_clip(title, duration, max_size):
    initial_text = TextClip(text=title, bg_color="black", color='white', method='caption', font_size=text_size,
                            font=font,
                            size=max_size).with_duration(duration)
    return initial_text.fx(fadein, crossfade_duration).fx(fadeout, crossfade_duration)


def final_clip(end_text, time, duration, max_size):
    final_text = TextClip(text=end_text, bg_color="black", color='white', method='caption', font_size=text_size,
                          font=font, size=max_size).with_duration(duration).with_start(time)
    return final_text.fx(fadein, crossfade_duration).fx(fadeout, crossfade_duration)



