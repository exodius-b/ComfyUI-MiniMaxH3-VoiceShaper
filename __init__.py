from .minimax_h3_voice_node import MiniMaxH3VoiceShaper
from .minimax_h3_voice_preview import MiniMaxH3VoicePreviewer

NODE_CLASS_MAPPINGS = {
    "MiniMaxH3VoiceShaper": MiniMaxH3VoiceShaper,
    "MiniMaxH3VoicePreviewer": MiniMaxH3VoicePreviewer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MiniMaxH3VoiceShaper": "MiniMax H3 Voice Tone & Quality Shaper",
    "MiniMaxH3VoicePreviewer": "MiniMax H3 Voice Test & Audio Preview",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
