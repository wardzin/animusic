# Animusic
Animusic is a Python package that allows you to easily create animated music videos with beautiful audio-reactive visual effects. All you need to do is provide an image or a video that you'd like to animate, as well as an audio file, and the rest is done for you!

## Features
* Uses [**librosa**](https://librosa.org/) to filter and process the audio in order to translate the beats and sounds into visual effect intensity.
* Uses different effects for different frequencies to create more dynamic and responsive animations.
* Can animate both images and videos.
* Supports all major image, video, and audio formats.
* Includes a user-friendly GUI made with [**PySimpleGUI**](https://github.com/PySimpleGUI/PySimpleGUI).
* No tweaking necessary - the animation algorithm was specifically designed to work well out-of-the-box for most types of music.

## Showcase
https://user-images.githubusercontent.com/1664699/117237477-0fe41580-adf9-11eb-834f-7ed80f4f703c.mp4

https://user-images.githubusercontent.com/1664699/117234423-f5a73900-adf2-11eb-9377-15736224f881.mp4

https://user-images.githubusercontent.com/1664699/117233721-ad3b4b80-adf1-11eb-9c12-5cdada513c17.mp4

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
