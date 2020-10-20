import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageChops
# from scipy.ndimage import zoom as zoom_image
# from wand.image import Image as WandImage


def sin_wave_distortion(img, signal, mag=10, freq=20):
    """Return an image with rows shifted according to a sine curve.

    im: Pillow Image
    mag: The magnitude of the sine wave
    freq: The frequency of the sine wave
    phase: The degree by which the cycle is offset (rads)
    """
    img = img.copy()
    phase = -2 * np.pi * signal
    mag = mag * signal
    height = img.shape[0]
    offsets = (mag * np.sin(2 * np.pi * freq * (np.arange(height) / height) + phase)).astype(int)
    for offset in np.unique(offsets):
        idx = (offsets==offset)
        img[idx] = np.roll(img[idx], offset, axis=1)
    return img


def chromatic_aberration(img, signal, mag=10):
    """
    Return an image where the color channels are horizontally offset.

    The Red and Blue color channels are horizontally offset from the Green
    channel left and right respectively.

    im: RGB array
    offset: distance in pixels the color channels should be offset by
    """
    img = img.copy()
    offset = int(mag * signal)
    img[:,:,0] = np.roll(img[:,:,0], -offset)
    img[:,:,2] = np.roll(img[:,:,2], offset)
    return img


def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


def make_noise_data(length, min_luminosity=0, max_luminosity=0.75):
    """Return a list of RGB tuples of random greyscale values.

    length: The length of the list
    min_luminosity: The lowest luminosity value (between 0 and 1)
    max_luminosity: The brightest luminosity value (between 0 and 1)
    """
    noise_data = []
    for _ in range(length):
        l = round(np.random.uniform(min_luminosity, max_luminosity) * 255)
        rgb = (l,l,l)
        noise_data.append(rgb)
    return noise_data


def noise_bands(im, signal, mag=5):
    """Return an image with randomly placed full-width bands of noise.

    im: Pillow Image
    count: The number of bands of noise
    thickness: Maximum thickness of the bands
    """
    count = int(mag * signal)
    thickness = int(mag * signal)
    modified = im.convert('RGBA')
    boxes = [
        (0, ypos, im.size[0], ypos + np.random.randint(1, thickness))
        for ypos in np.random.choices(range(im.size[1]), k=count)
    ]
    for box in boxes:
        noise_cell = Image.new(modified.mode, (box[2]-box[0], box[3]-box[1]))
        noise_cell.putdata(
            make_noise_data(noise_cell.size[0] * noise_cell.size[1])
        )
        combined_cell = ImageChops.lighter(modified.crop(box), noise_cell)
        combined_cell.putalpha(128)
        modified.alpha_composite(combined_cell, (box[0], box[1]))

    return modified.convert(im.mode)


def _split_data(data, width):
    height = int(len(data) / width)
    return [
        data[(row * width):(row * width + width)]
        for row in range(height)
    ]


def _get_lum(rgb):
    return int(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])


def pixel_sort(im, signal, multiplier=2, reverse=True):
    """Return a horizontally pixel-sorted Image based on the mask function.

    The default sorting direction is dark to light from left to right.

    Pixel-sorting algorithm from: http://satyarth.me/articles/pixel-sorting/

    im: Pillow Image
    mask_function: function that takes a pixel's luminance and returns
        255 or 0 depending on whether it should be sorted or not respectively.
    reverse: sort pixels in reverse order if True
    """
    median_lum = np.median(np.multiply(im, np.array([0.2126, 0.7152, 0.0722]), casting='unsafe').sum(axis=-1).astype(int))
    lum_limit = multiplier * median_lum # <- pixel sorting strength
    lum_limit = abs(lum_limit) if lum_limit <= 255 else 255
    mask_function = (lambda val, factor=signal, limit=lum_limit:
                    255 if val < limit * factor else 0)
    
    # Create a black-and-white mask to determine which pixels will be sorted
    interval_mask = im.convert('L').point(mask_function)
    interval_mask_data = list(interval_mask.getdata())
    interval_mask_row_data = _split_data(interval_mask_data, im.size[0])

    # Go row by row, recording the starting and ending points of each
    # contiguous block of white pixels in the mask
    interval_boxes = []
    for row_index, row_data in enumerate(interval_mask_row_data):
        for pixel_index, pixel in enumerate(row_data):
            # This is the first pixel on the row and it is white -> start box
            if pixel_index == 0 and pixel == 255:
                start = (pixel_index, row_index)
                continue
            # The pixel is white and the previous pixel was black -> start box
            if pixel == 255 and row_data[pixel_index - 1] == 0:
                start = (pixel_index, row_index)
                continue
            # This is the last pixel in the row and it is white -> end box
            if pixel_index == len(row_data) - 1 and pixel == 255:
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue
            # The pixel is (black) and (not the first in the row) and (the
            # previous pixel was white) -> end box
            if (pixel == 0 and pixel_index > 0 and
                    row_data[pixel_index - 1] == 255):
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue

    modified = im
    for box in interval_boxes:
        # Take the pixels from each box
        cropped_interval = modified.crop(box)
        interval_data = list(cropped_interval.getdata())
        # sort them by luminance
        cropped_interval.putdata(
            sorted(interval_data, key=_get_lum, reverse=reverse)
        )
        # and paste them back onto the image!
        modified.paste(cropped_interval, box=(box[0], box[1]))

    return modified


