# Animusic
Animusic is a Python package that allows you to easily create animated music videos with beautiful audio-reactive visual effects. All you need to do is provide an image or a video that you'd like to animate, as well as an audio file, and the rest is done for you!

## Features
* Uses the **librosa** library to process and filter the audio's spectrogram decomposition in order to translate the beats and sounds into visual effect intensity.
* Uses different effects for different frequencies to create more dynamic and responsive animations.
* Can animate both still images and videos.
* Supports all major image, video, and audio formats.
* Includes a user-friendly GUI made with **PySimpleGUI**.
* No tweaking necessary - the animation algorithm was specifically designed to work well out-of-the-box for most types of music.

## Requirements
This package requires [**ffmpeg**](https://www.ffmpeg.org/) to be installed in order to work.

### Linux
```sudo apt install ffmpeg```

### macOS
```brew install ffmpeg```

### Windows
A Windows binary of **ffmpeg** is already included with this package for convenience, so there is no need for you to install it.

## Installation
```pip install git+https://github.com/wardzin/animusic.git```

## Usage
To open the GUI, just run `animusic` from the command line.
