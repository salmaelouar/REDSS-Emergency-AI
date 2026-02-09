"""
Evidence-Based Emergency Urgency Classifier
Hybrid approach combining:
1. Emergency Severity Index (ESI) Version 5 - Rule-based clinical criteria
2. AI-Enhanced Analysis - Context-aware classification

Scientific References:
- Gilboy et al. (2020). Emergency Severity Index Implementation Handbook v5
- Emergency Nurses Association (2023). ESI Handbook Fifth Edition  
- Farrohknia et al. (2011). Emergency Department Triage Scales: Systematic Review
- Hinson et al. (2019). Triage Performance in Emergency Medicine
- AHRQ Healthcare Research & Quality ESI Algorithm

Validation: 94% of U.S. EDs use ESI (Worth et al., 2019)
Reliability: κ = 0.7-0.95 for CTAS/ESI (systematic reviews)
"""

import os # standard library for interacting with the operating system
from openai import OpenAI # openai python library
from dotenv import load_dotenv # load environment variables from a .env file
import re #regular expressions TO CLEAN THE TEXT

load_dotenv() # load environment variables from a .env file1

class HybridUrgencyClassifier:
    """
    Hybrid Emergency Triage Classifier
    Combines ESI Version 5 clinical criteria with AI contextual analysis
    """
    
    # ESI Level 1: Immediate lifesaving intervention required (Decision Point A)
    LEVEL_1_CRITERIA = {
        'airway_compromise': [
            'intubated', 'unresponsive', 'severe respiratory distress',
            'apneic', 'not breathing', 'stopped breathing', 'no airway'
        ],
        'circulation_compromise': [
            'pulseless', 'cardiac arrest', 'no pulse', 'heart stopped',
            'profound hypotension', 'severe shock', 'code blue'
        ],
        'neurological': [
            'unconscious', 'unresponsive', 'gcs < 8', 'non-verbal',
            'requires noxious stimulus', 'comatose', 'obtunded'
        ],
        'critical_presentations': [
            'anaphylaxis', 'severe anaphylactic', 'flaccid infant',
            'spo2 < 90', 'oxygen saturation below 90',
            'penetrating trauma head', 'penetrating trauma neck', 
            'penetrating trauma chest', 'gunshot wound torso'
        ]
    }
    
    # ESI Level 2: High-risk situation likely to deteriorate (Decision Point B)
    LEVEL_2_CRITERIA = {
        'cardiovascular': [
            'chest pain', 'acute coronary syndrome', 'heart attack',
            'active chest pain', 'crushing chest pain', 'stemi',
            'difficulty breathing cardiac', 'hypoperfusion'
        ],
        'neurological': [
            'stroke', 'cva', 'acute confusion', 'altered mental status',
            'thunderclap headache', 'worst headache of life',
            'headache with neck stiffness', 'post-ictal', 'seizure just had'
        ],
        'respiratory': [
            'respiratory distress', 'severe shortness of breath',
            'wheezing severe', 'stridor', 'tripoding',
            'speaking in short sentences', 'increased work of breathing'
        ],
        'obstetric': [
            'ectopic pregnancy', 'vaginal bleeding pregnant',
            'postpartum hemorrhage', 'pregnant with severe pain',
            'eclampsia', 'preeclampsia severe'
        ],
        'infectious': [
            'immunocompromised with fever', 'chemotherapy with fever',
            'transplant with fever', 'sepsis', 'septic shock',
            'meningitis', 'neutropenic fever'
        ],
        'trauma': [
            'fall greater than 20 feet', 'ejected from vehicle',
            'high speed collision', 'pedestrian struck',
            'neurovascular compromise', 'compartment syndrome'
        ],
        'severe_pain_distress': [
            'renal colic', 'kidney stone severe', 'sickle cell crisis',
            'suicidal', 'homicidal', 'acute psychosis',
            'violent', 'threat to self or others'
        ],
        'time_sensitive': [
            'testicular torsion', 'ovarian torsion', 
            'button battery ingestion', 'caustic ingestion',
            'acute vision loss', 'retinal detachment'
        ]
    }
    
    # ESI Level 3: Stable but needs multiple resources (Decision Point C: ≥2 resources)
    LEVEL_3_CRITERIA = {
        'abdominal_gi': [
            'abdominal pain moderate', 'belly pain', 'stomach pain',
            'nausea and vomiting', 'vomiting multiple times', 'diarrhea severe',
            'constipation severe', 'rectal bleeding', 'blood in stool',
            'gi bleed stable'
        ],
        'genitourinary': [
            'flank pain', 'kidney pain', 'urinary symptoms complex',
            'hematuria', 'blood in urine', 'urinary retention',
            'vaginal bleeding non-pregnant', 'pelvic pain moderate',
            'testicular pain non-acute', 'dysuria with fever'
        ],
        'musculoskeletal': [
            'back pain moderate', 'joint pain severe', 'extremity pain',
            'possible fracture', 'injury needs imaging', 'neck pain trauma',
            'limb swelling', 'joint swelling significant'
        ],
        'dermatologic': [
            'cellulitis', 'abscess needs drainage', 'wound infection',
            'rash with fever', 'allergic reaction moderate', 'bite infected',
            'burn partial thickness'
        ],
        'general': [
            'dehydration moderate', 'weakness generalized', 'dizziness recurrent',
            'fever with symptoms', 'chills and fever', 'malaise significant',
            'multiple complaints', 'fall with injury', 'syncope resolved'
        ],
        'infectious': [
            'flu-like symptoms severe', 'upper respiratory infection severe',
            'pneumonia suspected', 'bronchitis severe', 'infection systemic'
        ],
        'metabolic': [
            'hyperglycemia symptomatic', 'hypoglycemia resolved',
            'electrolyte imbalance suspected', 'diabetic not in crisis'
        ]
    }
    
    # ESI Level 4: One resource needed (Decision Point C: 1 resource)
    LEVEL_4_CRITERIA = {
        'minor_injuries': [
            'laceration simple', 'cut needs stitches', 'small wound',
            'sprain ankle', 'sprain wrist', 'minor strain',
            'bruise', 'contusion', 'minor trauma',
            'finger injury', 'toe injury', 'minor burn',
            'sunburn', 'first degree burn', 'abrasion'
        ],
        'simple_infections': [
            'uti simple', 'urinary tract infection', 'bladder infection',
            'ear infection', 'otitis', 'pharyngitis', 'strep throat suspected',
            'conjunctivitis', 'pink eye', 'simple skin infection',
            'folliculitis', 'minor abscess'
        ],
        'minor_symptoms': [
            'cough mild', 'cold symptoms', 'sore throat mild',
            'nasal congestion', 'minor headache', 'migraine stable',
            'back pain chronic stable', 'minor rash',
            'allergic reaction mild', 'insect bite minor',
            'minor pain', 'dental pain non-severe'
        ],
        'procedures': [
            'suture removal', 'dressing change', 'wound check',
            'splint check', 'cast check', 'foreign body simple',
            'simple procedure needed'
        ]
    }
    
    # ESI Level 5: No resources needed (Decision Point C: 0 resources)
    LEVEL_5_CRITERIA = {
        'administrative': [
            'prescription refill', 'med refill', 'medication renewal',
            'work excuse', 'work note', 'sick note', 'medical certificate',
            'form completion', 'disability paperwork', 'fmla paperwork'
        ],
        'chronic_stable': [
            'chronic condition stable', 'routine follow up', 'recheck stable',
            'blood pressure check', 'bp check only', 'glucose check',
            'weight check', 'vital signs only', 'no acute symptoms'
        ],
        'information': [
            'medical advice', 'health question', 'test results discussion',
            'lab results check', 'second opinion stable',
            'education', 'counseling', 'prevention counseling'
        ],
        'resolved': [
            'symptoms resolved', 'feeling better', 'improved',
            'just checking', 'reassurance only', 'no longer having symptoms'
        ]
    }
    
    # Japanese ESI Level 1 Criteria (Immediate Life Threat)
    JA_LEVEL_1_CRITERIA = {
        'airway_compromise': [
            '挿管', '呼吸していない', '反応がない', '重度の呼吸困難', 
            '無呼吸', '息をしていない', '気道閉塞', '窒息'
        ],
        'circulation_compromise': [
            '脈がない', '心停止', '心臓が止まった', '脈拍なし', 
            '重度のショック', 'コードブルー', '血圧低下'
        ],
        'neurological': [
            '意識不明', '意識がない', '反応しない', '呼びかけに反応しない', 
            '昏睡', '意識レベル低下', 'JCS 3桁'
        ],
        'critical_presentations': [
            'アナフィラキシー', 'ショック状態', '酸素飽和度90以下', 
            'SpO2低下', '銃傷', '刺傷', '大量出血'
        ]
    }
    
    # Japanese ESI Level 2 Criteria (High Risk / Emergency)
    JA_LEVEL_2_CRITERIA = {
        'cardiovascular': [
            '胸の痛み', '胸痛', '心筋梗塞', '狭心症', 
            '胸が締め付けられる', '冷や汗', '心不全', '不整脈'
        ],
        'neurological': [
            '脳卒中', '麻痺', 'ろれつが回らない', '激しい頭痛', 
            '今までにない頭痛', '雷鳴頭痛', '痙攣', 'けいれん', '意識障害'
        ],
        'respiratory': [
            '呼吸困難', '息苦しい', '喘鳴', 'ゼーゼーする', 
            '肩で息をしている', 'チアノーゼ', '顔色が悪い'
        ],
        'obstetric': [
            '子宮外妊娠', '妊娠中の出血', '分娩', '陣痛', 
            '破水', '妊娠中の激痛', '胎動減少'
        ],
        'infectious': [
            '敗血症', '高熱と悪寒', '免疫不全', '化学療法中の発熱', 
            '髄膜炎', '首が硬い'
        ],
        'trauma': [
            '交通事故', '高所転落', '骨折', '切断', 
            '激しい打撲', 'コンパートメント症候群'
        ],
        'severe_pain_distress': [
            '尿管結石', '激痛', '七転八倒', '自殺企図', 
            '錯乱', '暴れている', '危害を加える恐れ'
        ],
        'time_sensitive': [
            '睾丸捻転', '急激な視力低下', '網膜剥離', 
            '異物誤飲', '電池誤飲'
        ]
    }
    
    # Japanese ESI Level 3: 安定しているが複数のリソースが必要
    JA_LEVEL_3_CRITERIA = {
        'abdominal_gi': [
            '中等度の腹痛', '腹痛', '胃痛',
            '吐き気と嘔吐', '複数回の嘔吐', '重度の下痢',
            '重度の便秘', '直腸出血', '便に血が混じる',
            '安定した消化管出血'
        ],
        'genitourinary': [
            '側腹部痛', '腎臓痛', '複雑な泌尿器症状',
            '血尿', '尿に血が混じる', '尿閉',
            '非妊娠時の膣出血', '中等度の骨盤痛',
            '非急性の精巣痛', '発熱を伴う排尿痛'
        ],
        'musculoskeletal': [
            '中等度の腰痛', '重度の関節痛', '四肢の痛み',
            '骨折の可能性', '画像診断が必要な外傷', '外傷性頸部痛',
            '四肢の腫脹', '著明な関節腫脹'
        ],
        'dermatologic': [
            '蜂窩織炎', '排膿が必要な膿瘍', '創傷感染',
            '発熱を伴う発疹', '中等度のアレルギー反応', '感染した咬傷',
            '部分層熱傷'
        ],
        'general': [
            '中等度の脱水', '全身性の脱力感', '反復性のめまい',
            '症状を伴う発熱', '悪寒と発熱', '著明な倦怠感',
            '複数の訴え', '外傷を伴う転倒', '回復した失神'
        ],
        'infectious': [
            '重度のインフルエンザ様症状', '重度の上気道感染',
            '肺炎の疑い', '重度の気管支炎', '全身性感染症'
        ],
        'metabolic': [
            '症状のある高血糖', '回復した低血糖',
            '電解質異常の疑い', 'クリーゼではない糖尿病'
        ]
    }
    
    # Japanese ESI Level 4: 1つのリソースが必要
    JA_LEVEL_4_CRITERIA = {
        'minor_injuries': [
            '単純な裂傷', '縫合が必要な切り傷', '小さな創傷',
            '足首の捻挫', '手首の捻挫', '軽度の挫傷',
            '打撲', '挫傷', '軽度の外傷',
            '指の外傷', '足指の外傷', '軽度の熱傷',
            '日焼け', '第一度熱傷', '擦過傷'
        ],
        'simple_infections': [
            '単純な尿路感染症', '尿路感染症', '膀胱炎',
            '耳感染症', '中耳炎', '咽頭炎', '溶連菌感染症の疑い',
            '結膜炎', '結膜充血', '単純な皮膚感染症',
            '毛嚢炎', '軽度の膿瘍'
        ],
        'minor_symptoms': [
            '軽度の咳', '風邪症状', '軽度の喉の痛み',
            '鼻づまり', '軽度の頭痛', '安定した片頭痛',
            '安定した慢性腰痛', '軽度の発疹',
            '軽度のアレルギー反応', '軽度の虫刺され',
            '軽度の痛み', '非重度の歯痛'
        ],
        'procedures': [
            '抜糸', 'ドレッシング交換', '創傷確認',
            '副子確認', 'ギプス確認', '単純な異物',
            '単純な処置が必要'
        ]
    }
    
    # Japanese ESI Level 5: リソース不要
    JA_LEVEL_5_CRITERIA = {
        'administrative': [
            '処方箋の更新', '薬の補充', '薬の更新',
            '診断書', '勤務証明書', '病欠証明', '医療証明書',
            'フォーム記入', '障害関連書類', 'FMLA書類'
        ],
        'chronic_stable': [
            '安定した慢性疾患', '定期フォローアップ', '安定した再診',
            '血圧測定', '血圧チェックのみ', '血糖測定',
            '体重測定', 'バイタルサインのみ', '急性症状なし'
        ],
        'information': [
            '医療相談', '健康相談', '検査結果の説明',
            '検査結果確認', '安定した状態でのセカンドオピニオン',
            '教育', 'カウンセリング', '予防カウンセリング'
        ],
        'resolved': [
            '症状が回復した', '気分が良くなった', '改善した',
            '確認のため', '安心のため', 'もはや症状がない'
        ]
    }
    
    # Vital sign thresholds (ESI Algorithm Decision Point D)
    VITAL_SIGN_THRESHOLDS = {
        'adult': {
            'heart_rate_max': 100,
            'respiratory_rate_max': 20,
            'spo2_min': 92
        },
        'pediatric': {
            'infant': {'hr_max': 180, 'rr_max': 55},      # < 1 year
            'toddler': {'hr_max': 140, 'rr_max': 40},     # 1-3 years
            'child': {'hr_max': 120, 'rr_max': 30},       # 3-12 years
            'adolescent': {'hr_max': 100, 'rr_max': 20}   # 12-18 years
        }
    }
    
    def __init__(self):
        """Initialize hybrid classifier with AI capabilities"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-your"):
            raise ValueError("Please set OPENAI_API_KEY in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))
        
        print(f"✓ Hybrid Urgency Classifier initialized (ESI v5 + AI {self.model})")
    
    def classify(self, transcript: str, soap: dict, language: str = "en") -> dict:
        """
        Main classification method using hybrid approach
        
        1. Apply ESI clinical criteria (evidence-based)
        2. Enhance with AI contextual analysis
        3. Return most appropriate urgency level
        
        Args:
            transcript: Emergency call transcription
            soap: Structured SOAP notes
            language: Language code (en/ja)
            
        Returns:
            dict with level, score, reasoning, esi_rationale
        """
        print(f"🏥 Classifying urgency (ESI v5 + AI) - Language: {language}")
        
        # Step 1: Extract clinical information
        clinical_data = self._extract_clinical_data(transcript, soap)
        
        # Step 2: Apply ESI rule-based criteria
        esi_result = self._apply_esi_criteria(clinical_data, language)
        
        # Step 3: Get AI contextual analysis
        ai_result = self._ai_classification(transcript, soap, language)
        
        # Step 4: Combine results (safety-first approach)
        final_result = self._hybrid_decision(esi_result, ai_result, language)
        
        print(f"✓ Final urgency: {final_result['level']} (ESI: {esi_result['esi_level']}, AI: {ai_result['level']})")
        
        return final_result
    
    def _extract_clinical_data(self, transcript: str, soap: dict) -> dict:
        """Extract clinical information from transcript and SOAP notes"""
        text = transcript.lower()
        
        # Extract vital signs if mentioned
        vitals = {}
        
        # Heart rate
        hr_match = re.search(r'heart rate[:\s]+(\d+)', text)
        if hr_match:
            vitals['heart_rate'] = int(hr_match.group(1))
        
        # Respiratory rate
        rr_match = re.search(r'respiratory rate[:\s]+(\d+)', text)
        if rr_match:
            vitals['respiratory_rate'] = int(rr_match.group(1))
        
        # SpO2
        spo2_match = re.search(r'(?:oxygen|spo2|o2 sat)[:\s]+(\d+)', text)
        if spo2_match:
            vitals['spo2'] = int(spo2_match.group(1))
        
        # Pain score
        pain_match = re.search(r'pain[:\s]+(\d+)(?:/10)?', text)
        pain_score = int(pain_match.group(1)) if pain_match else None
        
        return {
            'chief_complaint': soap.get('subjective', transcript),
            'presentation': transcript,
            'vitals': vitals,
            'pain_score': pain_score,
            'soap': soap
        }
    
    def _apply_esi_criteria(self, clinical_data: dict, language: str) -> dict:
        """
        Apply ESI Version 5 Decision Points
        
        Decision Point A: Requires immediate lifesaving intervention?
        Decision Point B: High-risk situation?
        Decision Point C/D: Resources + Vital signs
        """
        
        text = clinical_data['presentation'].lower()
        
        # Decision Point A: ESI Level 1
        level_1_check = self._check_esi_level_1(text, clinical_data, language)
        if level_1_check['is_level_1']:
            return {
                'esi_level': 1,
                'urgency': 'CRITICAL',
                'rationale': level_1_check['rationale'],
                'time_to_physician': 'Immediate (0 minutes)',
                'method': 'ESI Decision Point A'
            }
        
        # Decision Point B: ESI Level 2
        level_2_check = self._check_esi_level_2(text, clinical_data, language)
        if level_2_check['is_level_2']:
            return {
                'esi_level': 2,
                'urgency': 'HIGH',
                'rationale': level_2_check['rationale'],
                'time_to_physician': 'Within 10 minutes',
                'method': 'ESI Decision Point B'
            }
        
        # Decision Points C & D: Resource-based classification
        # Check ESI Level 5 first (no resources)
        level_5_check = self._check_esi_level_5(text, clinical_data, language)
        if level_5_check['is_level_5']:
            return {
                'esi_level': 5,
                'urgency': 'MINIMAL',
                'rationale': level_5_check['rationale'],
                'time_to_physician': 'As needed',
                'method': 'ESI Decision Point C (0 resources)'
            }
        
        # Check ESI Level 4 (one resource)
        level_4_check = self._check_esi_level_4(text, clinical_data, language)
        if level_4_check['is_level_4']:
            return {
                'esi_level': 4,
                'urgency': 'LOW',
                'rationale': level_4_check['rationale'],
                'time_to_physician': 'Within 1-2 hours',
                'method': 'ESI Decision Point C (1 resource)'
            }
        
        # Check ESI Level 3 (multiple resources)
        level_3_check = self._check_esi_level_3(text, clinical_data, language)
        if level_3_check['is_level_3']:
            return {
                'esi_level': 3,
                'urgency': 'MEDIUM',
                'rationale': level_3_check['rationale'],
                'time_to_physician': 'Within 30 minutes',
                'method': 'ESI Decision Point C (≥2 resources)'
            }
        
        # Default to MEDIUM for unclear cases (will be refined by AI)
        return {
            'esi_level': 3,
            'urgency': 'MEDIUM',
            'rationale': 'Standard evaluation needed - ESI Level 3 baseline',
            'time_to_physician': 'Within 30 minutes',
            'method': 'ESI Decision Point C (baseline)'
        }
    
    def _check_esi_level_1(self, text: str, clinical_data: dict, language: str) -> dict:
        """Decision Point A: Immediate lifesaving intervention required?"""
        
        criteria_to_check = self.LEVEL_1_CRITERIA
        if language in ['ja', 'jp', 'japanese']:
            criteria_to_check = self.JA_LEVEL_1_CRITERIA
        
        for category, criteria_list in criteria_to_check.items():
            for criterion in criteria_list:
                if criterion in text:
                    return {
                        'is_level_1': True,
                        'rationale': f'ESI Level 1: {criterion} detected ({category})'
                    }
        
        # Check critical vital signs
        vitals = clinical_data.get('vitals', {})
        if vitals.get('spo2') and vitals['spo2'] < 90:
            return {
                'is_level_1': True,
                'rationale': 'ESI Level 1: SpO2 < 90% (critical hypoxemia)'
            }
        
        return {'is_level_1': False, 'rationale': None}
    
    def _check_esi_level_2(self, text: str, clinical_data: dict, language: str) -> dict:
        """Decision Point B: High-risk situation?"""
        
        criteria_to_check = self.LEVEL_2_CRITERIA
        if language in ['ja', 'jp', 'japanese']:
            criteria_to_check = self.JA_LEVEL_2_CRITERIA
        
        for category, criteria_list in criteria_to_check.items():
            for criterion in criteria_list:
                if criterion in text:
                    return {
                        'is_level_2': True,
                        'rationale': f'ESI Level 2: {criterion} (high-risk {category})'
                    }
        
        # Severe pain with systemic involvement
        pain_score = clinical_data.get('pain_score')
        if pain_score and pain_score >= 8:
            systemic_keywords = ['chest', 'abdominal', 'flank', 'renal']
            if any(kw in text for kw in systemic_keywords):
                return {
                    'is_level_2': True,
                    'rationale': 'ESI Level 2: Severe pain (≥8/10) with systemic presentation'
                }
        
        return {'is_level_2': False, 'rationale': None}
    
    def _check_esi_level_3(self, text: str, clinical_data: dict, language: str) -> dict:
        """Decision Point C: Multiple resources needed (≥2)?"""
        
        criteria_to_check = self.LEVEL_3_CRITERIA
        if language in ['ja', 'jp', 'japanese']:
            criteria_to_check = self.JA_LEVEL_3_CRITERIA
        
        for category, criteria_list in criteria_to_check.items():
            for criterion in criteria_list:
                if criterion in text:
                    return {
                        'is_level_3': True,
                        'rationale': f'ESI Level 3: {criterion} (multiple resources - {category})'
                    }
        
        return {'is_level_3': False, 'rationale': None}
    
    def _check_esi_level_4(self, text: str, clinical_data: dict, language: str) -> dict:
        """Decision Point C: One resource needed?"""
        
        criteria_to_check = self.LEVEL_4_CRITERIA
        if language in ['ja', 'jp', 'japanese']:
            criteria_to_check = self.JA_LEVEL_4_CRITERIA
        
        for category, criteria_list in criteria_to_check.items():
            for criterion in criteria_list:
                if criterion in text:
                    return {
                        'is_level_4': True,
                        'rationale': f'ESI Level 4: {criterion} (one resource - {category})'
                    }
        
        return {'is_level_4': False, 'rationale': None}
    
    def _check_esi_level_5(self, text: str, clinical_data: dict, language: str) -> dict:
        """Decision Point C: No resources needed?"""
        
        criteria_to_check = self.LEVEL_5_CRITERIA
        if language in ['ja', 'jp', 'japanese']:
            criteria_to_check = self.JA_LEVEL_5_CRITERIA
        
        for category, criteria_list in criteria_to_check.items():
            for criterion in criteria_list:
                if criterion in text:
                    return {
                        'is_level_5': True,
                        'rationale': f'ESI Level 5: {criterion} (no resources - {category})'
                    }
        
        return {'is_level_5': False, 'rationale': None}
    
    def _ai_classification(self, transcript: str, soap: dict, language: str = "en") -> dict:
        """AI contextual analysis to refine ESI classification"""
        
        is_japanese = language in ["ja", "jp", "japanese"]
        lang_name = "JAPANESE" if is_japanese else "ENGLISH"
        
        prompt = f"""You are an emergency medicine physician using the Emergency Severity Index (ESI) Version 5.

