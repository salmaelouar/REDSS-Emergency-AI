"""
Real-Time Call Handler - IMPROVED
WebSocket-basierte Live-Audio-Verarbeitung mit ECHTER Real-Time Transkription
"""
import asyncio
import json
import base64
import numpy as np
from datetime import datetime
from typing import Optional
import io
import wave
import os
import subprocess
import tempfile
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)# logging is used to log messages in the console
logger = logging.getLogger(__name__)

class RealtimeCallHandler:
    """Handles real-time audio streaming and processing"""
    # constructor is a special method that is called when an object is created we do it because we need to initialize the object with some values
    def __init__(self, pipeline, db_session): # we put self.pipeline and self.db_session as parameters to use them later in other methods like _process_queue and _transcribe_chunk and why we need self. is to make them accessible to other methods
        self.pipeline = pipeline #pipeline is not the pipeline of the model but the pipeline of the app is used in the _transcribe_chunk method to process the audio            
        self.db = db_session #db_session is used to save the call in the database
        self.call_id = None #call_id is used to identify the call
        self.audio_buffer = [] #audio_buffer is used to store the audio chunks
        self.transcript_buffer = "" #transcript_buffer is used to store the transcript chunks -> chunks are used to process the audio in smaller parts to avoid memory overflow 
        self.word_count = 0 #word_count is used to count the number of words in the transcript
        self.sample_rate = 16000 #sample_rate is used to set the sample rate of the audio
        # is the pipeline same as pipeline.py ? -> no it is not the same but it is used to process the audio in real time in the _transcribe_chunk method that i can finde in realtime_call.py why i have to define pipeline here? cause -> how is she proseccing in real time the audio? > _transcribe_chunk method is used to process the audio in real time in the _transcribe_chunk method that i can finde in realtime_call.py

        # Async Queue for processing chunks
        self.queue = asyncio.Queue() #queue is used to store the audio chunks
        self.processing_task = None #processing_task is used to store the processing task
        self.is_running = False #is_running is used to check if the call is running
        
        # Check dependencies -> dependencies are the required packages or modules that are needed to run the code -> here we need ffmpeg to convert the audio to wav 
        if not shutil.which('ffmpeg'): #shutil is a module in python that provides a high-level interface for file operations
            logger.error("CRITICAL: FFmpeg not found! Live call will fail.")

    async def start_call(self, language: str = "en") -> str: #if i do not us async it will block the main thread and await is used to wait for the function to finish
        """Initialize new real-time call"""
        if not shutil.which('ffmpeg'): #shutil is a module in python that provides a high-level interface for file operations
            raise RuntimeError("FFmpeg is not installed on the server. Cannot process audio.")

        self.call_id = f"LIVE_{datetime.now().strftime('%d%b_%Hh%M')}" #call_id is used to identify the call
        self.language = language #language is used to set the language of the call
        self.audio_buffer = [] #audio_buffer is used to store the audio chunks
        self.transcript_buffer = "" #transcript_buffer is used to store the transcript chunks
        self.word_count = 0 #word_count is used to count the number of words in the transcript
        self.start_time = datetime.now() #start_time is used to store the start time of the call
        
        # Start processing worker
        self.is_running = True           #is_running is used to check if the call is running
        self.processing_task = asyncio.create_task(self._process_queue()) #processing_task is used to store the processing task
        
        logger.info(f"🔴 LIVE CALL STARTED: {self.call_id} ({self.language})")
        return self.call_id
    
    async def process_audio_chunk(self, audio_data: str) -> dict:
        """
        Receive incoming audio chunk and put it in the queue.
        Returns immediate ack to keep WebSocket responsive.
        """
        try:
            # Decode audio immediately to fail fast, but process later
            audio_bytes = base64.b64decode(audio_data)
            
            if len(audio_bytes) < 1000:
                return {"status": "buffering", "call_id": self.call_id}
            
            # Put in queue
            await self.queue.put(audio_bytes)
            
            # Return current state (processed async by worker)
            # We include the CURRENT buffer state so the UI updates (polling effect)
            return {
                "status": "processing",
                "call_id": self.call_id,
                "queue_size": self.queue.qsize(),
                "word_count": self.word_count,
                "full_transcript": self.transcript_buffer.strip(),
                "soap": getattr(self, 'latest_soap', None),
                "language": self.language
            }
            
        except Exception as e:
            logger.error(f"❌ Error receiving audio: {e}")
            return {"status": "error", "error": str(e)}

    async def _process_queue(self):
        """Background worker that processes audio chunks one by one"""
        logger.info("Worker started")
        
        while self.is_running or not self.queue.empty():
            try:
                # Get next chunk
                try:
                    audio_bytes = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # PROCESS CHUNK (No batching, as WebM files cannot be simply concatenated)
                await self._transcribe_chunk(audio_bytes) #_transcribe_chunk is used to transcribe the audio in real time
                self.queue.task_done() #task_done is used to mark the task as done
                
                # Drain queue if backing up (drop intermediate? No, process them)
                # If we want to skip processing to catch up, we could, but that loses audio.
                # For now, strict one-by-one.
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                import traceback
                traceback.print_exc()

    async def _transcribe_chunk(self, audio_bytes):
        """Heavy lifting: Save file, ffmpeg, transcribe (in thread)"""
        try:
            # Create temp files
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_webm:
                temp_webm.write(audio_bytes)
                webm_path = temp_webm.name
            
            wav_path = webm_path + ".wav"
            
            # Non-blocking FFmpeg
            # We run this in a threadexecutor to avoid blocking the event loop
            await asyncio.to_thread(self._convert_audio, webm_path, wav_path)
            
            if not os.path.exists(wav_path):
                logger.error("WAV file creation failed")
                return None

            # Non-blocking Transcription
            from app.services.transcription import transcription_service
            
            # Use japanese code for whisper if needed
            whisper_lang = "ja" if self.language in ["ja", "jp", "japanese"] else self.language

            # Run transcribe in thread
            result = await asyncio.to_thread(transcription_service.transcribe, wav_path, language=whisper_lang)
            
            # Update State (Thread-safe enough for Python's GIL + Asyncio)
            new_text = result['text'].strip()
            detected_lang = result.get('language', 'en')
            
            # Auto-switch mode if detected language is significantly Japanese
            if detected_lang == 'ja' and self.language == 'en':
                logger.info("🇯🇵 JAPANESE DETECTED - Switching processing mode")
                self.language = 'ja'
            elif detected_lang == 'en' and self.language == 'ja':
                 logger.info("🇺🇸 ENGLISH DETECTED - Switching processing mode")
                 self.language = 'en'

            if new_text:
                self.transcript_buffer += " " + new_text
                self.word_count = len(self.transcript_buffer.split())
                logger.info(f"✓ UPDATE [{self.language}]: {new_text}")
            
            # Partial SOAP
            if self.word_count >= 10 and self.word_count % 10 == 0:
                 # Run in thread as it might be slow
                 soap = await asyncio.to_thread(self.pipeline.soap_extractor.extract, self.transcript_buffer, target_language=self.language)
                 # We might want to store this soap to return it later
                 self.latest_soap = soap

            # Cleanup
            try:
                if os.path.exists(webm_path):
                    os.remove(webm_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            
            return new_text
            
        except Exception as e:
            logger.error(f"Transcribe chunk error: {e}")
            # Ensure cleanup happens even on error
            try:
                if 'webm_path' in locals() and os.path.exists(webm_path):
                    os.remove(webm_path)
                if 'wav_path' in locals() and os.path.exists(wav_path):
                    os.remove(wav_path)
            except:
                pass
            return None

    def _convert_audio(self, input_path, output_path):
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', input_path,
                '-ar', '16000', '-ac', '1', '-f', 'wav',
                output_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
        except Exception as e:
             logger.error(f"Conversion error: {e}")

    async def end_call(self) -> dict:
        """
        Finalize call and run complete analysis.
        Waits for queue to finish first.
        """
        self.is_running = False
        
        # Wait for remaining items
        if not self.queue.empty():
            logger.info(f"Waiting for {self.queue.qsize()} pending chunks...")
            try:
                # Wait max 10 seconds for remaining chunks
                await asyncio.wait_for(self.queue.join(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Timed out waiting for queue to finish")
        
        # Cancel worker
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            
        return await self._finalize_call_logic(language=self.language)

    async def _finalize_call_logic(self, language: str = "en"):
        # ... (Previous end_call logic, but async where needed) ...
        try:
            logger.info(f"⏹️  ENDING CALL: {self.call_id} (Final language: {language})")
            
            if not self.transcript_buffer.strip():
                return {"status": "error", "error": "No transcript"}
            
            # Final Analysis (Threaded)
            soap = await asyncio.to_thread(self.pipeline.soap_extractor.extract, self.transcript_buffer, target_language=language)
            
            from app.services.urgency_classifier import urgency_classifier
            urgency = await asyncio.to_thread(urgency_classifier.classify, self.transcript_buffer, soap, language=language)
            
            # DB Storage (Threaded)
            from app.services.database import save_call, update_soap, update_urgency
            
            duration = (datetime.now() - self.start_time).total_seconds()
            
            await asyncio.to_thread(
                save_call, self.call_id, "realtime_call", self.transcript_buffer, duration, language=language
            )
            
            await asyncio.to_thread(
                update_soap, self.call_id, soap['subjective'], soap['objective'], soap['assessment'], soap['plan']
            )
            
            await asyncio.to_thread(
                update_urgency, self.call_id, urgency['level'], urgency['score'], urgency['reasoning']
            )
            
            return {
                "status": "completed",
                "call_id": self.call_id,
                "transcript": self.transcript_buffer.strip(),
                "soap": soap,
                "urgency": urgency,
                "word_count": self.word_count,
                 "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error finalizing: {e}")
            return {"status": "error", "error": str(e)}