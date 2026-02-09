import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.quality_metrics import quality_calculator
import json

ref = "The patient has chest pain and is sweating."
hyp = "The patient has chest pain and is very sweaty."

bleu = quality_calculator.calculate_bleu(ref, hyp)
cuda = quality_calculator.calculate_cuda(ref, hyp)
wer = quality_calculator.calculate_wer(ref, hyp)

print(json.dumps({
    "bleu": bleu,
    "cuda": cuda,
    "wer": wer
}, indent=2))
