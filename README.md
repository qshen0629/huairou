# 谁在替我说话？——声音克隆、人脸合成与身份验证

适用：40 分钟，六年级，苹果芯片 Mac。以本人授权制作的数字分身开场，拆解声音与人脸如何生成，再讨论检测、身份认证和授权。当前推荐使用 `课件/重制版/` 中的课件。

**核心问题：当声音和脸都能生成，我们凭什么确认本人表达和授权？**

## 先打开什么

- `课件/重制版/谁在替我说话.pptx`：可编辑的 16:9 课件，19 页课堂内容 + 3 页教师附录；逐页讲稿在演讲者备注中。
- `课件/重制版/谁在替我说话.pdf`：同版式静态预览，不包含可播放媒体。
- `课件/重制版/讲稿与演示安排.txt`：40 分钟时间分配、问题、机制说明和串场词。
- `课件/重制版/课件总览.png`：整套课件缩略图；`重点页面.png` 展示封面、技术拆解和讨论题。
- `assets/design/设计说明.md`：视觉设计、虚构肖像来源与生成提示词。
- `projects/`：从官方仓库下载的三个项目源码，保留原始许可证。
- `scripts/demo.py`：声音生成、照片说话、表情迁移、音频转换和合成标识入口。
- `scripts/setup_mac.sh`、`scripts/download_models.py`：Mac 分环境安装与课前权重下载入口。

当前交付不含你的照片、真人录音或已生成的数字分身。肖像为明确标注的 AI 虚构人物，仅供版式与结构图解使用。真人媒体需要录制并生成后加入；当前环境未完成你的 Mac 推理实测。

## 40 分钟怎么上

| 时间 | 页面 | 内容 | 学生活动 |
| --- | --- | --- | --- |
| 0–4 分钟 | 1–2 | 数字分身开场，观察真实技术效果 | 区分看到的外观、听到的声音与表达内容 |
| 4–12 分钟 | 3–6 | 声音对照、参考样本与新台词、训练与推理 | 解释模型怎样生成没录过的句子 |
| 12–21 分钟 | 7–10 | 音频驱动运动、逐帧生成、三类人脸技术、项目制作链 | 理解外观与运动可以怎样重组 |
| 21–28 分钟 | 11–13 | 实时交互系统、真实深伪会议案例、动作检查的边界 | 讨论交互能力能提供哪一部分证据 |
| 28–35 分钟 | 14–16 | 制作方式、本人授权、内容事实；检测器与信任链 | 说明检测结果与身份认证分别回答什么 |
| 35–40 分钟 | 17–19 | 使用边界与开放问题，收束全课 | 讨论授权分身是否能真实代表本人表达 |

讲授方式：先展示，再拆机制，再讨论证据。解释“音色线索、运动参数、推理、认证”等术语时，给出可观察的输入输出；技术名词可保留，长解释放在备注中。

结尾讨论：“我授权数字分身读出我认可的讲稿，你会把它叫作‘假的’吗？”从制作方式、本人授权、内容事实三个角度分别回答。

## 开源项目选择与取舍

核对日期：2026-10-14。下面的“适合”是结合课堂与设备条件的判断；不是当前 Mac 的速度实测。

