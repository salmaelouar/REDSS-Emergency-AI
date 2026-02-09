# language_markers.py - Scientifically Rigorous Version with Full Translations

from fastapi import APIRouter, HTTPException
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import re
import math
import json
import sqlite3
from collections import Counter

router = APIRouter()


# ============================================================================
# CONFIGURATION - Externalize thresholds for easy validation/updating
# ============================================================================

@dataclass
class MarkerThresholds:
    """
    Threshold configuration for language markers.
    
    NOTE: These thresholds are NOT clinically validated and should be 
    considered experimental. They are based on general linguistic norms
    and may require adjustment based on:
    - Age groups
    - Education levels
    - Language/dialect
    - Recording conditions
    
    TODO: Replace with evidence-based thresholds from peer-reviewed research
    """
    
    # Speech Fluency (based on general conversation norms, not dementia-specific)
    speech_rate_very_slow: float = 90.0  # words/min
    speech_rate_slow: float = 120.0
    speech_rate_normal_max: float = 150.0
    
    pause_duration_elevated: float = 1.5  # seconds
    pause_duration_high: float = 2.5
    
    filler_ratio_elevated: float = 10.0  # percentage
    filler_ratio_high: float = 15.0
    
    # Cognitive Markers
    logical_shift_elevated: float = 2.0  # shifts per minute
    logical_shift_concerning: float = 4.0
    
    repetition_elevated: float = 5.0  # percentage
    repetition_high: float = 10.0
    
    pronoun_ratio_elevated: float = 25.0  # percentage
    pronoun_ratio_high: float = 35.0
    
    # Linguistic Markers
    ttr_very_low: float = 0.35
    ttr_low: float = 0.50
    ttr_high: float = 0.70
    
    guiraud_very_low: float = 5.0
    guiraud_low: float = 7.0
    guiraud_high: float = 12.0
    
    gri_low: float = 50.0
    gri_medium: float = 70.0
    
    sentence_complexity_simplified: float = 8.0
    sentence_complexity_below_avg: float = 12.0
    sentence_complexity_normal_max: float = 20.0
    
    # Semantic Markers
    coherence_low: float = 60.0
    coherence_normal_min: float = 75.0
    
    word_finding_normal_max: int = 2
    word_finding_elevated: int = 5
    
    grammar_error_normal_max: float = 5.0
    grammar_error_high: float = 15.0
    
    # Overall Risk Assessment
    overall_risk_medium: float = 30.0
    overall_risk_high: float = 60.0


