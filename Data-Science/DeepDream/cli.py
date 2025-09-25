import argparse
from utils import load_image, save_image, resize_to_longer_side
from dream import run_deep_dream

def main(argv=None):
    ap = argparse.ArgumentParser(description='Deep Dream (TensorFlow) CLI')
    ap.add_argument('--input', required=True, help='Path to input image')
    ap.add_argument('--output', required=True, help='Path to save output image')
    ap.add_argument('--max-dim', type=int, default=1280, help='Resize longest side (0=keep)')
    ap.add_argument('--layers', default='mixed3,mixed5', help='Comma-separated InceptionV3 layer names')
    ap.add_argument('--layer-weights', help='Comma-separated weights matching --layers')
    ap.add_argument('--octaves', type=int, default=3)
    ap.add_argument('--octave-scale', type=float, default=1.4)
    ap.add_argument('--steps-per-octave', type=int, default=50)
    ap.add_argument('--step-size', type=float, default=0.01)
    ap.add_argument('--tile-size', type=int, default=256)
    ap.add_argument('--tv-weight', type=float, default=0.0)
    ap.add_argument('--jitter', type=int, default=8)
    ap.add_argument('--seed', type=int, help='Random seed')
    args = ap.parse_args(argv)

    img = load_image(args.input)
    if args.max_dim and args.max_dim > 0:
        img = resize_to_longer_side(img, args.max_dim)

    layers = [s.strip() for s in args.layers.split(',') if s.strip()]
    weights = None
    if args.layer_weights:
        parts = [p.strip() for p in args.layer_weights.split(',') if p.strip()]
        weights = [float(p) for p in parts]

    out = run_deep_dream(
        img=img,
        layers=layers,
        layer_weights=weights,
        steps_per_octave=args.steps_per_octave,
        step_size=args.step_size,
        octaves=args.octaves,
        octave_scale=args.octave_scale,
        tile_size=args.tile_size,
        tv_weight=args.tv_weight,
        jitter=args.jitter,
        seed=args.seed,
    )
    save_image(out, args.output)
    print(f"Saved dream image -> {args.output}")

if __name__ == '__main__':
    main()