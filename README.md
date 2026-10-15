# ComfyUI-MiniMaxH3-VoiceShaper

A custom node suite for **ComfyUI** designed for **MiniMax H3** audio-video generation workflows. Dial in a character's vocal pitch, timbre warmth, gravelly rasp, breathiness, speech rate, projection, and studio/room acoustics using intuitive **sliders and toggles**—and **immediately preview how the voice sounds** on a test sentence in ~1 second before running a full video generation.

---

## Features

* **Intuitive Sliders & Toggles:** Shape pitch, timbre warmth, vocal rasp/grit, breathiness, syllable pacing, projection volume, emotional intensity, vocal fry, nasal resonance, and microphone clarity.
* **Hover Tooltips Everywhere:** Hover over any slider, toggle, dropdown, or input/output pin in ComfyUI to see exactly how it affects the voice and MiniMax H3 syntax.
* **MiniMax H3 Spec Compliant:** Automatically compiles stable speaker IDs (`(S1)`, `(S2)`), language-tagged verbatim dialogue blocks (`<d>[Language] ...</d>`), off-screen voiceover lip locks, listener mouth-bleed locks, and cross-cut audio continuity rules.
* **1-Second Audio Preview Node:** Companion `MiniMax H3 Voice Test & Audio Preview` node synthesizes your test sentence and runs a real-time **PyTorch FFT & Time-Domain DSP chain** so you can hear your sliders and toggles immediately via ComfyUI's `PreviewAudio` node.
* **Direct Ref2VA `<audio_1>` Locking:** Route the `preview_audio` output directly into your MiniMax H3 reference audio input to lock both your prompt description and actual audio waveform.

---

## Example Workflows

Ready-to-use workflows are included in the [`example_workflows/`](./example_workflows) directory (and automatically appear inside ComfyUI under **Workflows -> Browse Templates**):

1. **[`01_Instant_Voice_Shaper_and_Preview.json`](./example_workflows/01_Instant_Voice_Shaper_and_Preview.json)**: Instant 1-second voice design and audio preview loop using `MiniMax H3 Voice Tone & Quality Shaper` -> `MiniMax H3 Voice Test & Audio Preview` -> `PreviewAudio`.
2. **[`02_Two_Speaker_Dialogue_Scene.json`](./example_workflows/02_Two_Speaker_Dialogue_Scene.json)**: Dual-speaker (`S1` and `S2`) conversation setup demonstrating contrasting vocal profiles and listener lip-locking for MiniMax H3.

---

## Installation

### Method 1: ComfyUI-Manager (Install via Git URL)
1. Open **ComfyUI-Manager** and click **Install via Git URL**.
2. Paste:
```text
https://github.com/exodius-b/ComfyUI-MiniMaxH3-VoiceShaper.git
```
3. Restart ComfyUI.

### Method 2: Manual Git Clone
Navigate to your `ComfyUI/custom_nodes/` folder and run:

```bash
git clone https://github.com/exodius-b/ComfyUI-MiniMaxH3-VoiceShaper.git
```

Install the dependencies into your ComfyUI Python environment:

* **Windows Portable ComfyUI:**
```cmd
..\..\python_embeded\python.exe -m pip install -r ComfyUI-MiniMaxH3-VoiceShaper\requirements.txt
```

* **Standard Venv / Conda:**
```bash
pip install -r ComfyUI-MiniMaxH3-VoiceShaper/requirements.txt
```

Restart ComfyUI and refresh your browser.

---

## Nodes Included

### 1. `MiniMax H3 Voice Tone & Quality Shaper`
Located under **Add Node -> MiniMax H3 -> Audio & Voice**.

| Control | Type | Range / Options | Effect |
| :--- | :--- | :--- | :--- |
| `speaker_id` | Dropdown | `S1`, `S2`, `S3`, `S4`, `S1,S2` | Persistent speaker ID across shots. |
| `subject_reference` | String | Free text | On-screen subject label (e.g., `The detective`, `<subj_1>`). |
| `vocal_archetype` | Dropdown | `auto`, `young woman`, `middle-aged man`, etc. | Base age/gender vocal profile. |
| `language` & `accent` | Dropdown | 11 Languages / 15 Accents | Sets `<d>[Language] ...</d>` tag and regional accent. |
| `emotional_tone` | Dropdown | 10 Emotional Profiles | Primary emotional inflection of the delivery. |
| `pitch` | Slider | `-1.0` to `1.0` | `-1.0` Deep bass/baritone to `+1.0` High soprano/bright register. |
| `timbre_warmth` | Slider | `-1.0` to `1.0` | `-1.0` Cold/sharp/clinical to `+1.0` Rich, warm, velvety timbre. |
| `texture_rasp` | Slider | `0.0` to `1.0` | `0.0` Smooth/pure to `0.5` Husky to `1.0` Heavy gravelly grit. |
| `breathiness` | Slider | `0.0` to `1.0` | `0.0` Full-chested to `1.0` Heavily breathy, near-whispered air. |
| `speech_rate` | Slider | `-1.0` to `1.0` | `-1.0` Slow, deliberate cadence to `+1.0` Rapid-fire clip. |
| `projection_volume` | Slider | `-1.0` to `1.0` | Shifts loudness and verb (`murmurs`, `says softly`, `says`, `says firmly`, `shouts`). |
| `emotional_intensity` | Slider | `0.0` to `1.0` | Scales emotional delivery from subtle (`0.0`) to dramatic (`1.0`). |
| `acoustic_clarity` | Slider | `0.0` to `1.0` | `0.0` Lo-fi telephone/radio filter to `1.0` Crisp close-mic studio clarity. |
| `offscreen_voiceover` | Toggle | On / Off | Formats as H3 off-screen voiceover and locks speaker lips closed. |
| `lock_other_lips` | Toggle | On / Off | Prevents other visible characters from moving their mouths. |
| `studio_dry_isolation` | Toggle | On / Off | Toggles between dry studio isolation and natural room reverb. |
| `vocal_fry` | Toggle | On / Off | Adds creaky low-frequency vocal fry on phrase tails. |
| `nasal_resonance` | Toggle | On / Off | Adds a 1.1 kHz nasal formant emphasis. |
| `singing_mode` | Toggle | On / Off | Switches delivery verb from spoken dialogue to melodic singing. |
| `cross_cut_continuity` | Toggle | On / Off | Appends H3 cross-cut audio continuity instruction. |

### 2. `MiniMax H3 Voice Test & Audio Preview`
Connect `voice_params` from the Shaper node into `voice_params` on the Preview node, and connect `preview_audio` to ComfyUI's built-in `PreviewAudio` node to immediately audition your voice settings.

---

## License
MIT License
