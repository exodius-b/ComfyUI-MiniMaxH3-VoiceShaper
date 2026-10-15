# ComfyUI Custom Node for MiniMax H3 Voice Shaping

class MiniMaxH3VoiceShaper:
    DESCRIPTION = (
        "Shapes vocal pitch, timbre warmth, gravelly rasp, breathiness, pacing, projection, "
        "and studio/room acoustics for MiniMax H3 dialogue prompts. Connect 'voice_params' "
        "to the companion Preview node to immediately hear your voice settings."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "speaker_id": (
                    ["S1", "S2", "S3", "S4", "S1,S2"],
                    {
                        "default": "S1",
                        "tooltip": "Assigns a persistent speaker tag (S1, S2, etc.) so MiniMax H3 preserves the same voice identity across shots.",
                    },
                ),
                "subject_reference": (
                    "STRING",
                    {
                        "default": "The speaker",
                        "multiline": False,
                        "tooltip": "Who is speaking in the shot (e.g., 'The detective', 'The young woman', or a reference tag like '<subj_1>').",
                    },
                ),
                "vocal_archetype": (
                    [
                        "auto (use subject_reference)",
                        "young woman",
                        "middle-aged woman",
                        "elderly woman",
                        "young man",
                        "middle-aged man",
                        "elderly man",
                        "child",
                        "androgynous speaker",
                    ],
                    {
                        "default": "auto (use subject_reference)",
                        "tooltip": "Selects the base age and gender vocal archetype. Choose 'auto' to infer from subject_reference, or pick an explicit archetype.",
                    },
                ),
                "language": (
                    [
                        "English",
                        "Chinese",
                        "Japanese",
                        "Korean",
                        "Spanish",
                        "French",
                        "German",
                        "Italian",
                        "Portuguese",
                        "Russian",
                        "Arabic",
                    ],
                    {
                        "default": "English",
                        "tooltip": "Sets the language tag inside <d>[Language] ...</d> and selects the matching neural language voice in the audio previewer.",
                    },
                ),
                "accent": (
                    [
                        "Neutral / Unspecified",
                        "General American",
                        "Received Pronunciation (British)",
                        "Cockney British",
                        "Scottish",
                        "Irish",
                        "Australian",
                        "Southern American",
                        "New York",
                        "French-accented",
                        "German-accented",
                        "Spanish-accented",
                        "Japanese-accented",
                        "Mandarin-accented",
                        "Russian-accented",
                    ],
                    {
                        "default": "Neutral / Unspecified",
                        "tooltip": "Applies a regional or national accent descriptor to the voice prompt and matches supported accents in the previewer.",
                    },
                ),
                "emotional_tone": (
                    [
                        "Neutral / Composed",
                        "Warm / Friendly",
                        "Playful / Confident",
                        "Urgent / Tense",
                        "Somber / Melancholic",
                        "Angry / Confrontational",
                        "Sarcastic / Dry",
                        "Fearful / Trembling",
                        "Authoritative / Commanding",
                        "Joyful / Excited",
                    ],
                    {
                        "default": "Neutral / Composed",
                        "tooltip": "Sets the primary emotional inflection of the vocal delivery (scale its strength using emotional_intensity).",
                    },
                ),
                "pitch": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Controls fundamental vocal pitch. -1.0 = Deep resonant bass/baritone | 0.0 = Natural mid-range | +1.0 = Bright high-register/soprano.",
                    },
                ),
                "timbre_warmth": (
                    "FLOAT",
                    {
                        "default": 0.2,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Shapes vocal tone color. -1.0 = Cold, sharp, clinical | 0.0 = Balanced neutral | +1.0 = Rich, rounded, velvety warmth.",
                    },
                ),
                "texture_rasp": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Adds vocal cord grit and roughness. 0.0 = Pure, smooth vocal cords | 0.5 = Slightly husky | 1.0 = Heavy gravelly, weathered rasp.",
                    },
                ),
                "breathiness": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Adjusts airflow and intimacy. 0.0 = Solid, full-chested tone | 0.5 = Softly airy | 1.0 = Heavily breathy, near-whispered delivery.",
                    },
                ),
                "speech_rate": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Controls syllable pacing. -1.0 = Very slow, deliberate cadence | 0.0 = Natural conversational pace | +1.0 = Rapid, fast-paced clip.",
                    },
                ),
                "projection_volume": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Sets vocal loudness and H3 delivery verb. -1.0 = Hushed murmur | -0.5 = Soft delivery | 0.0 = Conversational | +0.5 = Firm projection | +1.0 = Booming shout.",
                    },
                ),
                "emotional_intensity": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Scales how strongly the selected emotional_tone is performed. 0.0 = Subtle and restrained | 0.5 = Clear delivery | 1.0 = Intense, deeply expressive.",
                    },
                ),
                "acoustic_clarity": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                        "tooltip": "Tunes microphone fidelity. 0.0 = Lo-fi, band-limited vintage radio/telephone | 0.5 = Natural location mic | 1.0 = Crisp, close-mic studio clarity.",
                    },
                ),
                "offscreen_voiceover": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Off-Screen Voiceover",
                        "label_off": "On-Screen Speech",
                        "tooltip": "When enabled, uses MiniMax H3's 'says in an off-screen voiceover' syntax and locks the on-screen character's lips closed.",
                    },
                ),
                "lock_other_lips": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Lock Listener Lips Closed",
                        "label_off": "Normal Listener Behavior",
                        "tooltip": "When enabled, appends a clause keeping other visible characters silent with closed mouths to prevent H3 multi-character lip bleed.",
                    },
                ),
                "studio_dry_isolation": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label_on": "Dry Vocal Isolation",
                        "label_off": "Natural Room Reverb",
                        "tooltip": "ON = Dry, voice-forward close-mic studio isolation with no echo. OFF = Natural environmental room reflections wrap around the voice.",
                    },
                ),
                "vocal_fry": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Vocal Fry Enabled",
                        "label_off": "No Vocal Fry",
                        "tooltip": "When enabled, adds subtle creaky, low-frequency glottal vocal fry resonance at the end of spoken phrases.",
                    },
                ),
                "nasal_resonance": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Nasal Resonance On",
                        "label_off": "Standard Resonance",
                        "tooltip": "When enabled, shifts vocal placement forward to add a distinct nasal formant resonance (~1.1 kHz).",
                    },
                ),
                "singing_mode": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Melodic Singing",
                        "label_off": "Spoken Dialogue",
                        "tooltip": "Switches the H3 delivery verb from spoken dialogue ('says'/'murmurs'/'shouts') to melodic singing ('sings'/'softly hums'/'belts out').",
                    },
                ),
                "cross_cut_continuity": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "Continues Across Cut",
                        "label_off": "Contained in Shot",
                        "tooltip": "When enabled, appends 'The audio continues seamlessly across the cut.' so spoken dialogue bridges smoothly into the next shot.",
                    },
                ),
                "dialogue_text": (
                    "STRING",
                    {
                        "default": "I get off at the next station.",
                        "multiline": True,
                        "tooltip": "Enter the exact verbatim words to be spoken inside the MiniMax H3 <d>[Language] ...</d> dialogue block.",
                    },
                ),
            },
            "optional": {
                "audio_ref_tag": (
                    ["None", "<audio_1>", "<audio_2>", "<audio_3>"],
                    {
                        "default": "None",
                        "tooltip": "Optional Ref2VA audio reference tag (<audio_1>, <audio_2>, <audio_3>) to bind this speaker's voice profile to an external audio input.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "H3_VOICE_PARAMS")
    RETURN_NAMES = (
        "h3_dialogue_block",
        "voice_profile_only",
        "soundscape_acoustic_hint",
        "voice_params",
    )
    OUTPUT_TOOLTIPS = (
        "Complete MiniMax H3 dialogue sentence including subject, voice profile, speaker ID, <d>[Language] ...</d> block, and lip-lock/continuity rules.",
        "Standalone descriptive voice profile string (pitch, warmth, rasp, breathiness, rate, accent, emotion) for custom prompt templates.",
        "Microphone and room acoustic sentence ready to append to your MiniMax H3 overall_soundscape section.",
        "Live parameter bundle—connect this to the MiniMax H3 Voice Test & Audio Preview node to hear your voice settings immediately.",
    )
    FUNCTION = "build_voice_prompt"
    CATEGORY = "MiniMax H3/Audio & Voice"

    @staticmethod
    def _map_pitch(val: float) -> str:
        if val <= -0.7:
            return "deep, resonant bass-baritone"
        if val <= -0.3:
            return "low-pitched"
        if val < 0.3:
            return "natural mid-range"
        if val < 0.7:
            return "high-pitched"
        return "bright, high-register"

    @staticmethod
    def _map_warmth(val: float) -> str:
        if val <= -0.6:
            return "cold, clinical, sharp-edged"
        if val <= -0.2:
            return "crisp, cool"
        if val < 0.2:
            return "balanced"
        if val < 0.6:
            return "warm, rounded"
        return "rich, velvety, deeply warm"

    @staticmethod
    def _map_rasp(val: float) -> str:
        if val < 0.15:
            return "clear, smooth"
        if val < 0.45:
            return "slightly textured"
        if val < 0.75:
            return "husky, raspy"
        return "heavily gravelly, weathered, and hoarse"

    @staticmethod
    def _map_breathiness(val: float) -> str:
        if val < 0.15:
            return "full-chested"
        if val < 0.45:
            return "softly airy"
        if val < 0.75:
            return "breathy, intimate"
        return "heavily breathy, near-whispered"

    @staticmethod
    def _map_rate(val: float) -> str:
        if val <= -0.6:
            return "at a very slow, deliberate, unhurried pace"
        if val <= -0.2:
            return "at a slow, measured rate"
        if val < 0.2:
            return "at a natural conversational rate"
        if val < 0.6:
            return "at a brisk, energetic pace"
        return "at a rapid, fast-paced clip"

    @staticmethod
    def _map_projection(val: float, singing: bool) -> tuple[str, str]:
        if singing:
            if val <= -0.4:
                return "softly hums and sings", "with hushed vocal projection"
            if val >= 0.5:
                return "belts out and sings", "with powerful, resonant projection"
            return "sings", "with clear melodic projection"

        if val <= -0.7:
            return "murmurs", "at a hushed, barely audible volume"
        if val <= -0.3:
            return "says softly", "in a quiet, low-volume delivery"
        if val < 0.3:
            return "says", "at an even conversational volume"
        if val < 0.7:
            return "says firmly", "with strong, projected vocal presence"
        return "shouts", "at a loud, booming volume"

    @staticmethod
    def _map_emotion(tone: str, intensity: float) -> str:
        clean_tone = tone.split("/")[0].strip().lower()
        if clean_tone == "neutral":
            return "with a composed, matter-of-fact inflection"
        if intensity < 0.3:
            return f"with a subtle, restrained hint of {clean_tone} emotion"
        if intensity < 0.7:
            return f"in a {clean_tone} tone"
        return f"with an intense, deeply expressive {clean_tone} delivery"

    @staticmethod
    def _map_acoustics(clarity: float, dry_isolation: bool) -> tuple[str, str]:
        if clarity < 0.25:
            quality_phrase = "lo-fi, band-limited, vintage radio-style audio fidelity"
            soundscape_hint = (
                "The vocal track carries a compressed, lo-fi acoustic filtering "
                "with rolled-off highs and subtle analog warmth."
            )
        elif clarity < 0.6:
            quality_phrase = "natural on-location microphone sound"
            soundscape_hint = (
                "Voices blend naturally into the surrounding room tone with realistic spatial distance."
            )
        else:
            quality_phrase = "crisp, high-definition close-mic vocal clarity"
            soundscape_hint = (
                "The dialogue is captured with clean, voice-forward studio clarity and zero distortion."
            )

        if dry_isolation:
            quality_phrase += " and dry acoustic isolation"
            soundscape_hint += " Minimal room echo or competing background reflection on the voice."
        else:
            quality_phrase += " and natural room resonance"
            soundscape_hint += " Subtle environmental acoustics and room reflections wrap around the voice."

        return quality_phrase, soundscape_hint

    def build_voice_prompt(
        self,
        speaker_id: str,
        subject_reference: str,
        vocal_archetype: str,
        language: str,
        accent: str,
        emotional_tone: str,
        pitch: float,
        timbre_warmth: float,
        texture_rasp: float,
        breathiness: float,
        speech_rate: float,
        projection_volume: float,
        emotional_intensity: float,
        acoustic_clarity: float,
        offscreen_voiceover: bool,
        lock_other_lips: bool,
        studio_dry_isolation: bool,
        vocal_fry: bool,
        nasal_resonance: bool,
        singing_mode: bool,
        cross_cut_continuity: bool,
        dialogue_text: str,
        audio_ref_tag: str = "None",
    ):
        pitch_desc = self._map_pitch(pitch)
        warmth_desc = self._map_warmth(timbre_warmth)
        rasp_desc = self._map_rasp(texture_rasp)
        breath_desc = self._map_breathiness(breathiness)
        rate_desc = self._map_rate(speech_rate)
        verb, proj_desc = self._map_projection(projection_volume, singing_mode)
        emotion_desc = self._map_emotion(emotional_tone, emotional_intensity)
        acoustic_desc, soundscape_hint = self._map_acoustics(acoustic_clarity, studio_dry_isolation)

        timbre_extras = []
        if nasal_resonance:
            timbre_extras.append("a distinct nasal resonance")
        if vocal_fry:
            timbre_extras.append("subtle vocal fry at phrase endings")
        extra_timbre_str = f" with {' and '.join(timbre_extras)}" if timbre_extras else ""

        accent_str = (
            f" in a {accent} accent"
            if accent != "Neutral / Unspecified"
            else ""
        )

        voice_profile = (
            f"a {warmth_desc}, {pitch_desc}, {rasp_desc}, {breath_desc} voice"
            f"{extra_timbre_str} ({acoustic_desc}), speaking {rate_desc}{accent_str}, "
            f"{proj_desc} {emotion_desc}"
        )

        subj = subject_reference.strip() or "The speaker"
        if vocal_archetype != "auto (use subject_reference)":
            subject_phrase = f"{subj}, a {vocal_archetype} with {voice_profile}"
        else:
            subject_phrase = f"{subj} with {voice_profile}"

        if audio_ref_tag and audio_ref_tag != "None":
            subject_phrase += f" guided by {audio_ref_tag}'s vocal timbre"
            soundscape_hint = (
                f"{audio_ref_tag} serves as the voice-timbre and delivery reference for ({speaker_id}). "
                + soundscape_hint
            )

        clean_dialogue = " ".join(dialogue_text.strip().splitlines())
        dialogue_tag = f"<d>[{language}] {clean_dialogue}</d>"

        if offscreen_voiceover:
            h3_block = (
                f"{subject_phrase} ({speaker_id}) says in an off-screen voiceover: "
                f"{dialogue_tag} while their lips remain completely closed."
            )
        else:
            h3_block = f"{subject_phrase} ({speaker_id}) {verb}: {dialogue_tag}"

        tail_clauses = []
        if lock_other_lips and not offscreen_voiceover:
            tail_clauses.append("Other visible characters listen silently while their lips remain closed.")
        if cross_cut_continuity:
            tail_clauses.append("The audio continues seamlessly across the cut.")

        if tail_clauses:
            h3_block = f"{h3_block} {' '.join(tail_clauses)}"

        voice_params = {
            "vocal_archetype": vocal_archetype,
            "subject_reference": subj,
            "language": language,
            "accent": accent,
            "emotional_tone": emotional_tone,
            "pitch": pitch,
            "timbre_warmth": timbre_warmth,
            "texture_rasp": texture_rasp,
            "breathiness": breathiness,
            "speech_rate": speech_rate,
            "projection_volume": projection_volume,
            "emotional_intensity": emotional_intensity,
            "acoustic_clarity": acoustic_clarity,
            "studio_dry_isolation": studio_dry_isolation,
            "vocal_fry": vocal_fry,
            "nasal_resonance": nasal_resonance,
            "dialogue_text": clean_dialogue,
            "voice_profile": voice_profile,
        }

        return (h3_block, voice_profile, soundscape_hint, voice_params)