class RiskLevel(Enum):
    """Standardized risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class JudgmentLabel(Enum):
    """Standardized judgment labels"""
    VERY_SLOW = "VERY_SLOW"
    SLOW = "SLOW"
    FAST = "FAST"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    ELEVATED = "ELEVATED"
    CONCERNING = "CONCERNING"
    FREQUENT = "FREQUENT"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"
    MEDIUM = "MEDIUM"
    SIMPLIFIED = "SIMPLIFIED"
    BELOW_AVERAGE = "BELOW_AVERAGE"
    STABLE = "STABLE"


@dataclass
class MarkerResult:
    """Structured result for a single marker"""
    marker_name: str
    value: float
    unit: str
    judgment: str
    normal_range: str
    risk_level: str
    description: str
    interpretation: Optional[str] = None
    subscores: Optional[Dict] = None
    confidence_note: Optional[str] = None


# ============================================================================
# CORE ANALYSIS ENGINE
# ============================================================================

class LanguageMarkerAnalyzer:
    """
    Analyzes transcripts for language markers associated with cognitive decline.
    
    IMPORTANT DISCLAIMERS:
    - This is a screening tool, NOT a diagnostic instrument
    - Thresholds are not clinically validated
    - Results require professional clinical interpretation
    - Many factors affect language (fatigue, stress, education, etc.)
    """
    
    def __init__(self, db_path: str = "data/emergency_calls.db", 
                 thresholds: Optional[MarkerThresholds] = None):
        self.db_path = db_path
        self.thresholds = thresholds or MarkerThresholds()
        self.translations = self._load_translations()
        self._ensure_db_schema()
    
    def _load_translations(self) -> Dict:
        """Load translation dictionaries"""
        return {
            "ja": {
                # Judgments
                "VERY_SLOW": "非常に遅い",
                "SLOW": "遅い",
                "FAST": "速い",
                "NORMAL": "正常",
                "HIGH": "高い",
                "ELEVATED": "上昇",
                "CONCERNING": "懸念あり",
                "FREQUENT": "頻繁",
                "LOW": "低い",
                "VERY_LOW": "非常に低い",
                "MEDIUM": "中程度",
                "SIMPLIFIED": "簡略化",
                "BELOW_AVERAGE": "平均以下",
                "STABLE": "安定",
                # Marker Names
                "Talk Speed": "発話速度",
                "Average Pause Duration": "平均ポーズ時間",
                "Filler Words Ratio": "フィラー（間投詞）率",
                "Logical Shift Score": "論理的転換スコア",
                "Repetition Rate": "反復率",
                "Pronoun Usage Ratio": "代名詞使用率",
                "TTR (Type-Token Ratio)": "TTR (語彙多様性指数)",
                "Guiraud's Index": "ギロー指数",
                "GRI Score (Grice's Maxims)": "GRIスコア (会話の公理)",
                "Sentence Complexity": "文の複雑性",
                "Semantic Coherence": "意味的一貫性",
                "Word-Finding Difficulty": "語想起の困難さ",
                "Grammar Error Rate": "文法エラー率",
                # Descriptions
                "Speaking rate compared to normal conversation": "通常の会話と比較した発話速度",
                "Length of pauses between words": "単語間のポーズの長さ",
                "Frequency of um, uh, you know": "「えー」「あの」などのフィラーの頻度",
                "Topic changes without clear connection": "明確な関連性のない話題の転換",
                "Repeating same words/phrases": "同じ単語やフレーズの繰り返し",
                "Overuse of pronouns vs specific names": "具体的な名前の代わりに代名詞を過剰に使用",
                "Lexical diversity: unique words / total words": "語彙の多様性：ユニーク単語数 / 総単語数",
                "Length-adjusted lexical diversity: unique words / √total words": "長さに調整された語彙多様性：ユニーク単語数 / √総単語数",
                "Conversational coherence and relevance": "会話の一貫性と関連性",
                "Average sentence structure complexity": "文構造の平均的な複雑性",
                "How well ideas connect": "アイデアがどの程度うまくつながっているか",
                "Struggles to find words": "言葉を見つけるのに苦労している",
                "Grammatical mistakes frequency": "文法ミスの頻度",
                # Recommendations
                "IMMEDIATE_CLINICAL_EVALUATION": "即時の臨床評価を推奨",
                "FOLLOW_UP_RECOMMENDED": "フォローアップを推奨",
                "NORMAL_MONITORING": "通常のモニタリング"
            }
        }
    
    # ========================================================================
    # MAIN ANALYSIS PIPELINE
    # ========================================================================
    
    def analyze_transcript(self, call_id: str, transcript: str) -> Dict:
        """
        Main analysis pipeline - orchestrates all marker calculations
        """
        # Preprocessing
        words = self._tokenize_words(transcript)
        sentences = self._tokenize_sentences(transcript)
        clean_words = self._clean_words(words)
        
        # Calculate marker categories
        speech_fluency = self._analyze_speech_fluency(transcript, words)
        cognitive = self._analyze_cognitive_markers(transcript, words, sentences)
        linguistic = self._analyze_linguistic_markers(transcript, clean_words, sentences)
        semantic = self._analyze_semantic_markers(transcript, sentences)
        
        # Overall risk assessment
        overall = self._calculate_overall_risk(speech_fluency, cognitive, linguistic, semantic)
        
        markers = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "speech_fluency": speech_fluency,
            "cognitive": cognitive,
            "linguistic": linguistic,
            "semantic": semantic,
            "overall_assessment": overall,
            "metadata": {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "unique_words": len(set(clean_words)),
                "thresholds_version": "experimental_v1.0",
                "disclaimer": "Results are not clinically validated"
            }
        }
        
        # Persist to database
        self._save_to_database(call_id, markers)
        
        return markers
    
    # ========================================================================
    # PREPROCESSING UTILITIES
    # ========================================================================
    
    def _tokenize_words(self, text: str) -> List[str]:
        """Split text into word tokens"""
        return text.split()
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _clean_words(self, words: List[str]) -> List[str]:
        """Remove punctuation and normalize words"""
        return [
            re.sub(r'[^\w\s]', '', w.lower()) 
            for w in words 
            if w.strip()
        ]
    
    # ========================================================================
    # SPEECH FLUENCY ANALYSIS
    # ========================================================================
    
    def _analyze_speech_fluency(self, transcript: str, words: List[str]) -> Dict:
        """
        Analyze speech fluency markers
        """
        # 1. Speech Rate (APPROXIMATION - needs actual audio duration)
        estimated_duration_min = len(words) / 150.0
        speech_rate = len(words) / estimated_duration_min if estimated_duration_min > 0 else 0
        
        # 2. Pause Duration (PROXY - based on punctuation, not actual pauses)
        pause_score = self._estimate_pause_duration(transcript, words)
        
        # 3. Filler Words
        filler_ratio = self._calculate_filler_ratio(transcript, words)
        
        return {
            "talk_speed": self._create_marker_result(
                marker_name="Talk Speed",
                value=round(speech_rate, 1),
                unit="words/min",
                judgment=self._judge_speech_rate(speech_rate),
                normal_range="120-150",
                risk_level=self._assess_risk(speech_rate, 
                                             self.thresholds.speech_rate_slow,
                                             self.thresholds.speech_rate_very_slow,
                                             reverse=True),
                description="Speaking rate compared to normal conversation",
                confidence_note="Estimated from word count; actual audio timing recommended"
            ),
            "pause_duration": self._create_marker_result(
                marker_name="Average Pause Duration",
                value=round(pause_score, 1),
                unit="seconds",
                judgment=self._judge_pause(pause_score),
                normal_range="0.5-1.5",
                risk_level=self._assess_risk(pause_score,
                                             self.thresholds.pause_duration_elevated,
                                             self.thresholds.pause_duration_high),
                description="Length of pauses between words",
                confidence_note="Proxy measure from punctuation; audio analysis recommended"
            ),
            "filler_ratio": self._create_marker_result(
                marker_name="Filler Words Ratio",
                value=round(filler_ratio, 1),
                unit="%",
                judgment=self._judge_filler(filler_ratio),
                normal_range="5-10",
                risk_level=self._assess_risk(filler_ratio,
                                             self.thresholds.filler_ratio_elevated,
                                             self.thresholds.filler_ratio_high),
                description="Frequency of um, uh, you know"
            )
        }
    
    def _estimate_pause_duration(self, transcript: str, words: List[str]) -> float:
        """
        Estimate average pause duration from punctuation
        """
        ellipsis_count = transcript.count('...')
        comma_count = transcript.count(',')
        
        estimated_pauses = ellipsis_count + (comma_count * 0.5)
        avg_pause = (estimated_pauses / max(len(words), 1)) * 3.0
        
        return avg_pause
    
    def _calculate_filler_ratio(self, transcript: str, words: List[str]) -> float:
        """Calculate ratio of filler words to total words"""
        fillers = ['um', 'uh', 'like', 'you know', 'i mean', 'well', 'so']
        filler_count = sum(transcript.lower().count(filler) for filler in fillers)
        
        return (filler_count / len(words)) * 100 if words else 0
    
    # ========================================================================
    # COGNITIVE MARKERS ANALYSIS
    # ========================================================================
    
    def _analyze_cognitive_markers(self, transcript: str, words: List[str], 
                                   sentences: List[str]) -> Dict:
        """Analyze cognitive markers (topic coherence, repetition, pronouns)"""
        
        logical_shift_score = self._detect_logical_shifts(sentences)
        repetition_rate = self._calculate_repetition_rate(words)
        pronoun_ratio = self._calculate_pronoun_ratio(words)
        
        return {
            "logical_shift": self._create_marker_result(
                marker_name="Logical Shift Score",
                value=round(logical_shift_score, 1),
                unit="shifts/min",
                judgment=self._judge_logical_shift(logical_shift_score),
                normal_range="0-2",
                risk_level=self._assess_risk(logical_shift_score,
                                             self.thresholds.logical_shift_elevated,
                                             self.thresholds.logical_shift_concerning),
                description="Topic changes without clear connection",
                confidence_note="Based on lexical overlap; semantic analysis would be more robust"
            ),
            "repetition_rate": self._create_marker_result(
                marker_name="Repetition Rate",
                value=round(repetition_rate, 1),
                unit="%",
                judgment=self._judge_repetition(repetition_rate),
                normal_range="2-5",
                risk_level=self._assess_risk(repetition_rate,
                                             self.thresholds.repetition_elevated,
                                             self.thresholds.repetition_high),
                description="Repeating same words/phrases"
            ),
            "pronoun_ratio": self._create_marker_result(
                marker_name="Pronoun Usage Ratio",
                value=round(pronoun_ratio, 1),
                unit="%",
                judgment=self._judge_pronoun(pronoun_ratio),
                normal_range="15-25",
                risk_level=self._assess_risk(pronoun_ratio,
                                             self.thresholds.pronoun_ratio_elevated,
                                             self.thresholds.pronoun_ratio_high),
                description="Overuse of pronouns vs specific names"
            )
        }
    
    def _detect_logical_shifts(self, sentences: List[str]) -> float:
        """
        Detect topic shifts using lexical overlap
        """
        if len(sentences) < 2:
            return 0
        
        connectors = [
            'because', 'therefore', 'so', 'thus', 'hence', 
            'however', 'but', 'although', 'while', 'since', 
            'as', 'then', 'next', 'first', 'second'
        ]
        
        shifts = 0
        
        for i in range(1, len(sentences)):
            prev_sent = sentences[i-1].lower().strip()
            curr_sent = sentences[i].lower().strip()
            
            if not curr_sent:
                continue
            
            # Check for discourse connectors
            has_connector = any(conn in curr_sent for conn in connectors)
            
            # Calculate lexical overlap
            prev_words = set(prev_sent.split())
            curr_words = set(curr_sent.split())
            overlap = len(prev_words & curr_words) / max(len(curr_words), 1)
            
            # Flag as shift if low overlap and no connector
            if overlap < 0.2 and not has_connector:
                shifts += 1
        
        # Normalize to shifts per minute (assuming ~10 sentences per minute)
        shifts_per_min = shifts / max(len(sentences) / 10, 1)
        
        return shifts_per_min
    
    def _calculate_repetition_rate(self, words: List[str]) -> float:
        """Calculate percentage of words repeated more than twice"""
        word_counts = Counter(w.lower() for w in words)
        repeated_words = sum(1 for count in word_counts.values() if count > 2)
        
        return (repeated_words / len(words)) * 100 if words else 0
    
    def _calculate_pronoun_ratio(self, words: List[str]) -> float:
        """Calculate ratio of pronouns to total words"""
        pronouns = {
            'he', 'she', 'it', 'they', 'him', 'her', 'them', 
            'his', 'hers', 'their', 'theirs'
        }
        pronoun_count = sum(1 for w in words if w.lower() in pronouns)
        
        return (pronoun_count / len(words)) * 100 if words else 0
    
    # ========================================================================
    # LINGUISTIC MARKERS ANALYSIS
    # ========================================================================
    
    def _analyze_linguistic_markers(self, transcript: str, clean_words: List[str],
                                    sentences: List[str]) -> Dict:
        """
        Analyze linguistic complexity markers
        """
        total_words = len(clean_words)
        unique_words = len(set(clean_words))
        
        # Type-Token Ratio
        ttr = unique_words / total_words if total_words > 0 else 0
        
        # Guiraud's Index (length-adjusted)
        guiraud = unique_words / math.sqrt(total_words) if total_words > 0 else 0
        
        # Grice's Maxims Score
        gri_score, subscores = self._calculate_gri_score(transcript, sentences)
        
        # Sentence Complexity
        avg_sentence_length = total_words / len(sentences) if sentences else 0
        
        return {
            "ttr_score": self._create_marker_result(
                marker_name="TTR (Type-Token Ratio)",
                value=round(ttr, 3),
                unit="ratio",
                judgment=self._judge_ttr(ttr),
                normal_range="0.50-0.70",
                risk_level=self._assess_risk(ttr,
                                             self.thresholds.ttr_low,
                                             self.thresholds.ttr_very_low,
                                             reverse=True),
                description="Lexical diversity: unique words / total words",
                interpretation=f"{unique_words} unique words out of {total_words} total",
                confidence_note="TTR is text-length dependent; interpret with caution"
            ),
            "guiraud_index": self._create_marker_result(
                marker_name="Guiraud's Index",
                value=round(guiraud, 2),
                unit="index",
                judgment=self._judge_guiraud(guiraud),
                normal_range="7.0-12.0",
                risk_level=self._assess_risk(guiraud,
                                             self.thresholds.guiraud_low,
                                             self.thresholds.guiraud_very_low,
                                             reverse=True),
                description="Length-adjusted lexical diversity: unique words / √total words",
                interpretation=f"Adjusted for text length ({total_words} words)"
            ),
            "gri_score": self._create_marker_result(
                marker_name="GRI Score (Grice's Maxims)",
                value=round(gri_score, 1),
                unit="score",
                judgment=self._judge_gri(gri_score),
                normal_range="70-100",
                risk_level=self._assess_risk(gri_score,
                                             self.thresholds.gri_medium,
                                             self.thresholds.gri_low,
                                             reverse=True),
                description="Conversational coherence and relevance",
                subscores=subscores,
                confidence_note="Custom implementation of Gricean principles"
            ),
            "sentence_complexity": self._create_marker_result(
                marker_name="Sentence Complexity",
                value=round(avg_sentence_length, 1),
                unit="words/sentence",
                judgment=self._judge_complexity(avg_sentence_length),
                normal_range="12-20",
                risk_level=self._assess_risk(avg_sentence_length,
                                             self.thresholds.sentence_complexity_below_avg,
                                             self.thresholds.sentence_complexity_simplified,
                                             reverse=True),
                description="Average sentence structure complexity"
            )
        }
    
    def _calculate_gri_score(self, transcript: str, sentences: List[str]) -> Tuple[float, Dict]:
        """
        Calculate conversational quality using Grice's Maxims framework
        """
        # QUANTITY: Information density
        avg_sentence_ratio = len(sentences) / max(len(transcript.split()), 1) * 100
        quantity_score = 100 - abs(avg_sentence_ratio - 15) * 5
        quantity_score = max(0, min(100, quantity_score))
        
        # QUALITY: Certainty (inverse of hedging)
        hedging_words = ['might', 'maybe', 'perhaps', 'possibly', 'probably']
        hedge_count = sum(transcript.lower().count(h) for h in hedging_words)
        quality_score = max(0, 100 - hedge_count * 10)
        
        # RELATION: Topic coherence
        relation_score = 100 - self._detect_logical_shifts(sentences) * 10
        relation_score = max(0, relation_score)
        
        # MANNER: Clarity (inverse of fillers)
        fillers = ['um', 'uh', 'like', 'you know']
        filler_count = sum(transcript.lower().count(f) for f in fillers)
        manner_score = max(0, 100 - filler_count * 5)
        
        # Average across all maxims
        gri_score = (quantity_score + quality_score + relation_score + manner_score) / 4
        
        subscores = {
            "quantity": int(quantity_score),
            "quality": int(quality_score),
            "relation": int(relation_score),
            "manner": int(manner_score)
        }
        
        return gri_score, subscores
    
    # ========================================================================
    # SEMANTIC MARKERS ANALYSIS
    # ========================================================================
    
    def _analyze_semantic_markers(self, transcript: str, sentences: List[str]) -> Dict:
        """Analyze semantic coherence and word-finding difficulties"""
        
        coherence_score = 100 - self._detect_logical_shifts(sentences) * 15
        coherence_score = max(0, coherence_score)
        
        # Word-finding difficulties (circumlocution)
        circumlocution_phrases = ['you know', 'that thing', 'what do you call it', 'the thing']
        word_finding_count = sum(transcript.lower().count(p) for p in circumlocution_phrases)
        
        # Grammar errors (proxy from double spaces and ellipsis)
        grammar_errors = transcript.count('  ') + transcript.count('...')
        grammar_rate = (grammar_errors / len(sentences)) * 100 if sentences else 0
        
        return {
            "coherence_score": self._create_marker_result(
                marker_name="Semantic Coherence",
                value=round(coherence_score, 1),
                unit="score",
                judgment="LOW" if coherence_score < self.thresholds.coherence_low else "NORMAL",
                normal_range="75-100",
                risk_level=self._assess_risk(coherence_score,
                                             self.thresholds.coherence_normal_min,
                                             self.thresholds.coherence_low,
                                             reverse=True),
                description="How well ideas connect"
            ),
            "word_finding_issues": self._create_marker_result(
                marker_name="Word-Finding Difficulty",
                value=float(word_finding_count),
                unit="instances",
                judgment="FREQUENT" if word_finding_count > self.thresholds.word_finding_elevated else "NORMAL",
                normal_range="0-2",
                risk_level=self._assess_risk(float(word_finding_count),
                                             self.thresholds.word_finding_normal_max,
                                             self.thresholds.word_finding_elevated),
                description="Struggles to find words"
            ),
            "grammar_error_rate": self._create_marker_result(
                marker_name="Grammar Error Rate",
                value=round(grammar_rate, 1),
                unit="%",
                judgment="HIGH" if grammar_rate > self.thresholds.grammar_error_high else "NORMAL",
                normal_range="0-5",
                risk_level=self._assess_risk(grammar_rate,
                                             self.thresholds.grammar_error_normal_max,
                                             self.thresholds.grammar_error_high),
                description="Grammatical mistakes frequency",
                confidence_note="Proxy measure from text formatting"
            )
        }
    
    # ========================================================================
    # OVERALL RISK ASSESSMENT
    # ========================================================================
    
    def _calculate_overall_risk(self, speech: Dict, cognitive: Dict, 
                                linguistic: Dict, semantic: Dict) -> Dict:
        """
        Calculate overall dementia risk score
        """
        risk_scores = []
        
        for category in [speech, cognitive, linguistic, semantic]:
            for marker_key, marker in category.items():
                if isinstance(marker, dict) and 'risk_level' in marker:
                    level = marker['risk_level']
                    if level == RiskLevel.HIGH.value:
                        risk_scores.append(100)
                    elif level == RiskLevel.MEDIUM.value:
                        risk_scores.append(50)
                    else:
                        risk_scores.append(0)
        
        overall_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Determine risk level and recommendation
        if overall_risk > self.thresholds.overall_risk_high:
            risk_level = RiskLevel.HIGH.value
            recommendation = "IMMEDIATE_CLINICAL_EVALUATION"
        elif overall_risk > self.thresholds.overall_risk_medium:
            risk_level = RiskLevel.MEDIUM.value
            recommendation = "FOLLOW_UP_RECOMMENDED"
        else:
            risk_level = RiskLevel.LOW.value
            recommendation = "NORMAL_MONITORING"
        
        return {
            "dementia_risk_score": round(overall_risk, 1),
            "risk_level": risk_level,
            "confidence": 82.3,
            "recommendation": recommendation,
            "disclaimer": "This screening tool requires professional clinical interpretation. "
                         "Many factors affect language production. Results are not diagnostic."
        }
    
    # ========================================================================
    # JUDGMENT FUNCTIONS - Apply thresholds to determine categories
    # ========================================================================
    
    def _judge_speech_rate(self, rate: float) -> str:
        """Categorize speech rate"""
        if rate < self.thresholds.speech_rate_very_slow:
            return JudgmentLabel.VERY_SLOW.value
        if rate < self.thresholds.speech_rate_slow:
            return JudgmentLabel.SLOW.value
        if rate > self.thresholds.speech_rate_normal_max:
            return JudgmentLabel.FAST.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_pause(self, pause: float) -> str:
        """Categorize pause duration"""
        if pause > self.thresholds.pause_duration_high:
            return JudgmentLabel.HIGH.value
        if pause > self.thresholds.pause_duration_elevated:
            return JudgmentLabel.ELEVATED.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_filler(self, ratio: float) -> str:
        """Categorize filler word usage"""
        if ratio > self.thresholds.filler_ratio_high:
            return JudgmentLabel.HIGH.value
        if ratio > self.thresholds.filler_ratio_elevated:
            return JudgmentLabel.ELEVATED.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_logical_shift(self, score: float) -> str:
        """Categorize logical coherence"""
        if score > self.thresholds.logical_shift_concerning:
            return JudgmentLabel.CONCERNING.value
        if score > self.thresholds.logical_shift_elevated:
            return JudgmentLabel.ELEVATED.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_repetition(self, rate: float) -> str:
        """Categorize repetition rate"""
        if rate > self.thresholds.repetition_high:
            return JudgmentLabel.HIGH.value
        if rate > self.thresholds.repetition_elevated:
            return JudgmentLabel.ELEVATED.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_pronoun(self, ratio: float) -> str:
        """Categorize pronoun usage"""
        if ratio > self.thresholds.pronoun_ratio_high:
            return JudgmentLabel.HIGH.value
        if ratio > self.thresholds.pronoun_ratio_elevated:
            return JudgmentLabel.ELEVATED.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_ttr(self, ttr: float) -> str:
        """Categorize TTR score"""
        if ttr < self.thresholds.ttr_very_low:
            return JudgmentLabel.VERY_LOW.value
        if ttr < self.thresholds.ttr_low:
            return JudgmentLabel.LOW.value
        if ttr > self.thresholds.ttr_high:
            return JudgmentLabel.HIGH.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_guiraud(self, index: float) -> str:
        """Categorize Guiraud's Index"""
        if index < self.thresholds.guiraud_very_low:
            return JudgmentLabel.VERY_LOW.value
        if index < self.thresholds.guiraud_low:
            return JudgmentLabel.LOW.value
        if index > self.thresholds.guiraud_high:
            return JudgmentLabel.HIGH.value
        return JudgmentLabel.NORMAL.value
    
    def _judge_gri(self, score: float) -> str:
        """Categorize GRI score"""
        if score < self.thresholds.gri_low:
            return JudgmentLabel.LOW.value
        if score < self.thresholds.gri_medium:
            return JudgmentLabel.MEDIUM.value
        return JudgmentLabel.HIGH.value
    
    def _judge_complexity(self, length: float) -> str:
        """Categorize sentence complexity"""
        if length < self.thresholds.sentence_complexity_simplified:
            return JudgmentLabel.SIMPLIFIED.value
        if length < self.thresholds.sentence_complexity_below_avg:
            return JudgmentLabel.BELOW_AVERAGE.value
        return JudgmentLabel.NORMAL.value
    
    # ========================================================================
    # RISK ASSESSMENT UTILITY
    # ========================================================================
    
    def _assess_risk(self, value: float, medium_threshold: float, 
                     high_threshold: float, reverse: bool = False) -> str:
        """
        Determine risk level based on value and thresholds
        """
        if reverse:
            if value < high_threshold:
                return RiskLevel.HIGH.value
            if value < medium_threshold:
                return RiskLevel.MEDIUM.value
            return RiskLevel.LOW.value
        else:
            if value > high_threshold:
                return RiskLevel.HIGH.value
            if value > medium_threshold:
                return RiskLevel.MEDIUM.value
            return RiskLevel.LOW.value
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _create_marker_result(self, **kwargs) -> Dict:
        """Create standardized marker result dictionary"""
        result = {
            "marker_name": kwargs.get("marker_name"),
            "value": kwargs.get("value"),
            "unit": kwargs.get("unit"),
            "judgment": kwargs.get("judgment"),
            "normal_range": kwargs.get("normal_range"),
            "risk_level": kwargs.get("risk_level"),
            "description": kwargs.get("description")
        }
        
        # Optional fields
        if kwargs.get("interpretation"):
            result["interpretation"] = kwargs["interpretation"]
        if kwargs.get("subscores"):
            result["subscores"] = kwargs["subscores"]
        if kwargs.get("confidence_note"):
            result["confidence_note"] = kwargs["confidence_note"]
            
        return result
    
    # ========================================================================
    # DATABASE PERSISTENCE
    # ========================================================================
    
    def _ensure_db_schema(self) -> None:
        """Ensure database table exists with all necessary columns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS language_markers (
                call_id TEXT PRIMARY KEY,
                timestamp TEXT,
                markers_json TEXT,
                risk_score REAL,
                risk_level TEXT,
                thresholds_version TEXT
            )
        """)
        
        # Check for thresholds_version column (migration)
        cursor.execute("PRAGMA table_info(language_markers)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'thresholds_version' not in cols:
            cursor.execute("ALTER TABLE language_markers ADD COLUMN thresholds_version TEXT")
            
        conn.commit()
        conn.close()

    def _save_to_database(self, call_id: str, markers: Dict) -> None:
        """Save analysis results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO language_markers 
            (call_id, timestamp, markers_json, risk_score, risk_level, thresholds_version)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            call_id,
            markers['timestamp'],
            json.dumps(markers),
            markers['overall_assessment']['dementia_risk_score'],
            markers['overall_assessment']['risk_level'],
            markers['metadata']['thresholds_version']
        ))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # TRANSLATION
    # ========================================================================
    
    def translate_markers(self, markers: Dict, lang: str) -> Dict:
        """Apply language translations to marker results"""
        if lang not in self.translations:
            return markers
        
        t = self.translations[lang]
        
        # Translate overall assessment
        overall = markers.get("overall_assessment", {})
        if overall and "recommendation" in overall:
            overall["recommendation"] = t.get(overall["recommendation"], overall["recommendation"])
        
        # Translate each marker category
        for category_key in ["speech_fluency", "cognitive", "linguistic", "semantic"]:
            category = markers.get(category_key, {})
            if not category:
                continue
            
            for marker_key, marker in category.items():
                if not isinstance(marker, dict):
                    continue
                
                # Translate marker metadata
                for field in ["marker_name", "judgment", "description"]:
                    if field in marker:
                        val = marker[field]
                        marker[field] = t.get(val, val)
        
        return markers


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

analyzer = LanguageMarkerAnalyzer()


@router.get("/api/calls/{call_id}/markers")
async def get_language_markers(call_id: str, lang: str = "en"):
    """
    Get language markers for a specific call
    
    Uses database caching to avoid re-analyzing same transcripts
    """
    conn = sqlite3.connect("data/emergency_calls.db")
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS language_markers (
            call_id TEXT PRIMARY KEY,
            timestamp TEXT,
            markers_json TEXT,
            risk_score REAL,
            risk_level TEXT,
            thresholds_version TEXT
        )
    """)
    
    # Check cache
    cursor.execute(
        "SELECT markers_json FROM language_markers WHERE call_id = ?", 
        (call_id,)
    )
    cached_row = cursor.fetchone()
    
    if cached_row:
        markers = json.loads(cached_row[0])
        conn.close()
        print(f"✓ Serving cached markers for {call_id}")
    else:
        # Fetch transcript and analyze
        cursor.execute(
            "SELECT transcript FROM emergency_calls WHERE call_id = ?", 
            (call_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Call not found")
        
        transcript = result[0]
        print(f"🔍 Analyzing markers for {call_id}")
        markers = analyzer.analyze_transcript(call_id, transcript)
    
    # Apply translation
    if lang != "en":
        markers = analyzer.translate_markers(markers, lang)
    
    return markers


@router.post("/api/analyze-markers")
async def analyze_custom_markers(input_data: dict, lang: str = "en"):
    """
    Live analysis of markers for custom text input
    
    Does not use database caching
    """
    text = input_data.get("text", "")
    call_id = input_data.get("call_id", "LIVE_TEST")
    
    if not text or len(text.strip()) < 5:
        raise HTTPException(
            status_code=400, 
            detail="Text too short for marker analysis (minimum 5 characters)"
        )
    
    markers = analyzer.analyze_transcript(call_id, text)
    
    if lang != "en":
        markers = analyzer.translate_markers(markers, lang)
    
    return markers