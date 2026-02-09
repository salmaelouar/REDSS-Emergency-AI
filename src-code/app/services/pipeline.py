"""
Real-Time Emergency Call System
Complete Processing Pipeline
"""
from app.services.transcription import transcription_service
from app.services.soap_extractor import SOAPExtractor
from app.services.urgency_classifier import urgency_classifier
from app.services.database import save_call, update_soap, update_urgency, get_call
from datetime import datetime
import time

class ProcessingPipeline:
    """Complete call processing pipeline"""
    
    def __init__(self):
        # SOAPExtractor needs to load OpenAI client once
        # Now we can reuse it for every call
        #self.soap_extractor.extract(text1)
        #self.soap_extractor.extract(text2)
        # ... without reloading the OpenAI client each time
        self.soap_extractor = SOAPExtractor()
    
    
    #Full Audio Processing
    def process_call(self, audio_path: str, language: str = "en") -> dict:
        """
        Process an emergency call through the complete pipeline
        
        Args:
            audio_path: Path to audio file
            language: Target language (en, ja, etc.)
        
        Returns:
            dict with complete analysis
        """
        start_time = time.time()
        # Include seconds for uniqueness
        call_id = f"CALL_{datetime.now().strftime('%d%b_%Hh%M_%S')}" 
        #Console Output for Tracking:-> output: Console Output for Tracking:
        print(f"\n{'='*60}")
        print(f"Processing call: {call_id} (Language: {language})")
        print(f"{'='*60}") #'='*60 creates a line of 60 equal signs
        
        try:
            # Step 1: Transcribe -> what happens-> Call Whisper service:
            print(f"\n[1/4] Transcribing audio in {language}...")
            # If japanese, we use 'ja' for whisper
            whisper_lang = "ja" if language in ["ja", "jp", "japanese"] else language
            transcription = transcription_service.transcribe(audio_path, language=whisper_lang)
            transcript = transcription['text'] # the actual text 
            duration = transcription['duration']
            
            # Save to database
            save_call(call_id, audio_path, transcript, duration, language=language)
            print(f"✓ Transcription complete ({len(transcript)} characters)")
            
            # Step 2: Extract SOAP
            print(f"\n[2/4] Extracting SOAP notes in {language}...")
            soap = self.soap_extractor.extract(transcript, target_language=language)
            update_soap(call_id, soap['subjective'], soap['objective'],
                       soap['assessment'], soap['plan'])
            print(f"✓ SOAP extraction complete")
            
            # Step 3: Classify urgency
            print(f"\n[3/4] Classifying urgency in {language}...")
            urgency = urgency_classifier.classify(transcript, soap, language=language) #what happends-> Call hybrid classifier:
            update_urgency(call_id, urgency['level'], urgency['score'],
                         urgency['reasoning'])
            print(f"✓ Urgency classified: {urgency['level']}")
            
            # Step 4: Get final result
            print("\n[4/4] Finalizing...")
            call = get_call(call_id)
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'call_id': call.call_id,
                'language': language,
                'patient_name': call.patient_name,
                'doctor_name': call.doctor_name,
                'disease': call.disease,
                'processing_time': round(processing_time, 2),
                'audio_duration': call.audio_duration,
                'transcript': call.transcript,
                'soap': {
                    'subjective': call.soap_subjective,
                    'objective': call.soap_objective,
                    'assessment': call.soap_assessment,
                    'plan': call.soap_plan
                },
                'urgency': {
                    'level': call.urgency_level,
                    'score': call.urgency_score,
                    'reasoning': call.urgency_reasoning
                },
                'created_at': call.created_at.isoformat()
            }
            
            print(f"\n✅ Processing complete in {processing_time:.2f}s")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"\n✗ Processing failed: {e}")
            raise
    
    def process_text(self, transcript: str, patient_name: str = None, 
                     doctor_name: str = None, disease: str = None,
                     language: str = "en") -> dict: #Method 2: process_text() - Skip Audio Transcription

        """
        Process text transcript directly (skip audio transcription)
        
        Args:
            transcript: Text transcript of emergency call
            language: Target language
        
        Returns:
            dict with complete analysis
        """

        #Performance tracking:
        start_time = time.time()
        # Include seconds for uniqueness
        call_id = f"TEXT_{datetime.now().strftime('%d%b_%Hh%M_%S')}"
        
        print(f"\n{'='*60}")
        print(f"Processing text input: {call_id} (Language: {language})")
        print(f"{'='*60}")
        
        try:
            # Step 1: Save to database (no audio file)
            print("\n[1/3] Saving to database...")
            save_call(call_id, "text_input", transcript, 0.0, patient_name, doctor_name, disease, language=language)
            print(f"✓ Saved ({len(transcript)} characters) as {call_id}")
            
            # Step 2: Extract SOAP
            soap = self.soap_extractor.extract(transcript, target_language=language)
            
            # EXTRACT PATIENT INFO from SOAP Objective
            # The extractor puts Name: ..., Age: ... in Objective section
            objective_text = soap.get('objective', '')
            extracted_name = None
            
            # Simple parsing for Name/Age/Address to update DB re is a regex and means:
            # - Name: ... or 氏名: ... (in Japanese)
            # - Age: ... or 年齢: ... (in Japanese)
            # - Address: ... or 住所: ... (in Japanese)
            #is normaly used to extract information from a string
            import re
            
            # Check for Name
            name_match = re.search(r'(?:Name|氏名)[:：]\s*(.+)', objective_text, re.IGNORECASE)
            if name_match:
                extracted_name = name_match.group(1).strip()
                if extracted_name.lower() not in ['[not provided]', '[不明]', 'unknown', 'n/a']:
                    # Update variable for return
                    if not patient_name:
                        patient_name = extracted_name
                        # Update DB call record
                        from app.services.database import get_db, EmergencyCall
                        try:
                            with get_db() as db:
                                call_obj = db.query(EmergencyCall).filter(EmergencyCall.call_id == call_id).first()
                                if call_obj:
                                    call_obj.patient_name = extracted_name
                                    db.commit()
                        except Exception as e:
                            print(f"Failed to update patient name in DB: {e}")

            update_soap(call_id, soap['subjective'], soap['objective'],
                       soap['assessment'], soap['plan'])
            print(f"✓ SOAP extraction complete")
            
            # Step 3: Classify urgency
            print(f"\n[3/3] Classifying urgency in {language}...")
            urgency = urgency_classifier.classify(transcript, soap, language=language)
            update_urgency(call_id, urgency['level'], urgency['score'],
                         urgency['reasoning'])
            print(f"✓ Urgency classified: {urgency['level']}")
            
            # Get final result
            call = get_call(call_id)
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'call_id': call.call_id,
                'patient_name': call.patient_name,
                'doctor_name': call.doctor_name,
                'disease': call.disease,
                'processing_time': round(processing_time, 2),
                'audio_duration': 0.0,
                'transcript': call.transcript,
                'soap': {
                    'subjective': call.soap_subjective,
                    'objective': call.soap_objective,
                    'assessment': call.soap_assessment,
                    'plan': call.soap_plan
                },
                'urgency': {
                    'level': call.urgency_level,
                    'score': call.urgency_score,
                    'reasoning': call.urgency_reasoning
                },
                'created_at': call.created_at.isoformat()
            }
            
            print(f"\n✅ Processing complete in {processing_time:.2f}s")
            print(f"{'='*60}\n")
            
            return result
            #Error Handling:
        except Exception as e:
            print(f"\n✗ Processing failed: {e}")
            raise


# Create global instance
pipeline = ProcessingPipeline()