# def zoom(img, signal, max_zoom=0.1):
#     zoom_factor = 1 + max_zoom * signal
    
#     h, w = img.shape[:2]

#     # For multichannel images we don't want to apply the zoom factor to the RGB
#     # dimension, so instead we create a tuple of zoom factors, one per array
#     # dimension, with 1's for any trailing dimensions after the width and height.
#     zoom_tuple = (zoom_factor,) * 2 + (1,) * (img.ndim - 2)

#     # Zooming out
#     if zoom_factor < 1:
#         # Bounding box of the zoomed-out image within the output array
#         zh = int(np.round(h * zoom_factor))
#         zw = int(np.round(w * zoom_factor))
#         top = (h - zh) // 2
#         left = (w - zw) // 2

#         # Zero-padding
#         out = np.zeros_like(img)
#         out[top:top+zh, left:left+zw] = zoom_image(img, zoom_tuple, order=0)
    
#     # Zooming in
#     elif zoom_factor > 1:
#         # Bounding box of the zoomed-in region within the input array
#         zh = int(np.round(h / zoom_factor))
#         zw = int(np.round(w / zoom_factor))
#         top = (h - zh) // 2
#         left = (w - zw) // 2

#         out = zoom_image(img[top:top+zh, left:left+zw], zoom_tuple, order=0)

#         # `out` might still be slightly larger than `img` due to rounding, so
#         # trim off any extra pixels at the edges
#         trim_top = ((out.shape[0] - h) // 2)
#         trim_left = ((out.shape[1] - w) // 2)
#         out = out[trim_top:trim_top+h, trim_left:trim_left+w]

#     # If zoom_factor == 1, just return the input array
#     else:
#         out = img
#     return out

def zoom(img, signal, max_zoom=0.10):
    """
    Center zoom in/out of the given image and returning an enlarged/shrinked view of 
    the image without changing dimensions
    Args:
        img : Image array
        zoom_factor : amount of zoom as a ratio (0 to Inf)
    """
    zoom_factor = 1 + max_zoom * signal
    
    height, width = img.shape[:2] # It's also the final desired shape
    new_height, new_width = int(height * zoom_factor), int(width * zoom_factor)

    ### Crop only the part that will remain in the result (more efficient)
    # Centered bbox of the final desired size in resized (larger/smaller) image coordinates
    y1, x1 = max(0, new_height - height) // 2, max(0, new_width - width) // 2
    y2, x2 = y1 + height, x1 + width
    bbox = np.array([y1,x1,y2,x2])
    # Map back to original image coordinates
    bbox = (bbox / zoom_factor).astype(np.int)
    y1, x1, y2, x2 = bbox
    cropped_img = img[y1:y2, x1:x2]

    # Handle padding when downscaling
    resize_height, resize_width = min(new_height, height), min(new_width, width)
    pad_height1, pad_width1 = (height - resize_height) // 2, (width - resize_width) //2
    pad_height2, pad_width2 = (height - resize_height) - pad_height1, (width - resize_width) - pad_width1
    pad_spec = [(pad_height1, pad_height2), (pad_width1, pad_width2)] + [(0,0)] * (img.ndim - 2)

    result = cv2.resize(cropped_img, (resize_width, resize_height))
    result = np.pad(result, pad_spec, mode='constant')
    assert result.shape[0] == height and result.shape[1] == width
    return result

# def barrel_distortion(im, signal):
#     im_bytes = BytesIO()
#     im.save(im_bytes, format='png')
    
#     with WandImage(blob=im_bytes.getvalue()) as img:
#         img.virtual_pixel = 'white'
#         img.distort('barrel', (0.2, 0.0, 0.0, 0.8))

#         im_bytes = BytesIO(img.make_blob("png"))
#         im = Image.open(im_bytes)