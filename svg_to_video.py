import os.path
import sys
import io
import numpy as np
import moviepy.video.io.ImageSequenceClip as ImageSequenceClip
from PIL import Image, ImageColor
from cairosvg import svg2png
from lxml import etree


def update_animation_for_frame(root, frame_time):
    for animate in root.xpath("//*[local-name()='animate' or local-name()='animateTransform' or local-name()='animateMotion']"):
        # Get the animation duration
        dur = float(animate.get("dur", "0").replace("s", ""))
        if dur == 0:
            continue

        # Calculate animation progress (from 0 to 1)
        progress = (frame_time % dur) / dur

        # Updating animation attributes
        if animate.get("attributeName") == "transform" and animate.get("type") == "translate":
            # Handling the animation of movement
            values = animate.get("values", "").split(";")
            key_times = list(map(float, animate.get("keyTimes", "").split(";")))
            # Find the current value based on the progress
            for i in range(len(key_times) - 1):
                if key_times[i] <= progress < key_times[i + 1]:
                    start_value = values[i]
                    end_value = values[i + 1]
                    start_x, start_y = map(float, start_value.split())
                    end_x, end_y = map(float, end_value.split())
                    # Interpolation
                    t = (progress - key_times[i]) / (key_times[i + 1] - key_times[i])
                    current_x = start_x + (end_x - start_x) * t
                    current_y = start_y + (end_y - start_y) * t
                    # Apply a new value to an element
                    parent = animate.getparent()
                    parent.set("transform", f"translate({current_x}, {current_y})")
                    break


def render_svg_frame(svg_content, frame_time, bg_color=None):
    root = etree.fromstring(svg_content)

    update_animation_for_frame(root, frame_time)

    updated_svg = etree.tostring(root)

    png_output = svg2png(bytestring=updated_svg)
    image = Image.open(io.BytesIO(png_output))

    if bg_color:
        background = Image.new("RGBA", image.size, ImageColor.getrgb(bg_color))
        background.paste(image, (0, 0), image)
        image = background

    return np.array(image)


def svg_to_video(input_svg, output_path, duration_seconds=10, fps=25, frames_only=False, bg_color=None):
    if frames_only:
        bg_color = None
    with open(input_svg, 'rb') as f:
        svg_content = f.read()

    total_frames = int(duration_seconds * fps)

    frames = []
    for frame_number in range(total_frames):
        frame_time = (frame_number / fps)

        frame = render_svg_frame(svg_content, frame_time, bg_color=bg_color)

        if frames_only:
            frame_image = Image.fromarray(frame)
            frame_image.save(os.path.join(output_path, f'frame_{frame_number:04d}.png'))
        else:
            frames.append(frame)
    if not frames_only:
        clip = ImageSequenceClip.ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(output_path, codec='libx264')


if __name__ == '__main__':
    args = sys.argv[1:]
    input_path = args[0] if len(args) >= 1 else ''
    output_path = args[1] if len(args) >= 2 else ''
    duration_seconds = int(args[2]) if len(args) >= 3 else 2
    fps = int(args[3]) if len(args) >= 4 else 25
    bg_color = args[4] if len(args) >= 5 else '#000000'
    frames_only = (args[4] == 'frames') if len(args) >= 5 else False
    if output_path and frames_only and not os.path.isdir(output_path):
        os.mkdir(output_path)
    svg_to_video(input_path, output_path, duration_seconds=duration_seconds, fps=fps, frames_only=frames_only, bg_color=bg_color)
