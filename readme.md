# svg_to_video

## Convert animated SVG to video  

~~~
sudo apt-get install librsvg2-bin
~~~

### Usage
5 seconds, 25 fps, #000000 - background color:
~~~
python svg_to_video.py \
'example/anim_orbit.svg' \
'output.mp4' \
5 25 '#dddddd'
~~~

Frames only:
~~~
python svg_to_video.py \
'example/anim_orbit.svg' \
'output_frames' \
5 25 frames
~~~

Libraries used:  
- https://pypi.org/project/CairoSVG/
- https://pypi.org/project/lxml/
- https://pypi.org/project/moviepy/
- https://pypi.org/project/pillow/
