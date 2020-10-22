import librosa
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import PIL
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from moviepy import editor
from functools import partial
from tqdm import tqdm
from . import effects


def mins_to_secs(time_str):
    mins, secs = time_str.split(':')
    mins = int(mins) * 60
    secs = int(secs)
    return mins + secs


def secs_to_mins(secs):
    mins, secs = secs // 60, secs % 60
    return f'{mins:01d}:{secs:02d}'


def draw_visualizer(S_frame, height=1000, width=1000, dpi=100):
    fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi)
    canvas = FigureCanvas(fig)

    ax = fig.gca()
    ax.axis('off')
    fig.tight_layout()
    fig.patch.set_alpha(0)

    ax.set_ylim([0, 1])
    ax.bar(np.arange(S_frame.shape[0]), S_frame*0.2, color='#ab20fd')

    canvas.draw()       # draw the canvas, cache the renderer
    s, (width, height) = canvas.print_to_buffer()
    plt.close()
    
    return np.fromstring(s, np.uint8).reshape((height, width, 4))


def apply_effect(get_frame, t, effect, signals, convert_image=False):
        signal = signals.iloc[signals.index.get_loc(t ,method='nearest')]
        
        if signal == 0:
            return get_frame(t)
        else:
            if convert_image:
                return np.array(effect(PIL.Image.fromarray(get_frame(t), 'RGB'), signal=signal))
            else:
                return effect(get_frame(t), signal=signal)
            
            
# def apply_effect(frame, t, effect, signals, convert_image=False):
#         signal = signals.loc[t]
        
#         if signal == 0:
#             return frame
#         else:
#             if convert_image:
#                 return np.array(effect(Image.fromarray(frame, 'RGB'), signal=signal))
#             else:
#                 return effect(frame, signal=signal)


def create_animation(img='brigada.jpg', audio=None, video=None, output='dancing art.mp4', start_time=0, end_time=None, fps=30, frame_smoothing=4, visualizer=False):
    if isinstance(start_time, str):
        start_time = mins_to_secs(start_time)
    if isinstance(end_time, str):
        end_time = mins_to_secs(end_time)
        
    global original_image
    original_image = PIL.Image.open(img)
    
    print('Analyzing audio...')
    if video and not audio:
        y, sr = librosa.load(video, sr=None)
    else:
        y, sr = librosa.load(audio, sr=None)
    
    if end_time is None:
        end_time = librosa.get_duration(y, sr)
    y = y[int(start_time*sr):int(end_time*sr)]
    duration = end_time - start_time
    
    if video:
        video_clip = editor.VideoFileClip(video)
        fps = video_clip.fps
    else:
        video_clip = editor.ImageClip(img, duration=duration).set_fps(fps)
        
    if audio:
        audio_clip = editor.AudioFileClip(audio, fps=sr).subclip(t_start=start_time, t_end=end_time)
        video_clip = video_clip.set_audio(audio_clip)
    
    frame_times = []
    for t, frame in video_clip.iter_frames(with_times=True):
        frame_times.append(t)

    hop_length = int(np.round(sr/fps))
    win_length = int(np.round(frame_smoothing*sr/fps))
    n_fft = int(2**np.ceil(np.log2(win_length)))
    
    yh, yp = librosa.effects.hpss(y, margin=1)
    S = librosa.feature.melspectrogram(yp, sr=sr, power=1, n_fft=n_fft, hop_length=hop_length, win_length=win_length, window='blackman', center=False)
#     S = librosa.decompose.nn_filter(S, aggregate=np.median)
    rec = librosa.segment.recurrence_matrix(S, mode='affinity', metric='cosine', sparse=True)
    S = librosa.decompose.nn_filter(S, rec=rec, aggregate=np.average)

    
    components, activations = librosa.decompose.decompose(S, 2, sort=True)
#     bin_idx = np.argsort(components, axis=0)[components.shape[0] // 2]
#     activations = activations[np.argsort(bin_idx)]
    # low, mid, high = activations
    low, high = activations
    
    times = librosa.times_like(S, sr=sr, n_fft=n_fft, hop_length=hop_length)
    signals = pd.DataFrame({
        'low': low,
        # 'mid': mid,
        'high': high
    }, index=times)
#     signals = np.sqrt(signals)
    signals = (signals - signals.min()) / (signals.max() - signals.min())
#     signals /= signals.max()
#     min_cutoff = 0.25
#     max_cutoff = 0.45
#     signals = signals.clip(min_cutoff, max_cutoff)
#     signals = (signals - min_cutoff) / (max_cutoff - min_cutoff)
        
#     onset_env = librosa.onset.onset_strength(sr=sr, S=S)
#     beats = librosa.onset.onset_detect(sr=sr, onset_envelope=onset_env, units='time')
    signals = signals.reindex(frame_times, method='nearest')
#     signals = signals.rolling(6, win_type='blackman', center=True).mean().fillna(0)
#     signals = signals.clip(0)
    # signals.plot()
    # plt.show()
    signals = (signals - signals.min()) / (signals.max() - signals.min())
#     signals /= signals.max()

#     original_image = np.array(Image.open(img).convert('RGB'))
#     frames = []
#     for i, t in enumerate(tqdm(frame_times)):
# #         suspect_frames = [
# #             719,
# # #             838
# #         ]
# #         if i not in suspect_frames:
# #             continue
# #         print(i)30
#         frame = original_image.copy()
# #         print(frame.shape)
#         frame = apply_effect(frame, t, effect=sin_wave_distortion, signals=signals.high)
# #         print(frame.shape)
#         frame = apply_effect(frame, t, effect=chromatic_aberration, signals=signals.high)
#         frame = apply_effect(frame, t, effect=zoom, signals=signals.low)
#         frames.append(frame)
# #         if frame.shape != (998, 998, 3):
# #             print(i, t, frame.shape)

#     video_clip = ImageSequenceClip(frames, fps=fps)
#     audio_clip = AudioFileClip(audio, fps=sr).subclip(t_start=start_time, t_end=end_time)
#     video_clip = video_clip.set_audio(audio_clip)
        
#     Effects
    video_clip = (video_clip
        .fl(partial(
            apply_effect,
            effect=effects.chromatic_aberration,
            signals=signals.high,
        ))
        .fl(partial(
            apply_effect,
            effect=effects.sin_wave_distortion,
            signals=signals.high,
        ))
        .fl(partial(
            apply_effect,
            effect=effects.zoom,
            signals=signals.low,
        ))
    )
    
    if visualizer:
        print('Drawing visualizer...')

        bars = 64
        S = librosa.feature.melspectrogram(y, sr=sr, power=0.5, n_mels=bars, n_fft=n_fft, hop_length=hop_length, win_length=win_length, window='blackman')
        S = (S - S.min()) / (S.max() - S.min())

        visualizer_frames = []
        for S_frame in tqdm(S.T):
            frame = draw_visualizer(S_frame, height=video_clip.h, width=video_clip.w)
            visualizer_frames.append(frame)

        visualizer_clip = editor.ImageSequenceClip(visualizer_frames, fps=fps)
        video_clip = editor.CompositeVideoClip([video_clip, visualizer_clip])
    
    print('Rendering video...')
    # video_clip.preview()
    video_clip.write_videofile(output,
                               audio_codec='aac',
                               threads=os.cpu_count(),
                               preset='medium',
#                                preset='veryslow',
                               ffmpeg_params=['-bf', '2', '-b_strategy', '2']
                              )
