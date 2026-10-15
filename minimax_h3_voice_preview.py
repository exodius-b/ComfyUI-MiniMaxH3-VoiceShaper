# Companion Audio Previewer Node for MiniMaxH3VoiceShaper
import asyncio
import io
import math
import os
import tempfile
import threading
import av
import numpy as np
import requests
import torch
import torch.nn.functional as F


class MiniMaxH3VoicePreviewer:
    DESCRIPTION = (
        "Synthesizes an immediate ~1-second audio preview of your Voice Shaper settings "
        "using Neural TTS + real-time PyTorch FFT acoustic DSP. Connect 'preview_audio' "
        "to ComfyUI's PreviewAudio node or directly into a MiniMax H3 <audio_1> reference input."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "voice_params": (
                    "H3_VOICE_PARAMS",
                    {
                        "tooltip": "Connect the voice_params output from the MiniMax H3 Voice Tone & Quality Shaper node."
                    },
                ),
                "preview_engine": (
                    [
                        "Local Instant (Edge-TTS + PyTorch Acoustic DSP)",
                        "MiniMax T2A v2 API + PyTorch Acoustic DSP",
                    ],
                    {
                        "default": "Local Instant (Edge-TTS + PyTorch Acoustic DSP)",
                        "tooltip": "Choose 'Local Instant' for ~1-second free neural synthesis + PyTorch DSP, or 'MiniMax T2A v2 API' to preview with official MiniMax Speech-02 HD voices.",
                    },
                ),
                "override_sample_text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Optional test sentence. Leave empty to speak the dialogue_text from the Voice Shaper node, or type a custom test sentence here.",
                    },
                ),
                "apply_acoustic_dsp": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label_on": "DSP Shaping Active",
                        "label_off": "Raw TTS Output Only",
                        "tooltip": "ON = Applies real-time PyTorch FFT EQ warmth, harmonic rasp, breathiness air, nasal formants, vocal fry, and studio/room acoustics. OFF = Raw TTS output.",
                    },
                ),
            },
            "optional": {
                "minimax_api_key": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "tooltip": "Optional MiniMax API key (only required if preview_engine is set to 'MiniMax T2A v2 API' and MINIMAX_API_KEY is not set in your environment).",
                    },
                ),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("preview_audio",)
    OUTPUT_TOOLTIPS = (
        "Standard ComfyUI AUDIO output. Connect to PreviewAudio to listen immediately, or route into a MiniMax H3 <audio_1> reference input for Ref2VA voice locking.",
    )
    FUNCTION = "generate_preview"
    CATEGORY = "MiniMax H3/Audio & Voice"

    EDGE_VOICE_MAP = {
        ("English", "Received Pronunciation (British)", "female"): "en-GB-SoniaNeural",
        ("English", "Received Pronunciation (British)", "male"): "en-GB-RyanNeural",
        ("English", "Cockney British", "male"): "en-GB-ThomasNeural",
        ("English", "Australian", "female"): "en-AU-NatashaNeural",
        ("English", "Australian", "male"): "en-AU-WilliamNeural",
        ("English", "Irish", "female"): "en-IE-EmilyNeural",
        ("English", "Irish", "male"): "en-IE-ConnorNeural",
        ("English", "default", "female"): "en-US-AriaNeural",
        ("English", "default", "male"): "en-US-ChristopherNeural",
        ("English", "default", "child"): "en-US-AnaNeural",
        ("Chinese", "default", "female"): "zh-CN-XiaoxiaoNeural",
        ("Chinese", "default", "male"): "zh-CN-YunxiNeural",
        ("Japanese", "default", "female"): "ja-JP-NanamiNeural",
        ("Japanese", "default", "male"): "ja-JP-KeitaNeural",
        ("Korean", "default", "female"): "ko-KR-SunHiNeural",
        ("Korean", "default", "male"): "ko-KR-InJoonNeural",
        ("Spanish", "default", "female"): "es-ES-ElviraNeural",
        ("Spanish", "default", "male"): "es-ES-AlvaroNeural",
        ("French", "default", "female"): "fr-FR-DeniseNeural",
        ("French", "default", "male"): "fr-FR-HenriNeural",
        ("German", "default", "female"): "de-DE-KatjaNeural",
        ("German", "default", "male"): "de-DE-ConradNeural",
        ("Italian", "default", "female"): "it-IT-ElsaNeural",
        ("Italian", "default", "male"): "it-IT-DiegoNeural",
        ("Portuguese", "default", "female"): "pt-BR-FranciscaNeural",
        ("Portuguese", "default", "male"): "pt-BR-AntonioNeural",
        ("Russian", "default", "female"): "ru-RU-SvetlanaNeural",
        ("Russian", "default", "male"): "ru-RU-DmitryNeural",
        ("Arabic", "default", "female"): "ar-SA-ZariyahNeural",
        ("Arabic", "default", "male"): "ar-SA-HamedNeural",
    }

    @classmethod
    def _infer_gender_group(cls, params: dict) -> str:
        arch = params.get("vocal_archetype", "").lower()
        subj = params.get("subject_reference", "").lower()
        combined = f"{arch} {subj}"
        if "child" in combined or "kid" in combined or "girl" in combined or "boy" in combined:
            return "child"
        if any(w in combined for w in ["woman", "female", "she", "her", "lady", "mother", "sister"]):
            return "female"
        if any(w in combined for w in ["man", "male", "he", "him", "guy", "father", "brother", "detective"]):
            return "male"
        return "female"

    @classmethod
    def _select_edge_voice(cls, params: dict) -> str:
        lang = params.get("language", "English")
        accent = params.get("accent", "Neutral / Unspecified")
        group = cls._infer_gender_group(params)

        if (lang, accent, group) in cls.EDGE_VOICE_MAP:
            return cls.EDGE_VOICE_MAP[(lang, accent, group)]
        if (lang, "default", group) in cls.EDGE_VOICE_MAP:
            return cls.EDGE_VOICE_MAP[(lang, "default", group)]
        return cls.EDGE_VOICE_MAP.get((lang, "default", "female"), "en-US-AriaNeural")

    @staticmethod
    def _decode_audio_pyav(source) -> tuple[torch.Tensor, int]:
        with av.open(source) as container:
            audio_stream = next(s for s in container.streams if s.type == "audio")
            sr = int(audio_stream.rate or audio_stream.codec_context.sample_rate or 24000)
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=sr)
            chunks = []
            for frame in container.decode(audio=0):
                for out_frame in resampler.resample(frame):
                    chunks.append(out_frame.to_ndarray())
            for out_frame in resampler.resample(None):
                chunks.append(out_frame.to_ndarray())

        if not chunks:
            return torch.zeros((1, sr), dtype=torch.float32), sr

        arr = np.concatenate(chunks, axis=-1)
        waveform = torch.from_numpy(arr).float()
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        return waveform, sr

    @staticmethod
    def _run_edge_tts_sync(text: str, voice: str, rate_str: str, pitch_str: str, vol_str: str) -> str:
        import edge_tts

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp_file.name
        tmp_file.close()

        async def _task():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate_str,
                pitch=pitch_str,
                volume=vol_str,
            )
            await communicate.save(tmp_path)

        result_exc = []

        def _thread_target():
            try:
                asyncio.run(_task())
            except Exception as e:
                result_exc.append(e)

        t = threading.Thread(target=_thread_target)
        t.start()
        t.join()

        if result_exc:
            raise RuntimeError(f"Edge-TTS synthesis failed: {result_exc[0]}")
        return tmp_path

    @classmethod
    def _synthesize_minimax_api(cls, text: str, params: dict, api_key: str) -> tuple[torch.Tensor, int]:
        key = api_key.strip() or os.environ.get("MINIMAX_API_KEY", "").strip()
        if not key:
            raise ValueError(
                "MiniMax API Key is missing. Provide it in the node or switch preview_engine to 'Local Instant'."
            )

        group = cls._infer_gender_group(params)
        voice_id = "Wise_Woman" if group == "female" else "Deep_Voice_Man"
        if group == "child":
            voice_id = "Cute_Boy"

        speed = round(1.0 + (params.get("speech_rate", 0.0) * 0.45), 2)
        pitch = int(round(params.get("pitch", 0.0) * 10))
        vol = round(max(0.2, 1.0 + (params.get("projection_volume", 0.0) * 0.8)), 2)

        emotion_map = {
            "Neutral": "neutral",
            "Warm": "happy",
            "Playful": "happy",
            "Urgent": "fearful",
            "Somber": "sad",
            "Angry": "angry",
            "Sarcastic": "disgusted",
            "Fearful": "fearful",
            "Authoritative": "neutral",
            "Joyful": "happy",
        }
        raw_tone = params.get("emotional_tone", "Neutral").split("/")[0].strip()
        emotion = emotion_map.get(raw_tone, "neutral")

        endpoint_host = "api.minimax.io"
        url = f"https://{endpoint_host}/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "speech-02-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
                "emotion": emotion,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "wav",
                "channel": 1,
            },
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        audio_hex = data.get("data", {}).get("audio")
        if not audio_hex:
            raise RuntimeError(f"MiniMax T2A v2 error: {data}")

        audio_bytes = bytes.fromhex(audio_hex)
        return cls._decode_audio_pyav(io.BytesIO(audio_bytes))

    @staticmethod
    def _apply_dsp_chain(waveform: torch.Tensor, sr: int, params: dict) -> torch.Tensor:
        x = waveform.clone().float()
        if x.dim() == 1:
            x = x.unsqueeze(0)

        n_samples = x.shape[-1]
        freqs = torch.fft.rfftfreq(n_samples, d=1.0 / sr, device=x.device)
        eq_db = torch.zeros_like(freqs)

        warmth = float(params.get("timbre_warmth", 0.0))
        if abs(warmth) > 0.05:
            low_shelf = 1.0 / (1.0 + (freqs / 230.0) ** 2)
            high_shelf = 1.0 / (1.0 + (3600.0 / (freqs + 1e-5)) ** 2)
            eq_db = eq_db + (warmth * 7.5 * low_shelf) - (warmth * 5.5 * high_shelf)

        if params.get("nasal_resonance", False):
            nasal_bell = torch.exp(-0.5 * ((freqs - 1100.0) / 220.0) ** 2)
            sub_cut = 1.0 / (1.0 + (freqs / 180.0) ** 2)
            eq_db = eq_db + (8.5 * nasal_bell) - (4.5 * sub_cut)

        clarity = float(params.get("acoustic_clarity", 0.8))
        if clarity < 0.35:
            hp_mask = 1.0 / (1.0 + (360.0 / (freqs + 1e-5)) ** 4)
            lp_mask = 1.0 / (1.0 + (freqs / 3100.0) ** 4)
            band_gain = (hp_mask * lp_mask).clamp(min=1e-3)
            eq_db = eq_db + 20.0 * torch.log10(band_gain)
        elif clarity > 0.7:
            air_shelf = 1.0 / (1.0 + (6200.0 / (freqs + 1e-5)) ** 2)
            eq_db = eq_db + ((clarity - 0.7) * 12.0 * air_shelf)

        gain_linear = 10.0 ** (eq_db / 20.0)
        X = torch.fft.rfft(x, dim=-1)
        x = torch.fft.irfft(X * gain_linear.unsqueeze(0), n=n_samples, dim=-1)

        if clarity < 0.35:
            x = torch.tanh(x * 1.6) * 0.85

        win = max(1, int(sr * 0.015))
        env = F.avg_pool1d(x.abs().unsqueeze(0), kernel_size=win, stride=1, padding=win // 2).squeeze(0)
        env = env[:, :n_samples]

        rasp = float(params.get("texture_rasp", 0.0))
        if rasp > 0.05:
            t = torch.arange(n_samples, device=x.device, dtype=torch.float32) / sr
            flutter = (
                0.6 * torch.sin(2.0 * math.pi * 78.0 * t)
                + 0.4 * torch.sin(2.0 * math.pi * 119.0 * t)
            )
            rough_mod = 1.0 + (rasp * 0.42 * flutter.unsqueeze(0) * (env / (env.max() + 1e-6)))
            drive = 1.0 + rasp * 2.8
            x = torch.tanh(x * rough_mod * drive) / math.tanh(drive)

        breath = float(params.get("breathiness", 0.0))
        if breath > 0.05:
            noise = torch.randn_like(x)
            N_fft = torch.fft.rfft(noise, dim=-1)
            air_band = (1.0 / (1.0 + (2200.0 / (freqs + 1e-5)) ** 4)) * (1.0 / (1.0 + (freqs / 7500.0) ** 4))
            air = torch.fft.irfft(N_fft * air_band.unsqueeze(0), n=n_samples, dim=-1)
            voiced_weight = 1.0 - (breath * 0.35)
            x = (x * voiced_weight) + (air * env * breath * 0.65)

        if params.get("vocal_fry", False):
            t = torch.arange(n_samples, device=x.device, dtype=torch.float32) / sr
            fry_pulses = (torch.sin(2.0 * math.pi * 42.0 * t) > 0.35).float()
            norm_env = env / (env.max() + 1e-6)
            tail_mask = ((norm_env > 0.04) & (norm_env < 0.38)).float()
            x = x * (1.0 - 0.55 * tail_mask + 0.55 * tail_mask * fry_pulses.unsqueeze(0))

        if not params.get("studio_dry_isolation", True):
            ir_len = int(sr * 0.28)
            t_ir = torch.linspace(0.0, 0.28, ir_len, device=x.device)
            gen = torch.Generator(device=x.device)
            gen.manual_seed(42)
            ir = torch.randn((1, ir_len), generator=gen, device=x.device) * torch.exp(-t_ir * 16.0)
            ir[0, 0] = 1.0
            ir = ir / ir.norm()
            fft_size = n_samples + ir_len - 1
            wet = torch.fft.irfft(
                torch.fft.rfft(x, n=fft_size, dim=-1) * torch.fft.rfft(ir, n=fft_size, dim=-1),
                n=fft_size,
                dim=-1,
            )[:, :n_samples]
            x = 0.78 * x + 0.22 * wet

        proj = float(params.get("projection_volume", 0.0))
        target_peak = max(0.18, min(0.96, 0.65 + (proj * 0.30)))
        peak = x.abs().max()
        if peak > 1e-6:
            x = (x / peak) * target_peak

        return x.clamp(-1.0, 1.0)

    def generate_preview(
        self,
        voice_params: dict,
        preview_engine: str,
        override_sample_text: str,
        apply_acoustic_dsp: bool = True,
        minimax_api_key: str = "",
    ):
        text = override_sample_text.strip() or voice_params.get("dialogue_text", "").strip()
        if not text:
            text = "Testing voice tone, timbre, and acoustic clarity for MiniMax H3."

        if preview_engine.startswith("MiniMax T2A"):
            waveform, sr = self._synthesize_minimax_api(text, voice_params, minimax_api_key)
        else:
            voice_name = self._select_edge_voice(voice_params)
            rate_pct = int(round(float(voice_params.get("speech_rate", 0.0)) * 45))
            pitch_hz = int(round(float(voice_params.get("pitch", 0.0)) * 32))
            vol_pct = int(round(float(voice_params.get("projection_volume", 0.0)) * 35))

            rate_str = f"{rate_pct:+d}%"
            pitch_str = f"{pitch_hz:+d}Hz"
            vol_str = f"{vol_pct:+d}%"

            tmp_mp3 = self._run_edge_tts_sync(text, voice_name, rate_str, pitch_str, vol_str)
            try:
                waveform, sr = self._decode_audio_pyav(tmp_mp3)
            finally:
                if os.path.exists(tmp_mp3):
                    os.remove(tmp_mp3)

        if apply_acoustic_dsp:
            waveform = self._apply_dsp_chain(waveform, sr, voice_params)

        audio_tensor = waveform.unsqueeze(0).cpu()
        return ({"waveform": audio_tensor, "sample_rate": sr},)
