import React, { useState, useEffect } from 'react';
import {
  ArrowLeft, RefreshCw, Zap, TrendingUp, Target, CheckCircle
} from 'lucide-react';

function BleuScoreQualityMetrics({ callId, onBack, systemLanguage = 'en' }) {
  const [qualityData, setQualityData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Transcription field states
  const [liveTestText, setLiveTestText] = useState('');
  const [liveReferenceText, setLiveReferenceText] = useState('');
  const [isCalculatingManual, setIsCalculatingManual] = useState(false);

  const API_URL = 'http://localhost:8000';

  const TRANSLATIONS = {
    en: {
      title: "Transcription Validator",
      subtitle: "Stated Accuracy & Error Analysis",
      loading: "Loading Validator...",
      context: "Active Call Context",
      hypothesis: "AI Hypothesis (Hypothesis)",
      hypothesisPlaceholder: "What the system thought it heard...",
      reference: "Reference Text (Ground Truth)",
      referencePlaceholder: "Type your correction here...",
      calculate: "CALCULATE ACCURACY",
      calculating: "CALCULATING...",
      result: "Result",
      verifiedVia: "Verified via Word Error Rate (WER)",
      manualAccuracy: "Manual Comparison Accuracy",
      matchedWords: "Matched Words",
      discrepancies: "Discrepancies",
      substitutions: "Substitutions",
      deletions: "Deletions",
      insertions: "Insertions",
      werMetric: "WER Metric",
      bleuTitle: "Transcription BLEU (n-gram precision)",
      cudaTitle: "Transcription CUDA (Content Integrity)",
      score: "Score",
      avg: "Avg",
      comp: "Comp",
      acc: "Acc",
      det: "Det"
    },
    ja: {
      title: "文字起こしバリデータ",
      subtitle: "精度統計 & エラー分析",
      loading: "バリデータ読み込み中...",
      context: "現在の通話コンテキスト",
      hypothesis: "AI仮説 (認識結果)",
      hypothesisPlaceholder: "システムが認識した内容...",
      reference: "参照テキスト (正解データ)",
      referencePlaceholder: "修正後のテキストを入力してください...",
      calculate: "精度を計算する",
      calculating: "計算中...",
      result: "判定結果",
      verifiedVia: "単語誤り率 (WER) による検証",
      manualAccuracy: "手動比較精度",
      matchedWords: "一致単語数",
      discrepancies: "不一致数",
      substitutions: "置換 (Substitutions)",
      deletions: "削除 (Deletions)",
      insertions: "挿入 (Insertions)",
      werMetric: "WER指標",
      bleuTitle: "文字起こし BLEU (n-gram 精度)",
      cudaTitle: "文字起こし CUDA (内容の完全性)",
      score: "スコア",
      avg: "平均",
      comp: "網羅性",
      acc: "正確性",
      det: "詳細度"
    }
  };

  const t = TRANSLATIONS[systemLanguage] || TRANSLATIONS.en;

  const fetchQualityMetrics = async () => {
    if (!callId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/calls/${callId}/quality?lang=${systemLanguage}`);

      if (!response.ok) {
        throw new Error('Failed to fetch quality metrics');
      }

      const data = await response.json();
      setQualityData({
        transcription: data.transcription
      });

      if (data.transcript) {
        setLiveTestText(data.transcript);
      }
    } catch (err) {
      console.error("Quality fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleManualCalculation = async () => {
    if (!liveReferenceText) {
      alert(systemLanguage === 'ja' ? "比較用の参照テキストを入力してください。" : "Please enter a reference text to compare against.");
      return;
    }

    setIsCalculatingManual(true);
    try {
      const response = await fetch(`${API_URL}/api/quality/calculate-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hypothesis_soap: { subjective: '', objective: '', assessment: '', plan: '' },
          reference_soap: { subjective: '', objective: '', assessment: '', plan: '' },
          hypothesis_transcript: liveTestText,
          reference_transcript: liveReferenceText,
          language: systemLanguage
        })
      });

      if (!response.ok) throw new Error('Calculation failed');
      const data = await response.json();

      setQualityData({
        transcription: data.transcription
      });
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setIsCalculatingManual(false);
    }
  };

  useEffect(() => {
    fetchQualityMetrics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callId, systemLanguage]);

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.6) return 'text-yellow-500';
    if (score >= 0.4) return 'text-orange-500';
    return 'text-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-cyan-500 flex flex-col items-center">
          <RefreshCw className="h-12 w-12 animate-spin mb-4" />
          <p className="font-black uppercase tracking-widest">{t.loading}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6 font-sans text-white">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-10">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 flex items-center justify-between shadow-2xl">
          <div className="flex items-center space-x-6">
            <button onClick={onBack} className="bg-slate-800 hover:bg-slate-700 p-3 rounded-2xl text-white transition-all">
              <ArrowLeft className="h-6 w-6" />
            </button>
            <div>
              <h1 className="text-4xl font-black tracking-tighter uppercase italic">{t.title}</h1>
              <p className="text-cyan-500 font-bold text-sm tracking-widest uppercase mt-1">{t.subtitle}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="bg-slate-800 px-4 py-2 rounded-xl border border-slate-700">
              <span className="text-slate-500 text-[10px] block font-black uppercase tracking-widest">{t.context}</span>
              <span className="text-white font-mono text-xs">{callId}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Console */}
      <div className="max-w-7xl mx-auto mb-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="space-y-4">
            <label className="text-white text-[10px] font-black uppercase tracking-[0.3em] flex items-center px-4">
              <Zap className="h-4 w-4 mr-2 text-cyan-400" />
              {t.hypothesis}
            </label>
            <textarea
              value={liveTestText}
              onChange={(e) => setLiveTestText(e.target.value)}
              className="w-full h-[400px] bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] p-10 text-white text-xl leading-relaxed focus:outline-none focus:border-cyan-500 transition-all font-medium shadow-2xl"
              placeholder={t.hypothesisPlaceholder}
            />
          </div>

          <div className="space-y-4">
            <label className="text-white text-[10px] font-black uppercase tracking-[0.3em] flex items-center px-4">
              <Target className="h-4 w-4 mr-2 text-yellow-500" />
              {t.reference}
            </label>
            <textarea
              value={liveReferenceText}
              onChange={(e) => setLiveReferenceText(e.target.value)}
              className="w-full h-[400px] bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] p-10 text-white text-xl leading-relaxed focus:outline-none focus:border-yellow-500 transition-all font-medium shadow-2xl"
              placeholder={t.referencePlaceholder}
            />
          </div>
        </div>

        <div className="mt-10 flex justify-center">
          <button
            onClick={handleManualCalculation}
            disabled={isCalculatingManual}
            className="group px-16 py-8 bg-white text-black text-2xl font-black rounded-full hover:bg-cyan-400 hover:text-white transition-all flex items-center space-x-4 shadow-[0_30px_60px_rgba(0,0,0,0.6)] active:scale-95 disabled:opacity-50"
          >
            {isCalculatingManual ? <RefreshCw className="h-8 w-8 animate-spin" /> : <TrendingUp className="h-8 w-8" />}
            <span>{isCalculatingManual ? t.calculating : t.calculate}</span>
          </button>
        </div>
      </div>

      {/* Results View */}
      {qualityData && qualityData.transcription && (
        <div className="max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-10 duration-700">
          <div className={`rounded-[4rem] p-16 border-4 ${qualityData.transcription.accuracy > 80 ? 'border-green-500/30' : 'border-red-500/30'} bg-slate-900 shadow-2xl relative overflow-hidden group`}>
            <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 blur-[120px] rounded-full -mr-48 -mt-48 transition-all group-hover:bg-cyan-500/10"></div>

            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-16">
              <div className="text-center md:text-left">
                <h2 className="text-white text-7xl font-black tracking-tighter uppercase mb-2 italic">{t.result}</h2>
                <div className="flex items-center text-slate-500 text-xs font-black uppercase tracking-widest">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  {t.verifiedVia}
                </div>
              </div>

              <div className="flex flex-col items-center">
                <div className={`text-[160px] font-black leading-none tracking-tighter ${getScoreColor(qualityData.transcription.accuracy / 100)}`}>
                  {qualityData.transcription.accuracy}%
                </div>
                <div className="text-slate-500 font-black uppercase tracking-widest text-sm mt-4">{t.manualAccuracy}</div>
              </div>

              <div className="flex flex-col gap-6 w-full md:w-80">
                <div className="bg-slate-950 p-8 rounded-[2rem] border border-slate-800 text-center transition-all hover:border-green-500/50">
                  <span className="text-green-500 text-6xl font-black block leading-none mb-2">{qualityData.transcription.correct_words}</span>
                  <span className="text-slate-600 text-[10px] font-black uppercase tracking-widest">{t.matchedWords}</span>
                </div>
                <div className="bg-slate-950 p-8 rounded-[2rem] border border-slate-800 text-center transition-all hover:border-red-500/50">
                  <span className="text-red-500 text-6xl font-black block leading-none mb-2">{qualityData.transcription.errors}</span>
                  <span className="text-slate-600 text-[10px] font-black uppercase tracking-widest">{t.discrepancies}</span>
                </div>
              </div>
            </div>

            <div className="mt-16 pt-16 border-t border-slate-800 grid grid-cols-2 md:grid-cols-4 gap-8">
              <ResultStatistic label={t.substitutions} value={qualityData.transcription.substitutions} color="text-yellow-500" />
              <ResultStatistic label={t.deletions} value={qualityData.transcription.deletions} color="text-orange-500" />
              <ResultStatistic label={t.insertions} value={qualityData.transcription.insertions} color="text-purple-500" />
              <ResultStatistic label={t.werMetric} value={`${qualityData.transcription.wer_percentage}%`} color="text-cyan-500" />
            </div>

            {/* Transcription-level BLEU & CUDA */}
            <div className="mt-10 pt-10 border-t border-slate-800/50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="bg-slate-950/50 p-6 rounded-3xl border border-slate-800">
                  <h4 className="text-cyan-400 text-[10px] font-black uppercase tracking-widest mb-4 flex items-center">
                    <Zap className="h-3 w-3 mr-2" />
                    {t.bleuTitle}
                  </h4>
                  <div className="grid grid-cols-4 gap-4">
                    <MiniMetric label="B1" value={qualityData.transcription.bleu?.bleu_1 || 0} />
                    <MiniMetric label="B2" value={qualityData.transcription.bleu?.bleu_2 || 0} />
                    <MiniMetric label="B3" value={qualityData.transcription.bleu?.bleu_3 || 0} />
                    <MiniMetric label="Avg" value={qualityData.transcription.bleu?.bleu_avg || 0} highlight />
                  </div>
                </div>

                <div className="bg-slate-950/50 p-6 rounded-3xl border border-slate-800">
                  <h4 className="text-purple-400 text-[10px] font-black uppercase tracking-widest mb-4 flex items-center">
                    <Target className="h-3 w-3 mr-2" />
                    {t.cudaTitle}
                  </h4>
                  <div className="grid grid-cols-4 gap-4">
                    <MiniMetric label={t.comp} value={qualityData.transcription.cuda?.completion || 0} />
                    <MiniMetric label={t.acc} value={qualityData.transcription.cuda?.accuracy || 0} />
                    <MiniMetric label={t.det} value={qualityData.transcription.cuda?.detail || 0} />
                    <MiniMetric label={t.score} value={qualityData.transcription.cuda?.cuda_overall || 0} highlight />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MiniMetric({ label, value, highlight }) {
  return (
    <div className="text-center">
      <span className="text-[9px] text-slate-600 block uppercase font-bold mb-1">{label}</span>
      <span className={`text-xl font-black ${highlight ? 'text-white' : 'text-slate-400'}`}>
        {typeof value === 'number' ? value.toFixed(2) : value}
      </span>
    </div>
  );
}

function ResultStatistic({ label, value, color }) {
  return (
    <div className="text-center md:text-left">
      <span className="text-slate-600 text-[10px] font-black uppercase tracking-[0.2em] block mb-2">{label}</span>
      <span className={`text-3xl font-black ${color} tracking-tight`}>{value}</span>
    </div>
  );
}

export default BleuScoreQualityMetrics;