"""
Real-Time Emergency Call System
Transcription Service - Convert Audio to Text using Whisper
"""
import whisper
import time
from pathlib import Path

class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper"""
    
    def __init__(self, model_name="base"):
        """
        Initialize Whisper model
        
        Models available (size/accuracy trade-off):
        - tiny: fastest, least accurate (~40MB)
        - base: good balance (~140MB)
        - small: better accuracy (~460MB)
        - medium: high accuracy (~1.5GB)
        - large: best accuracy (~3GB)
        """
        print(f"Loading Whisper model: {model_name}...")
        self.model_name = model_name
        self.model = whisper.load_model(model_name)
        print(f"✓ Whisper {model_name} model loaded")
    
    def transcribe(self, audio_path: str, language: str = "en") -> dict: #dict is a dictionary used to store data in key-value pairs cause we need to return multiple values
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file (wav, mp3, m4a, etc.)
            language: 'en' for English, 'ja' for Japanese, 'auto' for detection
        
        Returns:
            dict with:
                - text: Full transcript
                - duration: Audio duration in seconds
                - language: Detected language
                - processing_time: How long transcription took
        """
        start_time = time.time()
        
        # Validate file exists
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing: {audio_path} (Language hint: {language})")
        
        # Whisper language code for Japanese is 'ja'
        lang_code = None if language == "auto" else language
        
        # Transcribe with tuned parameters for medical/emergency context
        result = self.model.transcribe(
            audio_path,
            language=lang_code,
            fp16=False,                 # CPU compatibility
            temperature=0.0,            # Deterministic (no random sampling)
            no_speech_threshold=0.6,    # stricter silence detection
            logprob_threshold=-1.0,     # discard low confidence
            condition_on_previous_text=False # prevent hallucination loops
        )
        
        processing_time = time.time() - start_time
        detected_language = result.get("language", "en")
        
        # Extract results
        transcript = result["text"].strip()
        
        print(f"✓ Transcription complete ({processing_time:.2f}s) - Language: {detected_language}")
        print(f"  Text length: {len(transcript)} characters")
        
        return {
            "text": transcript,
            "duration": result.get("duration", 0),
            "language": detected_language,
            "processing_time": processing_time
        }


# Create global instance (loads model once)
# Using 'base' model as requested by user
transcription_service = TranscriptionService(model_name="base")
