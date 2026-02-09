"""
Real-Time Emergency Call System
FastAPI REST API - With Quality Metrics
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pipeline import pipeline
from app.services.database import init_db, get_db
from app.services.quality_metrics import quality_calculator
from app.models.call import EmergencyCall
from pathlib import Path
import shutil
import os
import re
from datetime import datetime
from app.language_markers import router as markers_router
from fastapi import WebSocket, WebSocketDisconnect
from app.services.realtime_call import RealtimeCallHandler
import json


def normalize_urgency_for_ui(urgency_level: str) -> str:
    """
    Normalize urgency level for UI display.
    Maps MINIMAL -> LOW (UI uses 4 levels: CRITICAL, HIGH, MEDIUM, LOW)
    Backend keeps 5 ESI levels internally (1-5).
    """
    if urgency_level == 'MINIMAL':
        return 'LOW'
    return urgency_level


class TextInput(BaseModel):
    text: str
    patient_name: str = None
    doctor_name: str = None
    disease: str = None
    language: str = "en"
    reference_text: str = None  # NEW: Ground truth for manual comparison

class QualityComparisonInput(BaseModel):
    hypothesis_soap: dict[str, str]
    reference_soap: dict[str, str]
    hypothesis_transcript: str = None
    reference_transcript: str = None
    language: str = "en"


# Create FastAPI app
app = FastAPI(
    title="Real-Time Emergency Call System",
    description="AI-powered emergency call analysis",
    version="1.0.0"
)
app.include_router(markers_router)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()
    os.makedirs("data/audio", exist_ok=True)
    print("✓ API server started")


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "online",
        "system": "Real-Time Emergency Call System",
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...), language: str = "en"):
    """Upload and process audio file"""
    try:
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        file_path = f"data/audio/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = pipeline.process_call(file_path, language=language)
        
        # AUTO-SYNC: Sync to patient journey database
        try:
            from app.services.sync_helper import sync_emergency_call_to_patient_journey
            from app.models.call import EmergencyCall
            from app.services.database import get_db
            
            with get_db() as db:
                call_obj = db.query(EmergencyCall).filter(EmergencyCall.call_id == result['call_id']).first()
                if call_obj:
                    sync_emergency_call_to_patient_journey(call_obj.id)
                    print(f"🔄 Auto-synced audio call {result['call_id']} to patient journey")
        except Exception as sync_error:
            print(f"⚠️ Sync failed (non-blocking): {sync_error}")
            
        # Normalize for UI
        if 'urgency' in result and 'level' in result['urgency']:
            result['urgency']['level'] = normalize_urgency_for_ui(result['urgency']['level'])
            
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/process-text")
async def process_text(input_data: TextInput):
    """Process text directly"""
    try:
        if not input_data.text or len(input_data.text.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Text is too short to process (minimum 3 characters)"
            )
        
        result = pipeline.process_text(
            input_data.text, 
            patient_name=input_data.patient_name,
            doctor_name=input_data.doctor_name,
            disease=input_data.disease,
            language=input_data.language
        )
        print(f"✓ Pipeline processed text: {result['call_id']}")
        
        # AUTO-SYNC: Sync to patient journey database
        try:
            from app.services.sync_helper import sync_emergency_call_to_patient_journey
            from app.models.call import EmergencyCall
            from app.services.database import get_db
            
            # We need the numeric ID, not the string call_id
            with get_db() as db:
                call_obj = db.query(EmergencyCall).filter(EmergencyCall.call_id == result['call_id']).first()
                if call_obj:
                    sync_emergency_call_to_patient_journey(call_obj.id)
                    print(f"🔄 Auto-synced call {result['call_id']} to patient journey")
        except Exception as sync_error:
            print(f"⚠️ Sync failed (non-blocking): {sync_error}")
            
        # Normalize for UI
        if 'urgency' in result and 'level' in result['urgency']:
            result['urgency']['level'] = normalize_urgency_for_ui(result['urgency']['level'])
            
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        print(f"❌ Error in /api/process-text: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls")
def list_calls(limit: int = 50, lang: str = None):
    """List all calls with optional translation"""
    with get_db() as db:
        calls = db.query(EmergencyCall).order_by(
            EmergencyCall.created_at.desc()
        ).limit(limit).all()
        
        calls_data = []
        for call_obj in calls:
            # Parse existing cache
            cache = json.loads(call_obj.translated_data or "{}")
            
            # Prepare basic data
            item = {
                "call_id": call_obj.call_id,
                "urgency_level": normalize_urgency_for_ui(call_obj.urgency_level) if call_obj.urgency_level else None,
                "urgency_score": call_obj.urgency_score,
                "audio_duration": call_obj.audio_duration,
                "created_at": call_obj.created_at.isoformat() if call_obj.created_at else None,
                "transcript": call_obj.transcript,
                "transcript_preview": call_obj.transcript[:100] + "..." if call_obj.transcript else None,
                "soap_subjective": call_obj.soap_subjective,
                "soap_objective": call_obj.soap_objective,
                "soap_assessment": call_obj.soap_assessment,
                "soap_plan": call_obj.soap_plan,
                "patient_name": call_obj.patient_name,
                "doctor_name": call_obj.doctor_name,
                "disease": call_obj.disease,
                "language": call_obj.language or "en",
                "urgency_reasoning": call_obj.urgency_reasoning
            }

            # If translation requested
            if lang and lang != item["language"]:
                # Check cache first with improved validation
                # Cache version: v2 (includes proper label localization)
                CACHE_VERSION = "v2"
                is_valid_cache = False
                if lang in cache:
                    cached = cache[lang]
                    
                    # Check cache version first
                    if cached.get("_version") != CACHE_VERSION:
                        print(f"⚠️  Old cache version for list item {item['call_id']}. Re-translating...")
                        is_valid_cache = False
                    else:
                        obj_text = cached.get("soap_objective") or ""
                        subj_text = cached.get("soap_subjective") or ""
                        
                        # Enhanced detection: Check for language mixing
                        if lang == "ja":
                            # Japanese should not contain English labels
                            has_english_labels = any(label in obj_text for label in ["Name:", "Age:", "Address:", "Phone:", "Blood:"])
                            has_english_text = any(label in subj_text for label in ["Name:", "Age:", "Address:", "complained", "reported"])
                            if has_english_labels or has_english_text:
                                print(f"⚠️  English content in Japanese cache for {item['call_id']}. Re-translating...")
                            else:
                                is_valid_cache = True
                        elif lang == "en":
                            # English should not contain Japanese labels
                            has_japanese_chars = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', obj_text + subj_text))
                            if has_japanese_chars:
                                print(f"⚠️  Japanese content in English cache for {item['call_id']}. Re-translating...")
                            else:
                                is_valid_cache = True
                        else:
                            # For other languages, just check if cache exists
                            is_valid_cache = True

                if is_valid_cache:
                    cached = cache[lang]
                    item["original"] = {
                        "soap_subjective": item["soap_subjective"],
                        "transcript": item["transcript"],
                        "patient_name": item["patient_name"]
                    }
                    item["patient_name"] = cached.get("patient_name", item["patient_name"])
                    item["disease"] = cached.get("disease", item["disease"])
                    item["urgency_reasoning"] = cached.get("urgency_reasoning", item["urgency_reasoning"])
                    item["soap_subjective"] = cached.get("soap_subjective", item["soap_subjective"])
                    item["soap_objective"] = cached.get("soap_objective", item["soap_objective"])
                    item["soap_assessment"] = cached.get("soap_assessment", item["soap_assessment"])
                    item["soap_plan"] = cached.get("soap_plan", item["soap_plan"])
                else:
                    # Old cache or no cache - just show in original language for list view
                    # Translation will happen when user clicks to view full details
                    pass  # Keep original data, no translation needed for fast switching
            
            calls_data.append(item)

        # Commit any changes from valid cache hits only
        db.commit()

        return {
            "total": len(calls_data),
            "calls": calls_data
        }


@app.get("/api/calls/{call_id}")
def get_call_details(call_id: str, lang: str = None):
    """Get specific call details with optional on-the-fly translation"""
    with get_db() as db:
        call = db.query(EmergencyCall).filter(
            EmergencyCall.call_id == call_id
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Determine if translation is needed
        # We assume the stored language is call.language (or 'en' if not set)
        source_lang = call.language or "en"
        target_lang = lang or source_lang
        
        # Prepare response data (original language)
        transcript = call.transcript
        soap = {
            "subjective": call.soap_subjective or "",
            "objective": call.soap_objective or "",
            "assessment": call.soap_assessment or "",
            "plan": call.soap_plan or ""
        }
        
        urgency = {
            "level": normalize_urgency_for_ui(call.urgency_level) if call.urgency_level else None,
            "score": call.urgency_score,
            "reasoning": call.urgency_reasoning
        }
        
        # Store originals before translation
        original_data = {
            "transcript": call.transcript,
            "soap": {
                "subjective": call.soap_subjective,
                "objective": call.soap_objective,
                "assessment": call.soap_assessment,
                "plan": call.soap_plan
            },
            "urgency": {
                "level": call.urgency_level,
                "score": call.urgency_score,
                "reasoning": call.urgency_reasoning
            }
        }

        patient_name = call.patient_name
        doctor_name = call.doctor_name
        disease = call.disease

        # Load cache
        cache = json.loads(call.translated_data or "{}")

        # If translation requested and target differs from source
        if lang and lang != source_lang:
            # Enhanced cache validation to prevent language mixing
            # Cache version: v2 (includes proper label localization)
            CACHE_VERSION = "v2"
            is_valid_cache = False
            if lang in cache:
                cached = cache[lang]
                
                # Check cache version - invalidate old cache
                if cached.get("_version") != CACHE_VERSION:
                    print(f"⚠️  Old cache version detected for {call_id}. Re-translating...")
                    is_valid_cache = False
                else:
                    obj_text = cached.get("soap_objective") or ""
                    subj_text = cached.get("soap_subjective") or ""
                    assess_text = cached.get("soap_assessment") or ""
                    plan_text = cached.get("soap_plan") or ""
                    
                    # Improved validation for Japanese
                    if lang == "ja":
                        # Check for English labels or words that shouldn't be there
                        english_indicators = ["Name:", "Age:", "Address:", "Phone:", "Blood:", "not provided", "[Not provided]"]
                        has_english = any(indicator in obj_text or indicator in subj_text or indicator in assess_text or indicator in plan_text for indicator in english_indicators)
                        if has_english:
                            print(f"⚠️  English content found in Japanese cache for {call_id}. Re-translating...")
                        else:
                            is_valid_cache = True
                    
                    # Improved validation for English
                    elif lang == "en":
                        # Check for Japanese characters (Hiragana, Katakana, Kanji)
                        has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', obj_text + subj_text + assess_text + plan_text))
                        if has_japanese:
                            print(f"⚠️  Japanese content found in English cache for {call_id}. Re-translating...")
                        else:
                            is_valid_cache = True
                    else:
                        # For other languages
                        is_valid_cache = True

            if is_valid_cache:
                print(f"Cache hit: Serving {lang} for call {call_id}")
                cached = cache[lang]
                soap["subjective"] = cached.get("soap_subjective", soap["subjective"])
                soap["objective"] = cached.get("soap_objective", soap["objective"])
                soap["assessment"] = cached.get("soap_assessment", soap["assessment"])
                soap["plan"] = cached.get("soap_plan", soap["plan"])
                urgency["reasoning"] = cached.get("urgency_reasoning", urgency["reasoning"])
                patient_name = cached.get("patient_name", patient_name)
                doctor_name = cached.get("doctor_name", doctor_name)
                disease = cached.get("disease", disease)
                
                # Check if transcript is in cache too
                if "transcript" in cached:
                    transcript = cached["transcript"]
                elif transcript:
                    print(f"Transcript cache miss: Translating transcript for {call_id} to {lang}")
                    transcript = pipeline.soap_extractor.translate_text(transcript, target_lang)
                    # Update cache with transcript
                    cache[lang]["transcript"] = transcript
                    call.translated_data = json.dumps(cache)
                    # No need for explicit commit if inside 'with get_db()' that handles it
            else:
                print(f"Cache miss: Localizing call {call_id} from {source_lang} to {target_lang}...")
                
                # PREPARE DATA FOR CONSOLIDATED LOCALIZATION
                # This combines 3 separate AI calls into 1
                soap_notes = {
                    "subjective": call.soap_subjective or "",
                    "objective": call.soap_objective or "",
                    "assessment": call.soap_assessment or "",
                    "plan": call.soap_plan or ""
                }
                
                metadata = {
                    "reasoning": urgency["reasoning"] or "",
                    "patient_name": patient_name or "",
                    "doctor_name": doctor_name or "",
                    "disease": disease or ""
                }
                
                # ONE SINGLE CALL to OpenAI (Re-extraction + Localization + Translation)
                localized = pipeline.soap_extractor.localize_call_data(
                    transcript, soap_notes, metadata, target_lang
                )
                
                # UNPACK RESULTS
                transcript = localized.get("transcript", transcript)
                soap["subjective"] = localized.get("subjective", soap["subjective"])
                soap["objective"] = localized.get("objective", soap["objective"])
                soap["assessment"] = localized.get("assessment", soap["assessment"])
                soap["plan"] = localized.get("plan", soap["plan"])
                
                urgency["reasoning"] = localized.get("reasoning", urgency["reasoning"])
                patient_name = localized.get("patient_name", patient_name)
                doctor_name = localized.get("doctor_name", doctor_name)
                disease = localized.get("disease", disease)

                # Save to cache with version
                cache[lang] = {
                    "_version": CACHE_VERSION,
                    "soap_subjective": soap["subjective"],
                    "soap_objective": soap["objective"],
                    "soap_assessment": soap["assessment"],
                    "soap_plan": soap["plan"],
                    "urgency_reasoning": urgency["reasoning"],
                    "patient_name": patient_name,
                    "doctor_name": doctor_name,
                    "disease": disease,
                    "transcript": transcript
                }
                call.translated_data = json.dumps(cache)
                # Session will commit at end of 'with' block

        return {
            "call_id": call.call_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "disease": disease,
            "audio_duration": call.audio_duration,
            "transcript": transcript,
            "language": source_lang,
            "target_language": target_lang,
            "soap": soap,
            "urgency": urgency,
            "original": original_data if lang and lang != source_lang else None,
            "created_at": call.created_at.isoformat() if call.created_at else None,
            "processed_at": call.processed_at.isoformat() if call.processed_at else None
        }


# =====================================================
# NEW ENDPOINT: Quality Metrics (BLEU & CUDA)
# =====================================================
@app.get("/api/calls/{call_id}/quality")
def get_quality_metrics(call_id: str):
    with get_db() as db:
        call = db.query(EmergencyCall).filter(
            EmergencyCall.call_id == call_id
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if not call.soap_subjective:
            raise HTTPException(
                status_code=400, 
                detail="No SOAP notes available for this call"
            )
        
        # AI-generated SOAP (hypothesis)
        hypothesis_soap = {
            "subjective": call.soap_subjective or "",
            "objective": call.soap_objective or "",
            "assessment": call.soap_assessment or "",
            "plan": call.soap_plan or ""
        }
        
        # Try to get expected SOAP from evaluated_text_data.py (reference/gold standard)
        reference_soap = None
        matched_call_id = None
        
        try:
            from data.text.evaluated_text_data import EVALUATED_CALLS
            from data.text.custom_test_scripts import CUSTOM_CALLS
            from difflib import SequenceMatcher
            import re

            def clean_for_match(t):
                if not t: return ""
                # Remove labels, [brackets], and punctuation
                t = re.sub(r'^(Dispatcher|Caller|通信指令員|通報者):\s*', '', t, flags=re.MULTILINE)
                t = re.sub(r'\[.*?\]', '', t)
                t = re.sub(r'[^\w\s]', '', t)
                return " ".join(t.lower().split())

            # 1. Prioritize CUSTOM_CALLS, then EVALUATED_CALLS
            ALL_TEST_CALLS = CUSTOM_CALLS + EVALUATED_CALLS

            # 2. Try EXACT match by ID first
            for eval_call in ALL_TEST_CALLS:
                if eval_call["call_id"] == call_id:
                    reference_soap = eval_call["expected_soap"]
                    matched_call_id = eval_call["call_id"]
                    break
            
            # 3. If no exact match, try SMART fuzzy match
            if not reference_soap and call.transcript:
                best_ratio = 0
                best_match = None
                
                # Normalize current transcript
                current_clean = clean_for_match(call.transcript)[:300]
                
                for eval_call in ALL_TEST_CALLS:
                    ref_clean = clean_for_match(eval_call["text"])[:300]
                    ratio = SequenceMatcher(None, current_clean, ref_clean).ratio()
                    
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = eval_call
                
                # Threshold: If > 40% similarity, assume it's this script
                if best_ratio > 0.4 and best_match:
                    print(f"🎯 Smart Match! Detected script '{best_match['call_id']}' (Similarity: {best_ratio:.2f})")
                    reference_soap = best_match["expected_soap"]
                    matched_call_id = best_match["call_id"]

        except Exception as e:
            print(f"⚠️ Could not load expected SOAP data: {e}")
        
        # Default: No metrics if no gold standard
        metrics = {
            "overall": {"bleu_avg": 0, "cuda_overall": 0},
            "fields": {f: {"bleu": {"b1":0,"b2":0,"b3":0,"b4":0}, "cuda": {"c":0,"u":0,"d":0,"a":0}} for f in ["subjective", "objective", "assessment", "plan"]}
        }
        
        if matched_call_id and reference_soap:
            note = f"Comparing against Gold Standard script: {matched_call_id}"
            metrics = quality_calculator.calculate_all_metrics(
                reference_soap=reference_soap,
                hypothesis_soap=hypothesis_soap
            )
        else:
            note = "No matching reference script found in database. Please use the Live System Test with a manual reference to verify accuracy."

        
        # NEW: Calculate transcription quality (WER) if we have expected transcript
        transcription_metrics = None
        try:
            if reference_soap:  # Has gold standard
                # Try to get expected transcript from the matched call
                expected_transcript = None
                for eval_call in ALL_TEST_CALLS:
                    if eval_call.get("call_id") == matched_call_id:
                        expected_transcript = eval_call.get("text")
                        break
                
                if expected_transcript and call.transcript:
                    transcription_metrics = quality_calculator.calculate_wer(
                        reference=expected_transcript,
                        hypothesis=call.transcript
                    )
        except Exception as e:
            print(f"⚠️ Could not calculate transcription metrics: {e}")
        
        # ✅ ENSURE THIS STRUCTURE:
        return {
            "call_id": call_id,
            "transcript": call.transcript, # NEW: Actual transcript
            "hypothesis_soap": hypothesis_soap,
            "reference_soap": reference_soap,
            "metrics": metrics,  # Contains 'fields' and 'overall'
            "fields": metrics.get("fields", {}),  # ✅ Add this
            "overall": metrics.get("overall", {}), # ✅ Add this
            "transcription": {
                **(transcription_metrics or {}),
                "bleu": quality_calculator.calculate_bleu(expected_transcript, call.transcript) if (expected_transcript and call.transcript) else {},
                "cuda": quality_calculator.calculate_cuda(expected_transcript, call.transcript) if (expected_transcript and call.transcript) else {}
            } if transcription_metrics else None,
            "note": note,
            "has_gold_standard": matched_call_id is not None
        }


@app.post("/api/test-live")
async def test_live_emergency(input_data: TextInput):
    """
    Live emergency call testing - process and compare with expected
    Returns system analysis + expected triage for comparison
    """
    try:
        if not input_data.text or len(input_data.text.strip()) < 3:
            raise HTTPException(status_code=400, detail="Text too short")
        
        language = input_data.language or "en"
        
        # Step 1: Process with pipeline (without saving to DB)
        from app.services.soap_extractor import soap_extractor
        from app.services.urgency_classifier import urgency_classifier
        
        # Extract SOAP
        soap = soap_extractor.extract(input_data.text, target_language=language)
        
        # Classify urgency
        urgency = urgency_classifier.classify(
            input_data.text, 
            soap, 
            language=language
        )
        
        # Step 2: Try to find expected values from test data
        expected_urgency = None
        expected_soap = None
        matched_script = None
        
        try:
            from data.text.evaluated_text_data import EVALUATED_CALLS
            from data.text.custom_test_scripts import CUSTOM_CALLS
            from difflib import SequenceMatcher
            import re
            
            def clean_for_match(t):
                if not t: return ""
                t = re.sub(r'^(Dispatcher|Caller|通信指令員|通報者):\s*', '', t, flags=re.MULTILINE)
                t = re.sub(r'\[.*?\]', '', t)
                t = re.sub(r'[^\w\s]', '', t)
                return " ".join(t.lower().split())
            
            ALL_TEST_CALLS = CUSTOM_CALLS + EVALUATED_CALLS
            
            # Smart fuzzy matching
            best_ratio = 0
            best_match = None
            current_clean = clean_for_match(input_data.text)[:300]
            
            for eval_call in ALL_TEST_CALLS:
                ref_clean = clean_for_match(eval_call["text"])[:300]
                ratio = SequenceMatcher(None, current_clean, ref_clean).ratio()
                
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = eval_call
            
            # If >40% match, assume it's this script
            if best_ratio > 0.4 and best_match:
                expected_urgency = best_match.get("expected_urgency", "").upper()
                expected_soap = best_match.get("expected_soap", {})
                matched_script = best_match.get("call_id", "Unknown")
        except Exception as e:
            print(f"Could not load expected data: {e}")
        
        # Transcription quality for live test
        transcription_metrics = None
        try:
            # ONLY calculate WER if a manual reference is provided
            # No more auto-matching for WER to avoid 23800% errors
            if input_data.reference_text:
                from app.services.quality_metrics import quality_calculator
                transcription_metrics = quality_calculator.calculate_wer(
                    reference=input_data.reference_text,
                    hypothesis=input_data.text
                )
        except Exception as e:
            print(f"⚠️ Live test WER calculation failed: {e}")
            
        # Normalize urgency for UI
        system_urgency = normalize_urgency_for_ui(urgency['level'])
        
        return {
            "success": True,
            "system": {
                "soap": soap,
                "urgency": {
                    "level": system_urgency,
                    "score": urgency['score'],
                    "reasoning": urgency['reasoning'],
                    "esi_level": urgency.get('esi_level', 3)
                }
            },
            "expected": {
                "urgency": expected_urgency,
                "soap": expected_soap,
                "matched_script": matched_script
            },
            "comparison": {
                "urgency_match": system_urgency == expected_urgency if expected_urgency else None,
                "has_expected": expected_urgency is not None
            },
            "transcription": transcription_metrics
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quality/calculate-all")
async def calculate_custom_quality(input_data: QualityComparisonInput):
    """Calculate quality metrics purely from provided UI text inputs"""
    try:
        from app.services.quality_metrics import quality_calculator
        
        # 1. Calculate SOAP Metrics (BLEU/CUDA)
        metrics = quality_calculator.calculate_all_metrics(
            reference_soap=input_data.reference_soap,
            hypothesis_soap=input_data.hypothesis_soap
        )
        
        # 2. Calculate Transcription Metrics (WER)
        transcription_metrics = None
        if input_data.reference_transcript and input_data.hypothesis_transcript:
            transcription_metrics = quality_calculator.calculate_wer(
                reference=input_data.reference_transcript,
                hypothesis=input_data.hypothesis_transcript
            )
            
        return {
            "metrics": metrics,
            "fields": metrics.get("fields", {}),
            "overall": metrics.get("overall", {}),
            "transcription": {
                **(transcription_metrics or {}),
                "bleu": quality_calculator.calculate_bleu(input_data.reference_transcript, input_data.hypothesis_transcript),
                "cuda": quality_calculator.calculate_cuda(input_data.reference_transcript, input_data.hypothesis_transcript)
            } if transcription_metrics else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_statistics():
    """Get system statistics"""
    with get_db() as db:
        all_calls = db.query(EmergencyCall).limit(1000).all()
        urgency_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        total_duration = 0
        
        for call in all_calls:
            if call.urgency_level:
                # Normalize MINIMAL -> LOW for UI stats
                normalized_level = normalize_urgency_for_ui(call.urgency_level)
                urgency_counts[normalized_level] = urgency_counts.get(normalized_level, 0) + 1
            if call.audio_duration:
                total_duration += call.audio_duration
        
        return {
            "total_calls": len(all_calls),
            "urgency_distribution": urgency_counts,
            "total_audio_duration": round(total_duration, 2),
            "average_duration": round(total_duration / len(all_calls), 2) if all_calls else 0
        }

@app.post("/api/import-test-data")
async def import_test_data():
    """Import test data from evaluated_text_data.py"""
    try:
        from data.text.evaluated_text_data import EVALUATED_CALLS
        
        with get_db() as db:
            count = 0
            for call_data in EVALUATED_CALLS:
                existing = db.query(EmergencyCall).filter(
                    EmergencyCall.call_id == call_data['call_id']
                ).first()
                
                if not existing:
                    new_call = EmergencyCall(
                        call_id=call_data['call_id'],
                        transcript=call_data['text'],
                        soap_subjective=call_data['expected_soap']['subjective'],
                        soap_objective=call_data['expected_soap']['objective'],
                        soap_assessment=call_data['expected_soap']['assessment'],
                        soap_plan=call_data['expected_soap']['plan'],
                        urgency_level=call_data.get('expected_urgency', 'MEDIUM').upper(),
                        patient_name=call_data.get('expected_agent', 'Unknown'),
                        disease=call_data.get('expected_type', 'Medical')
                    )
                    db.add(new_call)
                    count += 1
            
            db.commit()
        
        return {"message": f"Imported {count} calls", "success": True}
    except Exception as e:
        print(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.websocket("/ws/realtime-call")
async def websocket_endpoint(websocket: WebSocket):
    """
    IMPROVED WebSocket endpoint for real-time call processing
    """
    await websocket.accept()
    print("🔌 WebSocket connected")
    
    handler = None
    try:
        with get_db() as db:
            handler = RealtimeCallHandler(pipeline, db)
            
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                action = message.get("action")
                
                if action == "start":
                    language = message.get("language", "en")
                    call_id = await handler.start_call(language=language)
                    await websocket.send_json({
                        "status": "started",
                        "call_id": call_id,
                        "message": f"Recording started ({language}) - speak now!"
                    })
                    print(f"✅ Call started: {call_id} ({language})")
                
                elif action == "audio":
                    audio_data = message.get("data")
                    print(f"📥 Received audio chunk ({len(audio_data)} bytes)")
                    
                    result = await handler.process_audio_chunk(audio_data)
                    await websocket.send_json(result)
                    
                    if result.get("status") == "processing" and result.get("new_transcript"):
                        print(f"📝 New text: {result['new_transcript'][:50]}...")
                
                elif action == "end":
                    print("⏹️  End call requested")
                    result = await handler.end_call()
                    await websocket.send_json(result)
                    
                    if result.get("status") == "completed":
                        print(f"✅ Call completed: {result['call_id']}")
                        
                        # AUTO-SYNC: Sync to patient journey database
                        try:
                            from app.services.sync_helper import sync_emergency_call_to_patient_journey
                            from app.models.call import EmergencyCall
                            # We're already in a with get_db() block (line 553), but handler uses it
                            # We can reuse 'db' session variable from outer scope if accessible or just query safely
                            # Since we are inside 'with get_db() as db:', 'db' is available
                            
                            call_obj = db.query(EmergencyCall).filter(EmergencyCall.call_id == result['call_id']).first()
                            if call_obj:
                                # We need to close this transaction effectively or ensure it's committed before sync reads it?
                                # handler.end_call() likely commits.
                                # To be safe, we can trigger sync in a way that opens its own short lived session if needed, 
                                # but sync_helper opens its own 'with get_db()'.
                                # So passing the ID is fine.
                                sync_emergency_call_to_patient_journey(call_obj.id)
                                print(f"🔄 Auto-synced realtime call {result['call_id']} to patient journey")
                        except Exception as sync_error:
                            print(f"⚠️ Sync failed (non-blocking): {sync_error}")
                            
                    else:
                        print(f"⚠️  Call ended with status: {result.get('status')}")
                    
                    break
                
                elif action == "ping":
                    await websocket.send_json({"status": "pong"})
                
                else:
                    print(f"⚠️  Unknown action: {action}")
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Unknown action: {action}"
                    })
    
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected by client")
        if handler and handler.call_id:
            print(f"⚠️  Auto-saving call: {handler.call_id}")
            try:
                await handler.end_call()
            except Exception as e:
                print(f"❌ Auto-save failed: {e}")
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })
        except:
            pass
        
        try:
            await websocket.close()
        except:
            pass

# =====================================================
# PATIENT REGISTRATION ENDPOINTS
# =====================================================

from app.services.patient_service import (
    get_patient_db, create_patient, get_patient_by_id, 
    get_patient_by_name, search_patients, get_all_patients,
    update_patient, add_journey_event, delete_patient
)
from fastapi import Depends
from sqlalchemy.orm import Session

class PatientInput(BaseModel):
    patient_id: str = None
    name: str
    date_of_birth: str = None
    age: int = None
    sex: str = None
    blood_type: str = None
    phone: str = None
    street: str = None
    city: str = None
    postal_code: str = None
    primary_condition: str = None
    allergies: str = None
    medications: str = None
    medical_history: str = None
    follow_up_notes: str = None
    clinical_notes: str = None

class PatientUpdateInput(BaseModel):
    name: str = None
    age: int = None
    sex: str = None
    blood_type: str = None
    phone: str = None
    street: str = None
    city: str = None
    postal_code: str = None
    primary_condition: str = None
    allergies: str = None
    medications: str = None
    medical_history: str = None
    follow_up_notes: str = None
    clinical_notes: str = None
    journey_image_1: str = None
    journey_image_2: str = None
    journey_events: str = None

class JourneyEventInput(BaseModel):
    segment: int
    date: str
    time: str
    description: str
    status: str = "pending"

@app.post("/api/patients")
def create_new_patient(patient_data: PatientInput, db: Session = Depends(get_patient_db)):
    """Create a new registered patient"""
    try:
        # Generate patient ID if not provided
        if not patient_data.patient_id:
            import uuid
            patient_data.patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        
        # Check if patient already exists
        existing = get_patient_by_id(db, patient_data.patient_id)
        if existing:
            raise HTTPException(status_code=400, detail="Patient ID already exists")
        
        patient = create_patient(db, patient_data.dict())
        
        # Return full patient data for immediate UI update
        events = json.loads(patient.journey_events) if patient.journey_events else []
        return {
            "success": True,
            "patient_id": patient.patient_id,
            "patient": {
                "patient_id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "sex": patient.sex,
                "primary_condition": patient.primary_condition,
                "journey_events": events,
                "last_contact": patient.last_contact.isoformat() if patient.last_contact else None,
                "follow_up_notes": patient.follow_up_notes,
                "clinical_notes": patient.clinical_notes
            },
            "message": "Patient registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients")
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_patient_db)):
    """Get all registered patients"""
    patients = get_all_patients(db, skip, limit)
    
    patients_data = []
    for p in patients:
        events = json.loads(p.journey_events) if p.journey_events else []
        patients_data.append({
            "patient_id": p.patient_id,
            "name": p.name,
            "age": p.age,
            "sex": p.sex,
            "blood_type": p.blood_type,
            "phone": p.phone,
            "street": p.street,
            "city": p.city,
            "postal_code": p.postal_code,
            "primary_condition": p.primary_condition,
            "allergies": p.allergies,
            "medications": p.medications,
            "medical_history": p.medical_history,
            "journey_events": events,
            "journey_image_1": p.journey_image_1,
            "journey_image_2": p.journey_image_2,
            "last_contact": p.last_contact.isoformat() if p.last_contact else None,
            "next_followup": p.next_followup.isoformat() if p.next_followup else None,
            "follow_up_notes": p.follow_up_notes,
            "clinical_notes": p.clinical_notes,
            "registered_at": p.registered_at.isoformat() if p.registered_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        })
    
    return {
        "total": len(patients_data),
        "patients": patients_data
    }

@app.get("/api/patients/check")
def check_patient_exists(name: str, db: Session = Depends(get_patient_db)):
    """Check if patient exists in journey database"""
    from app.services.patient_service import get_patient_by_name
    import json
    
    patient = get_patient_by_name(db, name)
    if patient:
        try:
            events = json.loads(patient.journey_events) if patient.journey_events else []
            count = len(events)
        except:
            count = 0
        return {
            "exists": True,
            "patient_id": patient.patient_id,
            "event_count": count
        }
    return {"exists": False}

@app.get("/api/patients/search/by-info")
def search_patients_by_info(
    name: str = None, 
    phone: str = None, 
    db: Session = Depends(get_patient_db)
):
    """Search for patients by name or phone"""
    from app.services.patient_service import search_patients
    patients = search_patients(db, name, phone)
    
    return [
        {
            "patient_id": p.patient_id,
            "name": p.name,
            "primary_condition": p.primary_condition,
            "age": p.age
        } for p in patients
    ]

@app.get("/api/patients/{patient_id}")
def get_patient_details(patient_id: str, db: Session = Depends(get_patient_db)):
    """Get specific patient details"""
    patient = get_patient_by_id(db, patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    events = json.loads(patient.journey_events) if patient.journey_events else []
    
    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        "age": patient.age,
        "sex": patient.sex,
        "blood_type": patient.blood_type,
        "phone": patient.phone,
        "street": patient.street,
        "city": patient.city,
        "postal_code": patient.postal_code,
        "primary_condition": patient.primary_condition,
        "allergies": patient.allergies,
        "medications": patient.medications,
        "medical_history": patient.medical_history,
        "journey_events": events,
        "journey_image_1": patient.journey_image_1,
        "journey_image_2": patient.journey_image_2,
        "last_contact": patient.last_contact.isoformat() if patient.last_contact else None,
        "next_followup": patient.next_followup.isoformat() if patient.next_followup else None,
        "follow_up_notes": patient.follow_up_notes,
        "clinical_notes": patient.clinical_notes,
        "registered_at": patient.registered_at.isoformat() if patient.registered_at else None,
        "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
    }


@app.put("/api/patients/{patient_id}")
def update_patient_endpoint(
    patient_id: str, 
    update_data: PatientUpdateInput,
    db: Session = Depends(get_patient_db)
):
    """Update patient information"""
    # Filter out None values
    data_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    updated_patient = update_patient(db, patient_id, data_dict)
    
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "success": True,
        "patient_id": updated_patient.patient_id,
        "message": "Patient updated successfully"
    }

@app.post("/api/patients/{patient_id}/journey-events")
def add_patient_journey_event(
    patient_id: str,
    event: JourneyEventInput,
    db: Session = Depends(get_patient_db)
):
    """Add a journey event to patient timeline"""
    event_dict = event.dict()
    
    updated_patient = add_journey_event(db, patient_id, event_dict)
    
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "success": True,
        "patient_id": updated_patient.patient_id,
        "message": "Journey event added successfully"
    }

@app.post("/api/patients/{patient_id}/generate-journey-images")
async def generate_journey_images_endpoint(patient_id: str, db: Session = Depends(get_patient_db)):
    """Generate AI journey visualization images for a patient"""
    from app.services.patient_service import get_patient_by_id
    from app.services.journey_image_generator import journey_image_generator
    import json as json_lib
    
    patient = get_patient_by_id(db, patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get patient journey events
    events = json_lib.loads(patient.journey_events) if patient.journey_events else []
    
    # Prepare patient data for generator
    patient_data = {
        "name": patient.name,
        "primary_condition": patient.primary_condition,
        "journey_events": events,
        "age": patient.age,
        "medical_history": patient.medical_history
    }
    
    try:
        # Generate images using JourneyImageGenerator
        result = journey_image_generator.generate_journey_images(patient_data)
        
        if result.get('image1') or result.get('image2'):
            return {
                "success": True,
                "patient_id": patient_id,
                "image1": result.get('image1'),
                "image2": result.get('image2'),
                "prompt1": result.get('prompt1'),
                "prompt2": result.get('prompt2'),
                "message": "Journey images generated successfully"
            }
        else:
            return {
                "success": False,
                "patient_id": patient_id,
                "error": result.get('error', 'Unknown error during generation'),
                "message": "Image generation failed or returned no data"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/api/patients/import-from-emergency-calls")
async def import_from_emergency_calls(db: Session = Depends(get_patient_db)):
    """Import emergency call patients into registered patient database"""
    from app.services.patient_service import create_patient, get_patient_by_name
    from app.services.database import get_db as get_emergency_db
    from app.models.call import EmergencyCall
    import uuid
    
    try:
        imported_count = 0
        skipped_count = 0
        
        # Get emergency calls
        with get_emergency_db() as emergency_db:
            calls = emergency_db.query(EmergencyCall).filter(
                EmergencyCall.patient_name.isnot(None),
                EmergencyCall.patient_name != ''
            ).all()
            
            for call in calls:
                # Check if patient already exists
                existing = get_patient_by_name(db, call.patient_name)
                
                # New event data
                new_event = {
                    'date': call.created_at.strftime('%Y-%m-%d'),
                    'time': call.created_at.strftime('%H:%M'),
                    'description': f"Emergency call: {call.disease or 'Medical emergency'}",
                    'status': 'completed'
                }

                if existing:
                    # Append event to existing patient
                    # Check if this event (by date/time/desc) already exists to avoid duplicates
                    events = json.loads(existing.journey_events) if existing.journey_events else []
                    
                    is_duplicate = any(
                        e.get('date') == new_event['date'] and 
                        e.get('time') == new_event['time'] 
                        for e in events
                    )
                    
                    # Update the call with patient_id (Link the databases)
                    if not call.patient_id:
                        call.patient_id = existing.patient_id
                        emergency_db.add(call) # Mark as modified
                    
                    if not is_duplicate:
                        new_event['segment'] = len(events) + 1
                        events.append(new_event)
                        # Sort and re-index
                        events.sort(key=lambda x: f"{x['date']} {x['time']}")
                        for i, e in enumerate(events):
                            e['segment'] = i + 1
                        
                        existing.journey_events = json.dumps(events)
                        existing.updated_at = datetime.utcnow()
                        db.commit()
                        imported_count += 1
                    else:
                        skipped_count += 1
                    continue
                
                # Create new registered patient from emergency call
                new_event['segment'] = 1
                new_patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
                
                patient_data = {
                    'patient_id': new_patient_id,
                    'name': call.patient_name,
                    'primary_condition': call.disease or 'Emergency',
                    'medical_history': f"Emergency call on {call.created_at.strftime('%Y-%m-%d')}: {call.soap_subjective or ''}",
                    'clinical_notes': call.soap_assessment or '',
                    'follow_up_notes': call.soap_plan or '',
                    'journey_events': json.dumps([new_event])
                }
                
                create_patient(db, patient_data)
                
                # Link back to emergency call
                call.patient_id = new_patient_id
                emergency_db.add(call)
                
                imported_count += 1
            
            # Commit changes to emergency calls DB
            emergency_db.commit()
            
        return {
            "success": True,
            "imported": imported_count,
            "skipped": skipped_count,
            "message": f"Processed {imported_count + skipped_count} calls: {imported_count} imported/updated, {skipped_count} skipped (duplicates)."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Import from emergency calls failed: {str(e)}")

@app.delete("/api/patients/clear-all")
def clear_all_patients(db: Session = Depends(get_patient_db)):
    """Delete all patients from Patient Journey database"""
    try:
        from app.models.patient import RegisteredPatient
        deleted_count = db.query(RegisteredPatient).delete()
        db.commit()
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} patients",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/patients/{patient_id}")
def delete_patient_endpoint(patient_id: str, db: Session = Depends(get_patient_db)):
    """Delete a patient"""
    success = delete_patient(db, patient_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "success": True,
        "message": "Patient deleted successfully"
    }



@app.delete("/api/calls/clear")
def clear_all_calls():
    """Delete all calls from database"""
    try:
        with get_db() as db:
            deleted_count = db.query(EmergencyCall).delete()
            db.commit()
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} calls",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)