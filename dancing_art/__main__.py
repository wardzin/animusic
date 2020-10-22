import os
import platform
import PySimpleGUIQt as sg
from concurrent.futures import ThreadPoolExecutor
from . import anim


def main():
    win_width, win_height = 600, 300

    layout = [
        [sg.Text('Input Image or Video'), sg.Input(key='input'), sg.FileBrowse(file_types=(('Image or Video', '*.jpg *.jpeg *.png *.gif *.mp4 *.mov *.flv *.avi *.webm *.mkv'), ('All Files', '*.*')))],
        [sg.Text('Audio'), sg.Input(key='audio'), sg.FileBrowse(file_types=(('Audio', '*.mp3 *.mpeg *.aiff *.wav *.flac *.ogg *.aac',), ('All Files', '*.*')))],
        [sg.Text('Output Video'), sg.Input(key='output'), sg.FileSaveAs(file_types=(('MP4 Video', '*.mp4'), ('All Files', '*.*')))],
        # [sg.Frame('Video Enconding Options', layout=[
        #     [sg.Text('Frames per second'), sg.Spin([i for i in range(24, 61)], initial_value=30)],
        #     [sg.Text('Encoding speed'), sg.Combo(['very fast', 'fast', 'medium', 'slow', 'very slow'], default_value='medium')],
        #     [sg.Text('Additional FFmpeg parameters'), sg.InputText('-bf 2 -b_strategy 2')],
        # ])],
        [sg.Button('Animate', key='Animate')],
    ]

    window = sg.Window('Dancing Art', layout, size=(win_width, win_height))
    
    with ThreadPoolExecutor(1) as executor:
        animation_thread = None

        while True:
            event, values = window.read(timeout=100)

            if event == sg.WIN_CLOSED:
                break

            if event == 'Animate':
                if not values['output'].endswith('.mp4'):
                    window['output'].update(values['output']+'.mp4')
                    values['output'] += '.mp4'

                animation_thread = executor.submit(anim.create_animation,
                    img=values['input'],
                    audio=values['audio'],
                    output=values['output'],
                )
                window['Animate'].update(disabled=True, text='Running...')

            if animation_thread is not None and animation_thread.done():
                try:
                    animation_thread.result()  # we call this to propagate errors to the main thread
                except Exception as e:
                    print(e)

                animation_thread = None

                window['Animate'].update(disabled=False, text='Animate')

                if platform.system() == 'Windows':
                    os.system(values['output'])
                elif platform.system() == 'Darwin':
                    os.system('open ' + values['output'])
                elif platform.system() == 'Linux':
                    os.system('xdg-open ' + values['output'])
                
    window.close()


if __name__ == '__main__':
    main()
