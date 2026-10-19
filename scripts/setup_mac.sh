#!/usr/bin/env bash
# 项目分别安装到 .envs，避免老版 SadTalker 与较新语音项目发生依赖冲突。
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "此安装脚本面向原生 arm64 的苹果芯片 Mac。请在 Mac 的原生终端运行。"
  exit 1
fi
if ! command -v conda >/dev/null; then
  echo "请先安装 arm64 Miniforge：https://github.com/conda-forge/miniforge"
  exit 1
fi
create_env() {
  if [[ -f "$ENV_PATH/conda-meta/history" ]]; then
    echo "复用已有环境：$ENV_PATH"
  elif [[ -e "$ENV_PATH" ]]; then
    echo "该路径已存在但不是 conda 环境，请先选择其他环境位置：$ENV_PATH"
    exit 1
  else
    conda create -y -p "$ENV_PATH" -c conda-forge "$@"
  fi
}
case "${1:-}" in
  voice)
    ENV_PATH="$TASK_ROOT/.envs/f5-tts"
    create_env python=3.11 pip ffmpeg
    conda run -p "$ENV_PATH" python -m pip install torch torchaudio
    conda run -p "$ENV_PATH" python -m pip install -e "$TASK_ROOT/projects/F5-TTS"
    ;;
  motion)
    ENV_PATH="$TASK_ROOT/.envs/liveportrait"
    create_env python=3.10 pip ffmpeg
    # 官方 requirements_macOS.txt 中已包含配套的 PyTorch 和 ONNX Runtime。
    (cd "$TASK_ROOT/projects/LivePortrait" && conda run -p "$ENV_PATH" python -m pip install -r requirements_macOS.txt)
    conda run -p "$ENV_PATH" python -m pip install 'huggingface_hub<1'
    ;;
  talking)
    ENV_PATH="$TASK_ROOT/.envs/sadtalker"
    create_env python=3.10 pip ffmpeg dlib
    # 上游仍使用旧 torchvision 接口及 numpy 1.x，单独使用兼容组合。
    conda run -p "$ENV_PATH" python -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
    conda run -p "$ENV_PATH" python -m pip install -r "$TASK_ROOT/projects/SadTalker/requirements.txt" \
      numpy==1.23.4 numba==0.57.1 gradio==3.50.2 Pillow==9.5.0
    ;;
  *)
    echo "用法：bash scripts/setup_mac.sh voice|motion|talking"
    exit 2
    ;;
esac
echo "安装结束：$ENV_PATH"
echo "运行方法见本目录 README.md。首次生成/下载权重需要联网，课堂播放本地素材不需要。"
