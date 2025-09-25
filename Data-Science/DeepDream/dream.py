from __future__ import annotations
import random
from typing import List, Optional

import numpy as np
import tensorflow as tf

# ---------------------- Model & Loss ----------------------

def build_feature_model(layer_names: List[str]) -> tf.keras.Model:
    base_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet')
    outputs = []
    valid = set(l.name for l in base_model.layers)
    missing = [n for n in layer_names if n not in valid]
    if missing:
        raise ValueError(f"Unknown layer(s): {missing}. Example layers: 'mixed3','mixed5','mixed7'.")
    for name in layer_names:
        outputs.append(base_model.get_layer(name).output)
    return tf.keras.Model(inputs=base_model.input, outputs=outputs)

@tf.function
def _calc_loss(model: tf.keras.Model, img_batch: tf.Tensor, layer_weights: tf.Tensor) -> tf.Tensor:
    # img_batch: [1,H,W,3] in [0,1]
    # preprocess for InceptionV3 -> [-1,1]
    img_prep = tf.keras.applications.inception_v3.preprocess_input(img_batch * 255.0)
    features = model(img_prep)
    if not isinstance(features, (list, tuple)):
        features = [features]
    loss = tf.constant(0.0, dtype=tf.float32)
    for w, feat in zip(layer_weights, features):
        # Encourage large activations across spatial map
        # Normalize by feature map size to keep scales balanced
        loss += w * tf.reduce_mean(tf.square(feat))
    return loss

# ---------------------- Tiled Gradients ----------------------

def _tiled_gradients(model: tf.keras.Model, img: tf.Tensor, layer_weights: tf.Tensor, tile_size: int = 256, jitter: int = 0) -> tf.Tensor:
    # Random jitter to avoid seam artifacts
    if jitter:
        ox = tf.random.uniform((), -jitter, jitter, dtype=tf.int32)
        oy = tf.random.uniform((), -jitter, jitter, dtype=tf.int32)
        img = tf.roll(img, shift=[oy, ox], axis=[1,2])

    B, H, W, C = img.shape
    assert B == 1, "Batch size must be 1"
    grad = tf.zeros_like(img)

    ys = list(range(0, H, tile_size))
    xs = list(range(0, W, tile_size))
    # Ensure coverage of edges
    if ys[-1] != H - tile_size:
        ys = ys[:-1] + [max(0, H - tile_size)]
    if xs[-1] != W - tile_size:
        xs = xs[:-1] + [max(0, W - tile_size)]

    for y in ys:
        for x in xs:
            tile = img[:, y:y+tile_size, x:x+tile_size, :]
            with tf.GradientTape() as tape:
                tape.watch(tile)
                loss = _calc_loss(model, tile, layer_weights)
            g = tape.gradient(loss, tile)
            # Normalize tile grad to unit std
            g /= (tf.math.reduce_std(g) + 1e-8)
            # Scatter-add into the gradient canvas
            pad_top, pad_left = y, x
            pad_bottom, pad_right = H - (y + tile_size), W - (x + tile_size)
            g_full = tf.pad(g, [[0,0],[pad_top,pad_bottom],[pad_left,pad_right],[0,0]])
            grad = grad + g_full

    # Un-jitter
    if jitter:
        grad = tf.roll(grad, shift=[-oy, -ox], axis=[1,2])

    # Final normalization
    grad /= (tf.math.reduce_std(grad) + 1e-8)
    return grad

# ---------------------- Gradient Ascent Step ----------------------

def ascent_step(img: tf.Tensor, model: tf.keras.Model, layer_weights: tf.Tensor, step_size: float = 0.01, tile_size: int = 256, tv_weight: float = 0.0, jitter: int = 0) -> tf.Tensor:
    grad = _tiled_gradients(model, img, layer_weights, tile_size=tile_size, jitter=jitter)
    img = img + step_size * grad
    if tv_weight and tv_weight > 0.0:
        # Total variation regularization
        tv = tf.image.total_variation(img)
        # Compute gradient of TV
        with tf.GradientTape() as tape:
            tape.watch(img)
            tv_loss = tf.reduce_mean(tf.image.total_variation(img))
        tv_grad = tape.gradient(tv_loss, img)
        img = img - tv_weight * tv_grad
    img = tf.clip_by_value(img, 0.0, 1.0)
    return img

# ---------------------- Multi-Scale (Octaves) ----------------------

def run_deep_dream(
    img: tf.Tensor,
    layers: List[str] = None,
    layer_weights: Optional[List[float]] = None,
    steps_per_octave: int = 50,
    step_size: float = 0.01,
    octaves: int = 3,
    octave_scale: float = 1.4,
    tile_size: int = 256,
    tv_weight: float = 0.0,
    jitter: int = 0,
    seed: Optional[int] = None,
) -> tf.Tensor:
    """Run DeepDream on a single image tensor [1,H,W,3] in [0,1]."""
    if seed is not None:
        tf.random.set_seed(int(seed))
        np.random.seed(int(seed))
        random.seed(int(seed))

    layers = layers or ['mixed3','mixed5']
    model = build_feature_model(layers)
    if layer_weights:
        assert len(layer_weights) == len(layers), "layer_weights must match layers length"
        lw = tf.constant(layer_weights, dtype=tf.float32)
    else:
        lw = tf.ones((len(layers),), dtype=tf.float32) / float(len(layers))

    # Build octave scales: go from smaller to original size
    base_h = tf.shape(img)[1]
    base_w = tf.shape(img)[2]
    # Precompute target sizes
    sizes = []
    for i in reversed(range(octaves)):
        scale = (octave_scale ** -i)
        sizes.append((tf.cast(tf.cast(base_h, tf.float32) * scale, tf.int32),
                      tf.cast(tf.cast(base_w, tf.float32) * scale, tf.int32)))

    dream = img
    for oh, ow in sizes:
        dream = tf.image.resize(dream, (oh, ow), method='bilinear')
        for _ in range(steps_per_octave):
            dream = ascent_step(dream, model, lw, step_size=step_size, tile_size=max(tile_size, 96), tv_weight=tv_weight, jitter=jitter)
    # Final resize back to original
    dream = tf.image.resize(dream, (base_h, base_w), method='bilinear')
    dream = tf.clip_by_value(dream, 0.0, 1.0)
    return dream