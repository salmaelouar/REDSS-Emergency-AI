"""
SOAP Extraction Service - OpenAI Version
"""
import os # is used to access environment variables
from openai import OpenAI # is used to access the OpenAI API
from dotenv import load_dotenv # is used to load environment variables from a .env file

load_dotenv() # is used to load environment variables from a .env file

class SOAPExtractor:
    """Extract SOAP notes using OpenAI GPT"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY") 
        if not api_key or api_key.startswith("sk-your"):
            raise ValueError("Please set OPENAI_API_KEY in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))
        
        print(f"✓ SOAP Extractor initialized (OpenAI {self.model})")
    
    def extract(self, transcript: str, target_language: str = "en") -> dict:
        print(f"Extracting SOAP notes (Target Language: {target_language})...")
        
        is_japanese = target_language in ["ja", "jp", "japanese"]
        lang_name = "JAPANESE" if is_japanese else "ENGLISH"
        
        # Define labels and missing data terms based on language
        if is_japanese:
            missing_term = "[不明]"
            labels = """氏名: [不明]
年齢: [不明]
住所: [不明]
電話: [不明]
血液型: [不明]"""
            strict_instruction = """
CRITICAL: You MUST use ONLY JAPANESE. NO ENGLISH words or labels allowed.
- Use 氏名: NOT Name:
- Use 年齢: NOT Age:
- Use 住所: NOT Address:
- Use 電話: NOT Phone:
- Use 血液型: NOT Blood:"""
            extraction_guidance = """
重要: 会話から情報を積極的に抽出してください:
- 年齢: 「60歳」「還暦」「六十代」などの表現を探す
- 住所: 通り名、番地、建物名、地区名を探す
- 電話: 電話番号のパターン
もし会話で言及されていれば、[不明]を実際の値に置き換えてください。"""
        else:
            missing_term = "[Not provided]"
            labels = """Name: [Not provided]
Age: [Not provided]
Address: [Not provided]
Phone: [Not provided]
Blood: [Not provided]"""
            strict_instruction = """
CRITICAL: You MUST use ONLY ENGLISH. NO Japanese characters or labels allowed.
- Use Name: NOT 氏名:
- Use Age: NOT 年齢:
- Use Address: NOT 住所:
- Use Phone: NOT 電話:
- Use Blood: NOT 血液型:"""
            extraction_guidance = """
IMPORTANT: Actively extract information from the conversation:
- Age: Look for "60 years old", "sixty", "in his sixties", age numbers
- Address: Look for street names, numbers, building names, district/area
- Phone: Look for phone number patterns
- Name: Look for "my name is", "this is", person references
If mentioned in the conversation, replace [Not provided] with actual values."""

        prompt = f"""You are an expert emergency medical dispatcher assistant. 
Analyze this 911 call transcript and extract clinical SOAP notes in {lang_name}.

{strict_instruction}

{extraction_guidance}

IMPORTANT: Everything - every single word, label, and description - must be in {lang_name}.
If any piece of information is missing, you MUST use exactly "{missing_term}".

