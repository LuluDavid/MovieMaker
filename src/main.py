from exiftool import ExifTool
from datetime import datetime, timedelta
from os.path import join, isfile, splitext
from collections import OrderedDict
from os import listdir
from moviepy.editor import *
from moviepy.video.fx.resize import resize
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
from argparse import ArgumentParser
import sys
import multiprocessing

# Changing imagemagick's directory
# Get arguments
parser = ArgumentParser(description="Get the resource folders")
parser.add_argument("-r", "--resources", metavar="resource_folder", type=str, nargs=1,
                    help="The relative path of your video resource folder")
parser.add_argument("-o", "--output", metavar="output_file", type=str, nargs=1,
                    help="The relative path of your output file")
args = vars(parser.parse_args())
# Directories
r_opt = "resources"
o_opt = "output"
if r_opt not in args or o_opt not in args:
    parser.print_help()
    sys.exit()
video_dir = args[r_opt][0]
output_file = args[o_opt][0]
print("Merging from videos in ", video_dir, " to file ", output_file, "...")
text_duration = 5  # 3 seconds
crossfade_duration = 0.5  # 1 second
files = listdir(video_dir)
line_break = 2*"\n"
# Whether we use vertical or horizontal clips here
vertical = True
comment_tag = 'QuickTime:Comment'
date_tag = 'File:FileModifyDate'
# Compute max width and height
data = OrderedDict()
max_ratio = 0
max_height = 0
# Depends on Exif ?
delta = 2
print("PRE-PROCESSING...")
for file in files:
    full_file = join(video_dir, file)
    print("Pre-processing " + full_file + "...")
    if file.endswith(".mp4") | file.endswith(".m4v") | file.endswith(".gif") | file.endswith(".mov") & \
            isfile(full_file):
        clip = VideoFileClip(full_file)
        with ExifTool() as et:
            filename = splitext(file)[0]
            # Get tags
            comment = et.get_tag(comment_tag, full_file)
            location = "" if comment is None else line_break + comment
            date = et.get_tag(date_tag, full_file)[:18]
            if date is None or str(date) == "0000:00:00 00:00:00":
                print("Ignoring", file, "(null date)")
                continue
            else:
                date = datetime.strptime(date, "%Y:%m:%d %H:%M:%S") + timedelta(hours=delta)
            # Build desc
            desc = filename + location + line_break + date.strftime("%d/%m/%Y %H:%M")
            width, height = clip.size
            # Seems that moviepy does not compute the resolution
            # for the rotated clip, thus rotate it manually
            if clip.rotation % 180 == 90:
                clip = resize(clip, (height, width))
                width, height = clip.size
            # Register the rotated video
            data[date] = (clip, desc)
            # Maximize the size of the video to the screen
            ratio = width/height
            if max_ratio < ratio:
                max_ratio = ratio
            if max_height < height:
                max_height = height
# Sort by date
data = OrderedDict(sorted(data.items()))
print("DONE")
max_width = int(max_height*max_ratio)
max_size = (max_width, max_height)
print("Final video width : ", max_width, ", height : ", max_height, "ratio :", max_ratio)

def compute_ratio(w, h):
    width_ratio = max_width/w
    height_ratio = max_height/h
    return min(width_ratio, height_ratio)


print("PROCESSING...")
# Initial clip
title = "Le Zoo, que s'est-il passé en 3 ans ?"
initial_text = TextClip(text=title, bg_color="black", color='white', method='caption', font_size=70, size=max_size)\
    .with_duration(text_duration)
initial_clip = initial_text.fx(crossfadein, crossfade_duration).fx(crossfadeout, crossfade_duration)
builder = [initial_clip]
time = initial_clip.end-crossfade_duration
# Concatenate successively all videos
for k, pair in data.items():
    clip, desc = pair
    print("Processing "+clip.filename+"...")
    width, height = clip.size
    # Compute transition clip
    transition_text = TextClip(text=desc, bg_color="black", color='white', method='caption', font_size=70,
                               size=max_size).with_duration(text_duration).with_start(time)
    transition = transition_text.fx(crossfadein, crossfade_duration).fx(crossfadeout, crossfade_duration)
    time = transition.end - crossfade_duration
    # Resize and compute main clip
    ratio = compute_ratio(width, height)
    clip = resize(clip, ratio).with_start(time).with_position('center')
    clip = clip.fx(crossfadein, crossfade_duration).fx(crossfadeout, crossfade_duration)
    time = clip.end - crossfade_duration
    # Add it to the video
    builder.append(transition)
    builder.append(clip)
print("DONE")
# Add the ending text
end_text = "À bientôt pour le retour des héros"
final_text = TextClip(text=end_text, bg_color="black", color='white', method='caption', font_size=70,
                      size=max_size).with_duration(text_duration).with_start(time)
final_clip = final_text.fx(crossfadein, crossfade_duration).fx(crossfadeout, crossfade_duration)
builder.append(final_clip)
final_video = CompositeVideoClip(builder)
# Output the final video
threads = multiprocessing.cpu_count()
print("Outputing the final video with CPU (", threads, "threads)")
final_video.write_videofile(output_file,
                            threads=threads,
                            fps=24,
                            codec='libx264',
                            audio_codec='aac',
                            temp_audiofile='temp-audio.m4a',
                            remove_temp=True)
