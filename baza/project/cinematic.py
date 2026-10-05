"""Film-look grade for a finished edit: muted teal/orange colour, soft highlight glow,
film grain, vignette and 2.39:1 letterbox bars.

usage: python3 cinematic.py ../final/knight.mp4 ../final/knight-cinematic.mp4
"""
import subprocess
import sys

src, dst = sys.argv[1], sys.argv[2]
W, H = 1280, 720
BAR = round((H - W / 2.39) / 2)  # letterbox bar height

grade = ",".join([
    "eq=saturation=0.84:contrast=1.06:gamma=1.06",
    # gentle S-curve, lifted blacks
    "curves=master='0/0.04 0.25/0.24 0.5/0.54 0.75/0.81 1/0.97'",
    # cool shadows, warm highlights
    "colorbalance=rs=-0.06:gs=-0.01:bs=0.07:rh=0.06:gh=0.02:bh=-0.05",
])
fc = (
    f"[0:v]{grade},split[base][hi];"
    # halation: blur only the bright parts and add them back softly
    "[hi]lutyuv=y='if(gt(val,200),val,0)':u=128:v=128,gblur=sigma=18[glow];"
    "[base][glow]blend=all_mode=screen:all_opacity=0.25,"
    "vignette=angle=PI/7,"
    "noise=c0s=7:c0f=t+u,"
    f"drawbox=x=0:y=0:w={W}:h={BAR}:color=black:t=fill,"
    f"drawbox=x=0:y={H - BAR}:w={W}:h={BAR}:color=black:t=fill[v]"
)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc,
                "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", dst], check=True)
print("wrote", dst)
