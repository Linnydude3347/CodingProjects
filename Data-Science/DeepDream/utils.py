from __future__ import annotations
import os
import numpy as np
from PIL import Image
import tensorflow as tf

def load_image(path: str, max_dim: int = None) -> tf.Tensor:
    img = Image.open(path).convert('RGB')
    if max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    arr = np.array(img).astype('float32') / 255.0
    return tf.convert_to_tensor(arr[None, ...], dtype=tf.float32)  # [1,H,W,3]

def save_image(img_batch: tf.Tensor, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    arr = deprocess(img_batch)
    Image.fromarray(arr).save(path, quality=95)

def deprocess(img_batch: tf.Tensor) -> np.ndarray:
    x = tf.clip_by_value(img_batch[0], 0.0, 1.0)
    x = tf.image.convert_image_dtype(x, dtype=tf.uint8)
    return x.numpy()

def resize_to_longer_side(img_batch: tf.Tensor, max_side: int) -> tf.Tensor:
    _, h, w, _ = img_batch.shape
    scale = max_side / float(max(h, w))
    new_h, new_w = int(round(h * scale)), int(round(w * scale))
    return tf.image.resize(img_batch, (new_h, new_w), method='bilinear')