IMPORTANT: Provide REASONING in {lang_name}.

ESI LEVELS:
- ESI 1/CRITICAL: Immediate life threat (cardiac arrest, not breathing, unresponsive)
- ESI 2/HIGH: High-risk/likely to deteriorate (chest pain, stroke, severe trauma)
- ESI 3/MEDIUM: Multiple resources needed but stable (moderate pain, infections needing multiple tests)
- ESI 4/LOW: One resource needed (simple laceration, minor sprain, simple UTI)
- ESI 5/MINIMAL: No resources needed (prescription refill, advice only, stable chronic condition)

CRITICAL RULES:
1. Context matters: "No chest pain" is LOW, not HIGH
2. Negation detection: "denies chest pain" = LOW
3. Nonsense/testing: "blah blah", "testing 123" = LOW
4. Safety first: Escalate only for clear medical threats

TRANSCRIPT:
{transcript}

SOAP NOTES:
Subjective: {soap.get('subjective', 'N/A')}
Objective: {soap.get('objective', 'N/A')}
Assessment: {soap.get('assessment', 'N/A')}
Plan: {soap.get('plan', 'N/A')}

Respond in EXACT format:
LEVEL: [CRITICAL/HIGH/MEDIUM/LOW/MINIMAL]
SCORE: [0-100]
REASONING: [Brief clinical rationale in {lang_name}]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an emergency medicine physician trained in ESI triage."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=250
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_ai_response(content)
            
        except Exception as e:
            print(f"✗ AI classification failed: {e}")
            return {
                'level': 'MEDIUM',
                'score': 50,
                'reasoning': 'AI analysis unavailable - using ESI baseline'
            }
    
    def _parse_ai_response(self, content: str) -> dict:
        """Parse structured AI response"""
        level = 'MEDIUM'
        score = 50
        reasoning = ''
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('LEVEL:'):
                level = line.split(':', 1)[1].strip()
            elif line.startswith('SCORE:'):
                try:
                    score = float(line.split(':', 1)[1].strip())
                except:
                    score = 50
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        return {
            'level': level,
            'score': score,
            'reasoning': reasoning
        }
    
    def _hybrid_decision(self, esi_result: dict, ai_result: dict, language: str) -> dict:
        """
        Combine ESI rule-based and AI contextual analysis
        
        Strategy:
        1. ESI Level 1/2 (critical/high-risk): Trust ESI (evidence-based, always escalate)
        2. ESI Level 4/5 (low/minimal): Trust ESI unless AI detects higher urgency (safety-first)
        3. ESI Level 3 (medium): Use AI refinement (context-aware)
        4. Safety-first: Always escalate to higher urgency if either method suggests it
        5. Special case: AI can detect nonsense/testing and downgrade appropriately
        """
        
        # Map ESI levels to urgency
        esi_level = esi_result['esi_level']
        esi_urgency = esi_result['urgency']
        
        # ESI Level 1 or 2: Trust evidence-based criteria (critical/high risk)
        if esi_level <= 2:
            print(f"  ├─ ESI detected {esi_urgency} - using evidence-based classification")
            return {
                'level': esi_urgency,
                'score': 100 if esi_level == 1 else 85,
                'reasoning': f"{esi_result['rationale']} (Evidence-based ESI v5)",
                'esi_level': esi_level,
                'method': 'ESI Rule-based',
                'time_to_physician': esi_result['time_to_physician']
            }
        
        # ESI Level 4 or 5: Trust evidence-based criteria but allow AI escalation (safety-first)
        if esi_level >= 4:
            ai_level = ai_result.get('level', 'LOW')
            # Safety-first: If AI detects higher urgency, escalate
            urgency_priority = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'MINIMAL': 1}
            
            if urgency_priority.get(ai_level, 0) > urgency_priority.get(esi_urgency, 0):
                print(f"  ├─ ESI: {esi_urgency}, but AI detected {ai_level} - escalating (safety-first)")
                return {
                    'level': ai_level,
                    'score': ai_result['score'],
                    'reasoning': f"{ai_result['reasoning']} (AI escalation from ESI Level {esi_level})",
                    'esi_level': esi_level,
                    'method': 'AI Safety Escalation',
                    'time_to_physician': esi_result['time_to_physician']
                }
            else:
                print(f"  ├─ ESI detected {esi_urgency} - using evidence-based classification")
                return {
                    'level': esi_urgency,
                    'score': 30 if esi_level == 4 else 10,
                    'reasoning': f"{esi_result['rationale']} (Evidence-based ESI v5)",
                    'esi_level': esi_level,
                    'method': 'ESI Rule-based',
                    'time_to_physician': esi_result['time_to_physician']
                }
        
        # ESI Level 3: Use AI contextual refinement with safety-first comparison
        print(f"  ├─ ESI baseline: {esi_urgency}, AI analysis: {ai_result['level']}")
        
        # Safety first: take higher urgency (5-level priority)
        urgency_priority = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'MINIMAL': 1}
        
        # SPECIAL CASE: AI Detection of Nonsense/Testing - allow downgrade to LOW or MINIMAL
        ai_level = ai_result.get('level', 'LOW')
        ai_reasoning = ai_result.get('reasoning', '').lower()
        is_nonsense = any(word in ai_reasoning for word in ['nonsense', 'testing', 'blah', 'gibberish', 'unrelated', 'non-medical'])
        
        if (ai_level in ['LOW', 'MINIMAL']) and is_nonsense:
            print(f"  ├─ AI detected nonsense/testing - allowing downgrade to {ai_level}")
            mapped_esi_level = 5 if ai_level == 'MINIMAL' else 4
            return {
                'level': ai_level,
                'score': ai_result['score'],
                'reasoning': ai_result['reasoning'],
                'esi_level': mapped_esi_level,
                'method': 'AI Nonsense Filter',
                'time_to_physician': 'N/A' if ai_level == 'MINIMAL' else 'Within 1-2 hours'
            }

        if urgency_priority.get(ai_level, 0) > urgency_priority.get(esi_urgency, 0):
            final_level = ai_level
            reasoning = f"{ai_result['reasoning']} (AI-enhanced from ESI Level {esi_level})"
            method = 'AI-Enhanced'
        else:
            final_level = esi_urgency
            reasoning = f"{esi_result['rationale']} + AI confirmation"
            method = 'ESI + AI Confirmed'
        
        return {
            'level': final_level,
            'score': ai_result['score'],
            'reasoning': reasoning,
            'esi_level': esi_level,
            'method': method,
            'time_to_physician': esi_result.get('time_to_physician', 'TBD')
        }

# Singleton instance
urgency_classifier = HybridUrgencyClassifier()
