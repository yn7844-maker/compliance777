"""Explicit, one-time model download; runtime server stays offline."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Download BAAI/bge-m3 model files once (Internet required).')
    parser.add_argument('--output', required=True, help='Local model directory; allow several GB of disk space.')
    args = parser.parse_args()
    from huggingface_hub import snapshot_download
    target = Path(args.output).expanduser().resolve()
    snapshot_download(repo_id='BAAI/bge-m3', local_dir=str(target), allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'tokenizer*', '1_Pooling/*'])
    print(f'Model downloaded. Set BGE_MODEL_PATH to: {target}')


if __name__ == '__main__':
    main()