In the OBJECTIVE (O) section, you MUST format the patient details using these exact labels:
{labels}
 
 EXTREMELY IMPORTANT - NONSENSE/TESTING DETECTION:
 - If the transcript is nonsense (e.g., "fbydfgjnxfkmxk", "testing", "blah blah", "ghjkl") or completely unrelated to a medical emergency, you MUST NOT generate a medical plan.
 - In such cases:
   S: [Testing/Nonsense detected]
   O: [Labels as above with {missing_term}]
   A: [No medical emergency detected / Non-medical input]
   P: [No action needed / Non-medical input]
 
 EXTRACT PATIENT INFO CAREFULLY:
 - Listen for age mentions (numbers, "years old", approximate age)
 - Listen for location/address details (street names, building numbers, districts)
 - Listen for phone numbers or callback numbers
 - Listen for patient names or references
 
 If you find the information in the transcript, replace {missing_term} with the actual data, but keep the labels in {lang_name}.
 
 TRANSCRIPT:
 {transcript}
 
 Extract and format as SOAP notes in {lang_name}:
 S: [Subjective - all in {lang_name}]
 O: [Objective with strictly {lang_name} labels as shown above - extract age, address if mentioned]
 A: [Assessment - all in {lang_name}]
 P: [Plan - all in {lang_name}]
 
 Remember: ABSOLUTELY NO mixing of languages. Use ONLY {lang_name} throughout.
 If patient says age or address, PUT IT IN THE OBJECTIVE SECTION with proper labels!
 """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert emergency medical dispatcher. You ONLY write in {lang_name}. Never mix languages. You are excellent at extracting patient demographics from natural conversation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            soap = self._parse_soap_response(content)
            
            print(f"✓ SOAP extraction complete")
            return soap
            
        except Exception as e:
            print(f"✗ SOAP extraction failed: {e}")
            return {
                "subjective": "Extraction failed",
                "objective": "Extraction failed",
                "assessment": "Extraction failed",
                "plan": "Extraction failed"
            }
    
    def _parse_soap_response(self, content: str) -> dict:
        soap = {
            "subjective": "",
            "objective": "",
            "assessment": "",
            "plan": ""
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('S:') or line.startswith('SUBJECTIVE'):
                current_section = 'subjective'
                line = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.startswith('O:') or line.startswith('OBJECTIVE'):
                current_section = 'objective'
                line = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.startswith('A:') or line.startswith('ASSESSMENT'):
                current_section = 'assessment'
                line = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.startswith('P:') or line.startswith('PLAN'):
                current_section = 'plan'
                line = line.split(':', 1)[1].strip() if ':' in line else ''
            
            if current_section and line:
                if soap[current_section]:
                    soap[current_section] += "\n" + line
                else:
                    soap[current_section] = line
        
        return soap

    def translate_text(self, text: str, target_language: str) -> str:
        """Simple translation helper"""
        if not text or len(text.strip()) < 2:
            return text
            
        is_japanese = target_language in ["ja", "jp", "japanese"]
        lang_name = "JAPANESE" if is_japanese else "ENGLISH"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a professional medical translator. Translate the text to {lang_name}."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Translation failed: {e}")
            return text

    def localize_call_data(self, transcript: str, soap_notes: dict, metadata: dict, target_language: str) -> dict:
        """
        MASSIVE PERFORMANCE IMPROVEMENT:
        Consolidate all translation and localization tasks into ONE single AI call.
        Translates transcript, re-localizes SOAP labels, and translates metadata.
        """
        import json
        
        is_japanese = target_language in ["ja", "jp", "japanese"]
        lang_name = "JAPANESE" if is_japanese else "ENGLISH"
        
        # Language-specific labels for SOAP Objective section
        if is_japanese:
            labels = "氏名:, 年齢:, 住所:, 電話:, 血液型:"
            missing = "[不明]"
        else:
            labels = "Name:, Age:, Address:, Phone:, Blood:"
            missing = "[Not provided]"

        prompt = f"""You are a medical localization expert. 
Localize the following emergency call data into {lang_name}.

TASK:
1. Translate the transcript accurately.
2. Translate the SOAP notes (Subjective, Objective, Assessment, Plan).
3. EXTREMELY IMPORTANT: In the Objective section, you MUST use these exact labels: {labels}.
4. Translate metadata fields (Reasoning, Patient Name, Doctor Name, Disease).
5. If information is missing, use "{missing}".
6. Return ONLY a JSON object.

INPUT DATA:
{{
  "transcript": {json.dumps(transcript)},
  "soap": {json.dumps(soap_notes)},
  "metadata": {json.dumps(metadata)}
}}

OUTPUT FORMAT (Strictly JSON):
{{
  "transcript": "...",
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "...",
  "reasoning": "...",
  "patient_name": "...",
  "doctor_name": "...",
  "disease": "..."
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a medical translation API. Respond ONLY with valid JSON in {lang_name}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"✓ Consolidated translation to {lang_name} complete")
            return result
        except Exception as e:
            print(f"Consolidated localization failed: {e}")
            # Return original data if failed
            return {
                "transcript": transcript,
                "subjective": soap_notes.get('subjective', ''),
                "objective": soap_notes.get('objective', ''),
                "assessment": soap_notes.get('assessment', ''),
                "plan": soap_notes.get('plan', ''),
                "reasoning": metadata.get('reasoning', ''),
                "patient_name": metadata.get('patient_name', ''),
                "doctor_name": metadata.get('doctor_name', ''),
                "disease": metadata.get('disease', '')
            }

    def translate_batch(self, texts: list, target_language: str) -> list:
        """Translate multiple snippets in one call to save time/cost"""
        if not texts: return []
        
        # Filter out empty or N/A strings but keep indices
        to_translate = []
        indices = []
        for i, t in enumerate(texts):
            if t and len(t.strip()) > 1 and t.lower() != "n/a" and t.lower() != "unassigned":
                to_translate.append(t)
                indices.append(i)
        
        if not to_translate:
            return texts

        is_japanese = target_language in ["ja", "jp", "japanese"]
        lang_name = "JAPANESE" if is_japanese else "ENGLISH"
        
        try:
            # Create a structured prompt
            delimiter = "|||"
            input_text = delimiter.join(to_translate)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a medical translator. Translate each section separated by '{delimiter}' into {lang_name}. Return the translations separated by EXACTLY the same delimiter '{delimiter}'. Do not add numbering or extra text."},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.1
            )
            
            results = response.choices[0].message.content.strip().split(delimiter)
            
            # Map back to original list
            final_list = list(texts)
            for j, res in enumerate(results):
                if j < len(indices) and j < len(results):
                    final_list[indices[j]] = res.strip()
            
            return final_list
        except Exception as e:
            print(f"Batch translation failed: {e}")
            return texts

soap_extractor = SOAPExtractor()