| 项目 | 输入 → 输出 | Mac 情况与课堂位置 | 代码 / 模型说明 |
| --- | --- | --- | --- |
| **[F5-TTS](https://github.com/SWivid/F5-TTS)**，已下载 | 一小段参考声音 + 逐字稿 + 新台词 → 相似音色的新语音 | 官方列有 Apple Silicon 安装路径，代码支持 MPS。作为声音主线；是否现场生成，先在你的机器上完成一次实际演练再决定 | 代码 MIT；官方预训练模型为 CC-BY-NC-4.0，见[模型卡](https://huggingface.co/SWivid/F5-TTS)。收费培训、商业宣传等用途不能仅凭代码 MIT 推断可用 |
| **[SadTalker](https://github.com/OpenTalker/SadTalker)**，已下载 | 一张肖像 + 音频 → 开口说话视频 | 官方提供 M1 安装记录；当前 `inference.py` 只选择 CUDA 或 CPU，Mac 使用 CPU。与 F5-TTS 串联，课前生成约 5–10 秒片段 | 主项目 Apache-2.0；依赖与附带组件各自的条款仍需保留。默认不启用额外的画质增强器 |
| **[LivePortrait](https://github.com/KlingAIResearch/LivePortrait)**，已下载 | 肖像 + 驱动动作视频 → 肖像表情/姿态动画 | 官方支持苹果芯片人像模式，并提示可能明显慢于高端 NVIDIA GPU。适合“我点头，照片也点头”的第二展示 | 代码 MIT；包含的 InsightFace 检测模型限非商业研究，见[原始许可证](https://github.com/KlingAIResearch/LivePortrait/blob/main/LICENSE)。普通课堂的具体用途也不能直接视作已获模型授权 |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)，仅列备选 | 参考语音 + 台词 → 克隆语音 | 中文操作资料多，官方有 Mac MPS/CPU 安装路径；F5-TTS 的声音效果不满意时可换用 | 以原仓库及所选权重条款为准，不把它的依赖再混装进 F5 环境 |
| [MuseTalk](https://github.com/TMElyralab/MuseTalk)，仅列备选 | 人脸视频 + 音频 → 修改嘴部的同步视频 | 官方主教程围绕 CUDA，不能把 V100 的实时结果套到 Mac；本课不选它作 Mac 主线 | 代码 MIT；其模型与其他组件的条款分别列在原仓库 |
| [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)，仅列对照 | 人脸视频 + 音频 → 对口型视频 | 经典方案，但环境较旧，本次不优先 | 原仓库强调非商业用途限制；不要把“能下载”理解成任意使用 |

**能力边界：**LivePortrait 不会根据一段新声音自动生成对应口型，单纯把 F5-TTS 的声音贴到它的视频上，不能保证对口型。本课的音画组合路线是 **F5-TTS → SadTalker**。这些项目展示的是声音合成与人像动画，不等于已经演示了“把某人的脸替换进另一个人的整段视频”，也不代表所有生成模型的最高水平。

主展示优先完成 F5-TTS + SadTalker 短片。LivePortrait 在新版中作为技术对照与可选扩展，不需要为课堂另外制作一整段动作迁移演示。

## 素材只需要你自己录

放在 `assets/input/`：

1. `teacher_reference.wav`：8–10 秒单人自然语音，没有音乐，总时长少于 12 秒，末尾留约 1 秒停顿。参考台词已放在 `teacher_reference.txt`；实际说了什么，就把逐字稿改成什么。
2. `teacher.jpg`：单人正面照，嘴自然闭合、光线均匀，建议 512 像素以上。
3. `teacher_real.wav`：你本人读 `comparison_text.txt` 的原声。A/B 对比的原声和合成声读相同台词，音量接近；参考录音与这段测试原声分开。
4. 可选 `teacher_driving.mp4`：5–8 秒点头、微笑、眨眼，首帧正面自然表情。用于 LivePortrait 动作迁移，不要求它与合成音频对口型。

演示使用本人或明确授权成人的素材。A/B 台词在 `comparison_text.txt`，你本人读一遍，再由模型生成一遍。开场台词在 `demo_text.txt`：“你现在看到的是我的数字分身。这段话没有被我录下来，而是由人工智能生成的。”这段开场台词只由模型生成，不要求你录制，确保“没录过的新句子”与 A/B 对照是两组不同材料。

## 在苹果芯片 Mac 上生成

下面命令在**把整个目录复制到 Mac 后**、该目录下运行；不会自动安装到这台 Linux 工作环境。路径含中文与空格时也请保留引号。需要原生 arm64 的 [Miniforge](https://github.com/conda-forge/miniforge)，不要在 Rosetta 的 x86 终端中安装。

安装脚本会分别创建三个环境。只想完成主线，安装 `voice` 与 `talking` 就够了。脚本按官方环境与已读源码整理，**尚未在你的 Mac 上实测**；不能据此承诺一键安装或具体生成时长。三个环境合计依赖与模型会占用数 GB 以上空间。

### 1. 声音主线

```bash
bash scripts/setup_mac.sh voice

# 把两段录音保存为 teacher_reference.m4a 和 teacher_real.m4a，再转换成 WAV：
./.envs/f5-tts/bin/python scripts/demo.py audio assets/input/teacher_reference.m4a
./.envs/f5-tts/bin/python scripts/demo.py audio assets/input/teacher_real.m4a --output assets/input/teacher_real.wav

# 参考录音逐字稿不要留空。默认先生成 comparison_text.txt 对应的 A/B 合成声。
./.envs/f5-tts/bin/python scripts/demo.py voice --device mps

# 再生成开场视频所用的新台词。这段话不用你本人录。
./.envs/f5-tts/bin/python scripts/demo.py voice --device mps \
  --text-file assets/input/demo_text.txt \
  --output assets/output/00_opening_voice_ai.wav
```

输出两份合成声音：`assets/output/01_voice_ai.wav` 用于与本人原声做 A/B 对比，`assets/output/00_opening_voice_ai.wav` 用于开场视频。各自旁边保存说明它是合成声音的 JSON。首次推理会下载 F5-TTS / Vocos 权重；必须在课前联网完成。课堂可修改一句新台词：

```bash
./.envs/f5-tts/bin/python scripts/demo.py voice --device mps \
  --text '这句话没有被我录下来，而是由人工智能生成的。' \
  --output assets/output/voice_live_ai.wav
```

如果 MPS 报算子或设备错误，用同一入口加 `--device cpu`。CPU 会更慢，课堂直接播放课前文件。默认 32 步；`--steps 16` 可缩短计算，但会改变声音效果，不能保证更快就同样好。现场优先保持预先选好的设置。

喜欢界面操作，可以在相同环境运行官方界面；它默认可能同时初始化语音识别组件，首次也要课前完成：

```bash
./.envs/f5-tts/bin/f5-tts_infer-gradio --host 127.0.0.1 --port 7860
```

### 2. 声音 + 肖像 → 说话视频

```bash
bash scripts/setup_mac.sh talking
./.envs/sadtalker/bin/python scripts/download_models.py talking
./.envs/sadtalker/bin/python scripts/demo.py talking --device cpu --audio assets/output/00_opening_voice_ai.wav
```

输出：`assets/output/02_talking_ai.mp4`，持续带有“AI 合成 · 教学演示”画面标识。基础版使用 256 像素渲染、batch size 1，不启用 GFPGAN 额外增强。Mac 上将它视作课前制作任务，先用一段实际要上课播放的短音频完成成片，不在课上等待。

SadTalker 的依赖较旧，因此分开安装 Python 3.10、PyTorch 2.0.1 / torchvision 0.15.2 / torchaudio 2.0.2，并保留 numpy 1.23.4 和 Pillow 9.5.0；这是为避免已读源码中的旧 `functional_tensor` 与 `Image.ANTIALIAS` 接口冲突。原作者的 [Mac 安装记录](https://github.com/OpenTalker/SadTalker/blob/main/docs/install.md) 使用 Python 3.8；这里给的是便于依赖安装的适配方案，不冒充原作者已验证的完整组合。不要把这个环境的依赖升级后覆盖 F5 环境。

### 3. 可选：照片跟着点头、眨眼

```bash
bash scripts/setup_mac.sh motion
./.envs/liveportrait/bin/python scripts/download_models.py motion
PYTORCH_ENABLE_MPS_FALLBACK=1 ./.envs/liveportrait/bin/python scripts/demo.py motion
```

输出：`assets/output/03_motion_ai.mp4`，优先选取含输入与生成结果的并排对照视频，并加入合成标识。这里只下载人像模式的权重，不下载动物模式；官方动物模式没有 Mac 支持。

### 4. 已有成片可以单独加标识

```bash
./.envs/f5-tts/bin/python scripts/demo.py label 你的合成视频.mp4 \
  --output assets/output/你的合成视频_教学标识.mp4
```

输出默认不覆盖旧文件；需要重做时换输出名，或明确加 `--force`。原始中间视频保存在 `assets/output/raw/`，课堂使用已加标识的输出。标识用于诚实表达演示用途，并不能证明其他未标识的视频一定真实。

## 把素材放进 PPT

1. 第 2 页播放 `02_talking_ai.mp4`。文件位于 `assets/output/` 时，运行新版生成器会自动嵌入。也可以在 PowerPoint 中手动“插入 → 视频 → 文件中的影片”。
2. 第 4 页在 A 区插入 `teacher_real.wav`，B 区插入 `01_voice_ai.wav`。二者均为 `comparison_text.txt`，设为单击播放。备注中的顺序固定为 **A 原声、B 合成**，在本页口头揭晓。开场视频使用另一份 `00_opening_voice_ai.wav`，与 A/B 台词分开。
3. `teacher.jpg` 存在时，重新生成会自动将多页示意肖像替换为本人照片。面部结构线始终标为结构示意，不是实际检测输出。
4. 保存手动插好音频的副本；重新运行生成器会覆盖 `课件/重制版/` 内的默认 PPT/PDF。音频目前不自动嵌入。

推荐文件名：`谁在替我说话_已插入素材.pptx`。用最终演示的 Mac、投影仪和音响完整演练；将 PPT 与所有本地成片一并携带。

## 演示临场怎么办

- 现场声音生成等候超过约 20 秒，就说“电脑还在计算，我们先看课前生成的版本”，然后播放预生成结果。这是课堂等待上限，不是模型速度承诺。
- 视频只播放预生成版本。联网不稳时不要打开在线 Demo；模型缓存是否完整也不会影响本地文件播放。
- 合成效果明显不自然，仍可用于讲解输入输出，但应如实说“这是这套开源模型在这份素材上的效果”，不要声称所有 AI 都能一眼识破。
- A/B 被学生轻松猜中，就追问：“你发现的是这次生成的线索。如果下一次更自然，你还会怎样确认？”
- 讨论动作检查和检测器时，说明它们能增加哪种证据；身份与重要授权仍应通过独立可信渠道和相应流程核实。

## 重新生成课件

仅制作课件需要的依赖与模型环境无关：

```bash
python3 -m pip install python-pptx Pillow reportlab pymupdf numpy
python3 scripts/build_slides_v2.py
```

PPT 使用 Mac 系统 PingFang / Menlo；PDF 使用附带的 Noto Sans SC / JetBrains Mono，各自 OFL 保存在字体目录。文字、流程与图解为可编辑对象。总览与重点页面从实际生成的 PDF 渲染；当前环境没有运行 Mac PowerPoint 渲染。

## 已完成与尚缺内容

已完成：课堂结构、可编辑课件、讲稿、项目源码、Mac 分环境安装入口、模型下载入口、生成与标识脚本。已核对项目接口与能力边界，并验证课件结构与媒体标识处理。

尚缺：你本人录音、照片、可选动作视频，模型权重下载、你的 Mac 实际推理和 PPT 媒体插入。没有这些素材，当前无法产出真实的声音克隆或人脸合成视频。
