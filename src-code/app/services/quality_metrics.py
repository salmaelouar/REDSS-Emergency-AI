"""
Quality Metrics Module - BLEU vs CUDA Comparison
Add this to: app/services/quality_metrics.py
"""

import re
from typing import Dict, List, Tuple
from collections import Counter

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download('punkt', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not available. Install with: pip install nltk")


class QualityMetricsCalculator:
    """Calculate BLEU and CUDA metrics for SOAP note comparison"""
    
    def __init__(self):
        if NLTK_AVAILABLE:
            self.smoothing = SmoothingFunction()
        else:
            self.smoothing = None
    
    def _clean_text(self, text: str) -> str:
        """Remove speaker labels and metadata for better comparison (supports English and Japanese)"""
        if not text: return ""
        # Remove [Metadata in brackets]
        text = re.sub(r'\[.*?\]', '', text)
        # Remove Speaker: labels (English and Japanese)
        text = re.sub(r'^(Dispatcher|Caller|通信指令員|通報者|Man|Woman):\s*', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # Remove punctuation but keep word characters and CJK ranges
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', ' ', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()

    def calculate_wer(self, reference: str, hypothesis: str) -> Dict[str, any]: # DICT IS A DICTIONARY
        """
        Calculate Word Error Rate (WER) for transcription quality
        """
        if not reference or not hypothesis:
            return {
                "wer": 1.0,
                "wer_percentage": 100.0,
                "correct_words": 0,
                "errors": 0,
                "total_words": 0,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 0,
                "accuracy": 0.0
            }
        
        # Clean both texts first
        reference = self._clean_text(reference)
        hypothesis = self._clean_text(hypothesis)
        
        # Tokenize
        def tokenize(text):
            has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))
            if has_japanese:
                return [c for c in text if c.strip()]
            else:
                return re.findall(r'\w+', text)
        
        ref_tokens = tokenize(reference)
        hyp_tokens = tokenize(hypothesis)
        
        # Levenshtein distance calculation (dynamic programming)
        n = len(ref_tokens)
        m = len(hyp_tokens)
        
        # Create DP matrix
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        
        # Initialize base cases
        for i in range(n + 1):
            dp[i][0] = i  # Deletions
        for j in range(m + 1):
            dp[0][j] = j  # Insertions
        
        # Fill DP matrix
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_tokens[i-1] == hyp_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1]  # Match
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # Deletion
                        dp[i][j-1],      # Insertion
                        dp[i-1][j-1]     # Substitution
                    )
        
        # Backtrack to count operation types
        total_edits = dp[n][m]
        substitutions = 0
        deletions = 0
        insertions = 0
        
        i, j = n, m
        while i > 0 or j > 0:
            if i > 0 and j > 0 and ref_tokens[i-1] == hyp_tokens[j-1]:
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                substitutions += 1
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
                deletions += 1
                i -= 1
            else:
                insertions += 1
                j -= 1
        
        # Calculate metrics
        total_words = n
        errors = total_edits
        # Standard: Correct = N - S - D
        correct_words = max(0, n - (substitutions + deletions))
        
        # Standard WER can be > 1.0 if I is large
        wer = total_edits / total_words if total_words > 0 else 1.0
        
        # Word Recognition Rate (WRR) / Accuracy
        # Clamped at 0 to 100 for display
        accuracy = max(0, (1 - wer) * 100)
        
        return {
            "wer": round(wer, 4),
            "wer_percentage": round(wer * 100, 2),
            "correct_words": correct_words,
            "errors": errors,
            "total_words": total_words,
            "substitutions": substitutions,
            "deletions": deletions,
            "insertions": insertions,
            "accuracy": round(accuracy, 2)
        }
    
    def calculate_all_metrics(self, reference_soap: Dict[str, str], 
                              hypothesis_soap: Dict[str, str]) -> Dict:
        """
        Calculate both BLEU and CUDA metrics for all SOAP fields
        
        Args:
            reference_soap: Gold standard SOAP notes
            hypothesis_soap: AI-generated SOAP notes
            
        Returns:
            Dictionary with all metrics
        """
        
        results = {
            "fields": {},
            "overall": {}
        }
        
        # Calculate for each SOAP field
        all_bleu_scores = []
        all_cuda_scores = []
        
        for field in ['subjective', 'objective', 'assessment', 'plan']:
            ref_text = reference_soap.get(field, "")
            hyp_text = hypothesis_soap.get(field, "")
            
            # Calculate BLEU
            bleu_scores = self.calculate_bleu(ref_text, hyp_text)
            
            # Calculate CUDA
            cuda_scores = self.calculate_cuda(ref_text, hyp_text)
            
            # Store field-specific results
            results["fields"][field] = {
                "bleu": bleu_scores,
                "cuda": cuda_scores
            }
            
            # Collect for overall average
            if bleu_scores:
                all_bleu_scores.append(bleu_scores.get('bleu_avg', 0))
            if cuda_scores:
                all_cuda_scores.append(cuda_scores.get('cuda_overall', 0))
        
        # Calculate overall averages
        results["overall"] = {
            "bleu_avg": sum(all_bleu_scores) / len(all_bleu_scores) if all_bleu_scores else 0,
            "cuda_overall": sum(all_cuda_scores) / len(all_cuda_scores) if all_cuda_scores else 0
        }
        
        return results
    
    def calculate_bleu(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate BLEU scores (1-4 gram)
        """
        
        if not NLTK_AVAILABLE:
            return {
                "bleu_1": 0.0, "bleu_2": 0.0, "bleu_3": 0.0, "bleu_4": 0.0, "bleu_avg": 0.0
            }
        
        if not reference or not hypothesis:
            return {
                "bleu_1": 0.0, "bleu_2": 0.0, "bleu_3": 0.0, "bleu_4": 0.0, "bleu_avg": 0.0
            }
        
        try:
            # Smart Tokenization: Detect if it's a non-spaced language (like Japanese/Chinese)
            # If the text has few spaces but many characters, use character-level tokenization
            def smart_tokenize(text):
                text = text.lower().strip()
                # Basic check for Japanese characters
                has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))
                
                if has_japanese:
                    # Character-level tokenization for Japanese
                    # Filter out punctuation and whitespace
                    return [c for c in text if c.strip() and not re.match(r'[^\w\s]', c)]
                else:
                    # Standard word tokenization for English etc.
                    return word_tokenize(text)

            ref_tokens = smart_tokenize(reference)
            hyp_tokens = smart_tokenize(hypothesis)
            
            if not ref_tokens or not hyp_tokens:
                 return {"bleu_1": 0.0, "bleu_avg": 0.0}

            # Calculate BLEU-1 through BLEU-4
            scores = {}
            for n in range(1, 5):
                # Only calculate up to the available number of tokens
                if len(hyp_tokens) < n:
                    scores[f'bleu_{n}'] = 0.0
                    continue
                    
                weights = tuple([1.0/n] * n + [0.0] * (4-n))
                score = sentence_bleu(
                    [ref_tokens], 
                    hyp_tokens, 
                    weights=weights,
                    smoothing_function=self.smoothing.method1
                )
                scores[f'bleu_{n}'] = round(score, 4)
            
            # Average BLEU
            scores['bleu_avg'] = round(sum(scores.values()) / 4, 4)
            
            return scores
            
        except Exception as e:
            print(f"BLEU calculation error: {e}")
            return {
                "bleu_1": 0.0,
                "bleu_2": 0.0,
                "bleu_3": 0.0,
                "bleu_4": 0.0,
                "bleu_avg": 0.0
            }
    
    def calculate_cuda(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate CUDA scores
        """
        
        if not reference or not hypothesis:
            return {
                "completion": 0.0, "understanding": 0.0, "detail": 0.0, "accuracy": 0.0, "cuda_overall": 0.0
            }
        
        # Tokenize specifically for word/concept set comparison
        def get_words(text):
            text = self._clean_text(text)
            has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))
            if has_japanese:
                return [c for c in text if c.strip()]
            return text.split()

        ref_words = set(get_words(reference))
        hyp_words = set(get_words(hypothesis))
        
        # 1. COMPLETION: How much of reference is in hypothesis
        if len(ref_words) > 0:
            completion = len(ref_words & hyp_words) / len(ref_words)
        else:
            completion = 0.0
        
        # 2. UNDERSTANDING: Jaccard similarity (word overlap)
        union = ref_words | hyp_words
        if len(union) > 0:
            understanding = len(ref_words & hyp_words) / len(union)
        else:
            understanding = 0.0
        
        # 3. DETAIL: Length ratio
        ref_len = len(get_words(reference))
        hyp_len = len(get_words(hypothesis))
        if ref_len > 0:
            length_ratio = min(hyp_len, ref_len) / max(hyp_len, ref_len)
            detail = length_ratio
        else:
            detail = 0.0
        
        # 4. ACCURACY: Precision - no hallucinations
        if len(hyp_words) > 0:
            accuracy = len(ref_words & hyp_words) / len(hyp_words)
        else:
            accuracy = 0.0
        
        # Overall CUDA score (average of components)
        cuda_score = (completion + understanding + detail + accuracy) / 4
        
        return {
            "completion": round(completion, 4),
            "understanding": round(understanding, 4),
            "detail": round(detail, 4),
            "accuracy": round(accuracy, 4),
            "cuda_overall": round(cuda_score, 4)
        }
    


# Singleton instance
quality_calculator = QualityMetricsCalculator()