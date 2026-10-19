#!/usr/bin/env python3
"""教师自有或明确授权素材的课堂演示入口。模型依赖按项目分别安装。"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "assets" / "input"
OUTPUT = ROOT / "assets" / "output"
# 直接调用 .envs/.../bin/python 也能让上游找到同环境里的 FFmpeg。
os.environ["PATH"] = str(Path(sys.executable).absolute().parent) + os.pathsep + os.environ.get("PATH", "")


def require_file(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"找不到素材：{path}\n请先按 README.md 准备你本人或已获授权的素材。")
    return path


def output_path(value: str | Path, force: bool = False) -> Path:
    path = Path(value).expanduser().resolve()
    if path.exists() and not force:
        raise ValueError(f"文件已存在：{path}\n请换一个输出名，或明确使用 --force 覆盖。")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:
        raise ValueError("需要 FFmpeg。Mac 可在对应 conda 环境执行 conda install -c conda-forge ffmpeg。") from exc


def run(command: list[str], cwd: Path | None = None, dry_run: bool = False) -> None:
    print("执行：", shlex.join(command), flush=True)
    if dry_run:
        return
    env = os.environ.copy()
    env.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    subprocess.run(command, cwd=cwd, env=env, check=True)


def find_font(explicit: str | None = None) -> str:
    candidates = [explicit] if explicit else []
    candidates += [
        str(ROOT / "assets/fonts/NotoSansSC-Regular.ttf"),
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise ValueError("没有找到中文字体，请使用 --font 指定中文 .ttf 或 .ttc 文件。")


def label_video(source: Path, target: Path, font: str | None = None, force: bool = False) -> None:
    """将合成标识直接写进视频画面，不依赖可被忽略的文件名。"""
    from PIL import Image, ImageDraw, ImageFont

    if source.resolve() == target.resolve():
        raise ValueError("输入和输出不能是同一个文件。")
    exe = ffmpeg()
    frame = subprocess.run(
        [exe, "-v", "error", "-i", str(source), "-map", "0:v:0", "-frames:v", "1",
         "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout
    with Image.open(io.BytesIO(frame)) as image:
        width = image.width
    height = max(30, round(width * 0.075))
    with tempfile.TemporaryDirectory(prefix="classroom-label-") as tmp:
        banner = Image.new("RGBA", (width, height), (10, 20, 35, 235))
        draw = ImageDraw.Draw(banner)
        text = "AI 合成 · 教学演示"
        size = max(12, min(46, round(height * 0.53)))
        face = ImageFont.truetype(find_font(font), size)
        while draw.textbbox((0, 0), text, font=face)[2] > width - 16 and size > 8:
            size -= 1
            face = ImageFont.truetype(find_font(font), size)
        bounds = draw.textbbox((0, 0), text, font=face)
        draw.text((8, (height - (bounds[3] - bounds[1])) / 2 - bounds[1]), text,
                  font=face, fill=(222, 249, 125, 255))
        overlay = Path(tmp) / "label.png"
        banner.save(overlay)
        run([exe, "-hide_banner", "-loglevel", "error", "-y" if force else "-n",
             "-i", str(source), "-i", str(overlay), "-filter_complex",
             "[0:v][1:v]overlay=0:0:format=auto,pad=ceil(iw/2)*2:ceil(ih/2)*2,format=yuv420p[v]",
             "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(target)])


def voice(args: argparse.Namespace) -> None:
    ref = require_file(args.reference)
    ref_text = require_file(args.reference_text).read_text(encoding="utf-8").strip()
    text = args.text if args.text is not None else require_file(args.text_file).read_text(encoding="utf-8").strip()
    if not ref_text or not text.strip():
        raise ValueError("参考录音的逐字稿和生成台词都不能为空。")
    target = output_path(args.output, args.force)
    if args.dry_run:
        print(json.dumps({"model": "F5TTS_v1_Base", "device": args.device,
                          "ref_file": str(ref), "ref_text": ref_text,
                          "gen_text": text, "file_wave": str(target)}, ensure_ascii=False, indent=2))
        return
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    import soundfile as sf
    import torch
    from f5_tts.api import F5TTS

    duration = sf.info(str(ref)).duration
    if not 2 <= duration < 12:
        raise ValueError(f"参考录音为 {duration:.1f} 秒。请准备 2–12 秒以内的完整短句，建议 8–10 秒，并同步修改逐字稿。")
    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    if device == "mps" and not torch.backends.mps.is_available():
        raise ValueError("当前 Python 环境不能使用 MPS；苹果芯片请安装原生 arm64 PyTorch，或改用 --device cpu。")
    print(f"使用 {device}；首次运行会下载 F5-TTS 与 Vocos 权重，请在课前完成。", flush=True)
    model = F5TTS(model="F5TTS_v1_Base", device=device)
    # 写到临时路径，生成失败时不破坏已经存在的课堂素材。
    with tempfile.TemporaryDirectory(prefix="voice-", dir=target.parent) as tmp:
        generated = Path(tmp) / "voice.wav"
        model.infer(ref_file=str(ref), ref_text=ref_text, gen_text=text,
                    file_wave=str(generated), nfe_step=args.steps, seed=args.seed)
        shutil.move(str(generated), target)
    target.with_suffix(".json").write_text(json.dumps({
        "synthetic": True, "purpose": "课堂教学演示", "model": "F5-TTS / F5TTS_v1_Base",
        "text": text, "reference": str(ref), "seed": args.seed,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"声音已生成：{target}\n播放时请在课件上保留“本轮含合成片段”的提示，并在竞猜后立即揭晓。")


def portrait(args: argparse.Namespace, talking: bool) -> None:
    repo = ROOT / "projects" / ("SadTalker" if talking else "LivePortrait")
    require_file(repo / "inference.py")
    photo = require_file(args.photo)
    driving = require_file(args.audio if talking else args.driving)
    target = output_path(args.output, args.force)
    # 每次使用独立结果目录，避免误取以前生成的视频。
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    work = OUTPUT / "raw" / ("talking-" if talking else "motion-") / stamp
    command = [args.python or sys.executable, str(repo / "inference.py")]
    if talking:
        command += ["--source_image", str(photo), "--driven_audio", str(driving),
                    "--result_dir", str(work), "--size", "256", "--batch_size", "1", "--still"]
        if args.device == "cpu":
            command += ["--cpu"]
    else:
        command += ["-s", str(photo), "-d", str(driving), "-o", str(work), "--flag_crop_driving_video"]
    run(command, cwd=repo, dry_run=args.dry_run)
    if args.dry_run:
        print("生成成功后会自动写入“AI 合成 · 教学演示”标识。")
        return
    videos = sorted(work.rglob("*.mp4"))
    # SadTalker 的最终结果在 result_dir 内；LivePortrait 优先取并排对照版本。
    if not videos:
        raise ValueError(f"项目运行结束，但没有生成视频：{work}\n请查看上方日志，例如是否检测到人脸。")
    if talking:
        preferred = [p for p in videos if p.parent == work]
    else:
        preferred = [p for p in videos if p.stem.endswith("_concat")]
    source = (preferred or videos)[-1]
    label_video(source, target, args.font, args.force)
    print(f"课堂播放文件：{target}\n中间结果保存在：{work}")


def main() -> int:
    parser = argparse.ArgumentParser(description="六年级科技课：用自有或授权素材演示合成声音与人脸。")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("voice", help="F5-TTS：参考声音 + 新台词 → 合成声音")
    p.add_argument("--reference", default=str(INPUT / "teacher_reference.wav"))
    p.add_argument("--reference-text", default=str(INPUT / "teacher_reference.txt"))
    group = p.add_mutually_exclusive_group()
    group.add_argument("--text")
    group.add_argument("--text-file", default=str(INPUT / "comparison_text.txt"))
    p.add_argument("--device", choices=["auto", "mps", "cpu", "cuda"], default="auto")
    p.add_argument("--steps", type=int, choices=[16, 32], default=32)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", default=str(OUTPUT / "01_voice_ai.wav"))
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="仅显示输入参数，不下载或生成")
    p.set_defaults(handler=voice)

    for name, talking in [("talking", True), ("motion", False)]:
        p = sub.add_parser(name, help="SadTalker：照片 + 声音 → 说话视频（Mac 用 CPU）" if talking else
                               "LivePortrait：照片 + 动作视频 → 表情动画（不自动按音频对口型）")
        p.add_argument("--photo", default=str(INPUT / "teacher.jpg"))
        if talking:
            p.add_argument("--audio", default=str(OUTPUT / "00_opening_voice_ai.wav"))
            p.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
        else:
            p.add_argument("--driving", default=str(INPUT / "teacher_driving.mp4"))
        p.add_argument("--output", default=str(OUTPUT / ("02_talking_ai.mp4" if talking else "03_motion_ai.mp4")))
        p.add_argument("--python", help="对应项目的 Python；默认使用当前环境")
        p.add_argument("--font", help="合成标识使用的中文字体路径")
        p.add_argument("--force", action="store_true")
        p.add_argument("--dry-run", action="store_true")
        p.set_defaults(handler=lambda a, t=talking: portrait(a, t))

    p = sub.add_parser("audio", help="把手机/Mac 录音转换为单声道 24 kHz WAV；不裁剪台词")
    p.add_argument("source")
    p.add_argument("--output", default=str(INPUT / "teacher_reference.wav"))
    p.add_argument("--force", action="store_true")
    p.set_defaults(handler=lambda a: run([ffmpeg(), "-hide_banner", "-loglevel", "error",
        "-y" if a.force else "-n", "-i", str(require_file(a.source)), "-vn", "-ac", "1", "-ar", "24000",
        "-c:a", "pcm_s16le", str(output_path(a.output, a.force))]))

    p = sub.add_parser("label", help="给已有合成视频加入持续可见的教学标识")
    p.add_argument("source")
    p.add_argument("--output", required=True)
    p.add_argument("--font")
    p.add_argument("--force", action="store_true")
    p.set_defaults(handler=lambda a: label_video(require_file(a.source), output_path(a.output, a.force), a.font, a.force))
    args = parser.parse_args()
    try:
        args.handler(args)
    except (ValueError, ImportError, OSError, subprocess.CalledProcessError) as exc:
        print(f"\n未完成：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
