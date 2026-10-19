#!/usr/bin/env python3
"""只下载选中项目的官方模型；不会执行模型或修改第三方源码。"""
import argparse
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="课前模型下载：motion=LivePortrait 人像；talking=SadTalker 256 像素基础版")
    parser.add_argument("project", choices=["motion", "talking"])
    args = parser.parse_args()
    if args.project == "motion":
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id="KlingTeam/LivePortrait",
                          local_dir=str(ROOT / "projects/LivePortrait/pretrained_weights"),
                          allow_patterns=["liveportrait/**", "insightface/**"])
        return
    base = "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/"
    downloads = {
        "checkpoints/mapping_00109-model.pth.tar": base + "mapping_00109-model.pth.tar",
        "checkpoints/mapping_00229-model.pth.tar": base + "mapping_00229-model.pth.tar",
        "checkpoints/SadTalker_V0.0.2_256.safetensors": base + "SadTalker_V0.0.2_256.safetensors",
        "gfpgan/weights/alignment_WFLW_4HG.pth": "https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth",
        "gfpgan/weights/detection_Resnet50_Final.pth": "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth",
    }
    for relative, url in downloads.items():
        target = ROOT / "projects/SadTalker" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size:
            print("已有，跳过：", target.name)
            continue
        partial = target.with_name(target.name + ".part")
        print("下载：", target.name, flush=True)
        # 失败的下载只留下 .part，下一次不会误认为是完整权重。
        urllib.request.urlretrieve(url, partial)
        partial.replace(target)
    print("基础版模型已下载。不包含 512 像素模型及 GFPGAN 增强器。")


if __name__ == "__main__":
    main()
