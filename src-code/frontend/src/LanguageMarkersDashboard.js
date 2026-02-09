import React, { useState, useEffect } from 'react';
import {
  Brain, AlertTriangle, CheckCircle, MessageCircle,
  Zap, Activity, BarChart3, ArrowLeft, RefreshCw
} from 'lucide-react';

function LanguageMarkersDashboard({ callId, onBack, systemLanguage = 'en' }) {
  const [markers, setMarkers] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyzedText, setAnalyzedText] = useState('');
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [isAnalyzingLive, setIsAnalyzingLive] = useState(false);
  const API_URL = 'http://localhost:8000';

  const TRANSLATIONS = {
    en: {
      title: "Marker Analysis",
      subtitle: "AI-Powered Dementia Risk Assessment",
      riskAssessment: "Overall Assessment",
      riskLevel: "RISK",
      riskScore: "Risk Score",
      confidence: "Confidence",
      recommendation: "AI Recommendation",
      conversationalAdherence: "Conversational adherence (GRI Score)",
      fluencyTitle: "Speech Fluency",
      cognitiveTitle: "Cognitive Markers",
      complexityTitle: "Language Complexity",
      semanticTitle: "Semantic Markers",
      analyzing: "Analyzing language markers...",
      noSelected: "No call selected",
      incompleteData: "Incomplete data for this call",
      goBack: "Go Back",
      refresh: "Refresh Analysis",
      stable: "STABLE",
      noDementia: "No Dementia detected",
      high: "HIGH",
      medium: "MEDIUM",
      low: "LOW",
      risk: "RISK"
    },
    ja: {
      title: "言語マーカー分析",
      subtitle: "AIによる認知症リスク評価",
      riskAssessment: "総合評価",
      riskLevel: "リスク",
      riskScore: "リスクスコア",
      confidence: "確信度",
      recommendation: "AI推奨事項",
      conversationalAdherence: "会話の流暢性 (GRIスコア)",
      fluencyTitle: "発話の流暢性",
      cognitiveTitle: "認知機能指標",
      complexityTitle: "言語の複雑性",
      semanticTitle: "意味論的指標",
      analyzing: "言語マーカーを分析中...",
      noSelected: "通報が選択されていません",
      incompleteData: "この通報には不完全なデータがあります",
      goBack: "戻る",
      refresh: "分析を更新",
      stable: "安定",
      noDementia: "認知症の兆候なし",
      high: "高リスク",
      medium: "中リスク",
      low: "低リスク",
      risk: "リスク"
    }
  };

  const t = TRANSLATIONS[systemLanguage] || TRANSLATIONS.en;

  const fetchMarkers = async () => {
    if (!callId) {
      setError(t.noSelected);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/calls/${callId}/markers?lang=${systemLanguage}`);

      if (!response.ok) {
        throw new Error('Failed to fetch markers');
      }

      const data = await response.json();
      setMarkers(data);

      // Fetch the actual transcript from emergency_calls table to show it
      const callResp = await fetch(`${API_URL}/api/calls/${callId}`);
      if (callResp.ok) {
        const callData = await callResp.json();
        setAnalyzedText(callData.transcript || '');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLiveAnalysis = async () => {
    if (!analyzedText || analyzedText.trim().length < 5) return;
    setIsAnalyzingLive(true);
    try {
      const response = await fetch(`${API_URL}/api/analyze-markers?lang=${systemLanguage}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: analyzedText, call_id: callId })
      });
      if (!response.ok) throw new Error("Analysis failed");
      const data = await response.json();
      setMarkers(data);
      setIsLiveMode(true);
    } catch (err) {
      alert(err.message);
    } finally {
      setIsAnalyzingLive(false);
    }
  };

  useEffect(() => {
    fetchMarkers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callId, systemLanguage]);

  const getRiskColor = (level) => {
    const colors = {
      'HIGH': 'bg-red-500',
      'MEDIUM': 'bg-yellow-500',
      'LOW': 'bg-green-500',
      'NORMAL': 'bg-blue-500'
    };
    return colors[level] || 'bg-gray-500';
  };

  const getRiskBorder = (level) => {
    const borders = {
      'HIGH': 'border-red-500',
      'MEDIUM': 'border-yellow-500',
      'LOW': 'border-green-500',
      'NORMAL': 'border-blue-500'
    };
    return borders[level] || 'border-gray-500';
  };

  const getRiskIcon = (level) => {
    if (level === 'HIGH') return <AlertTriangle className="h-5 w-5" />;
    if (level === 'MEDIUM') return <Activity className="h-5 w-5" />;
    return <CheckCircle className="h-5 w-5" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 p-6 flex flex-col items-center justify-center">
        <div className="text-purple-500 flex flex-col items-center">
          <RefreshCw className="h-12 w-12 animate-spin mb-4" />
          <p className="font-black uppercase tracking-widest">{t.analyzing}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-white text-xl mb-4">Error: {error}</p>
          <button onClick={onBack} className="px-6 py-3 bg-slate-800 text-white rounded-lg">
            {t.goBack}
          </button>
        </div>
      </div>
    );
  }

  const griTranslations = {
    quantity: systemLanguage === 'ja' ? '情報量' : 'Quantity',
    quality: systemLanguage === 'ja' ? '品質' : 'Quality',
    relation: systemLanguage === 'ja' ? '関連性' : 'Relation',
    manner: systemLanguage === 'ja' ? '妥当性' : 'Manner'
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6 font-sans text-white">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex items-center justify-between shadow-2xl">
          <div className="flex items-center space-x-6">
            <button onClick={onBack} className="bg-slate-800 hover:bg-slate-700 p-3 rounded-2xl text-white transition-all">
              <ArrowLeft className="h-6 w-6" />
            </button>
            <div className="flex items-center gap-4">
              <div className="bg-purple-600 p-3 rounded-xl shadow-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-black tracking-tight uppercase italic">{t.title}</h1>
                <p className="text-purple-400 font-bold text-xs tracking-widest uppercase">{t.subtitle}</p>
              </div>
            </div>
          </div>
          <div className="text-right flex items-center gap-4">
            <div className="bg-slate-800 px-4 py-2 rounded-xl border border-slate-700">
              <span className="text-slate-500 text-[10px] block font-black uppercase tracking-widest">Analysis ID</span>
              <span className="text-white font-mono text-xs">{markers?.call_id || callId}</span>
            </div>
            <button onClick={fetchMarkers} className="p-3 bg-slate-800 hover:bg-slate-700 rounded-xl transition-all">
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-8">

        {/* Source Text Analysis Box */}
        <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl overflow-hidden relative">
          <div className={`absolute top-0 left-0 w-2 h-full transition-all duration-500 ${isLiveMode ? 'bg-yellow-500 shadow-[0_0_20px_rgba(234,179,8,0.5)]' : 'bg-purple-500'}`}></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="flex justify-between items-center mb-4">
                <label className="text-white text-[10px] font-black uppercase tracking-[0.2em] flex items-center px-2">
                  {isLiveMode ? <Zap className="h-4 w-4 mr-2 text-yellow-500" /> : <MessageCircle className="h-4 w-4 mr-2 text-purple-400" />}
                  {isLiveMode ? "LIVE ANALYSIS (Custom Text)" : "SOURCE TRANSCRIPT (Database Reference)"}
                </label>
                {isLiveMode && (
                  <button
                    onClick={() => { setIsLiveMode(false); fetchMarkers(); }}
                    className="text-[9px] bg-slate-800 hover:bg-slate-700 text-slate-400 px-3 py-1 rounded-full border border-slate-700 font-black uppercase"
                  >
                    Reset to Original
                  </button>
                )}
              </div>
              <textarea
                value={analyzedText}
                onChange={(e) => setAnalyzedText(e.target.value)}
                className="w-full h-40 bg-slate-950/50 border-2 border-slate-800 rounded-3xl p-6 text-white text-lg leading-relaxed focus:outline-none focus:border-purple-500 transition-all font-medium"
                placeholder="Enter text to analyze linguistic markers..."
              />
              <div className="mt-4 flex justify-between items-center px-2">
                <p className="text-slate-500 text-[10px] font-black uppercase">
                  {analyzedText.split(' ').filter(w => w).length} Words | {analyzedText.length} Chars
                </p>
                <button
                  onClick={handleLiveAnalysis}
                  disabled={isAnalyzingLive}
                  className="bg-white text-black px-6 py-2 rounded-full font-black text-[10px] tracking-widest hover:bg-purple-500 hover:text-white transition-all flex items-center space-x-2 shadow-xl"
                >
                  {isAnalyzingLive ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Activity className="h-4 w-4" />}
                  <span>{isAnalyzingLive ? "ANALYZING..." : "RE-ANALYZE THIS TEXT"}</span>
                </button>
              </div>
            </div>

            <div className="bg-slate-950/50 rounded-3xl p-6 border border-white/5 flex flex-col justify-center">
              <h3 className="text-white text-[10px] font-black uppercase tracking-widest mb-4 flex items-center">
                <Brain className="h-4 w-4 mr-2 text-purple-400" />
                Clinical Reference Logic
              </h3>
              <p className="text-slate-400 text-[11px] leading-relaxed mb-6 italic font-medium">
                This module analyzes the text on the left as its primary <b>Source Reference</b>. It detects patterns like topic drift, lexical poverty (TTR), and fluency gaps.
              </p>
              <div className="space-y-3">
                <div className="flex justify-between text-[10px] uppercase font-black border-b border-white/5 pb-2">
                  <span className="text-slate-500">TTR Range</span>
                  <span className="text-purple-400">0.50 - 0.70</span>
                </div>
                <div className="flex justify-between text-[10px] uppercase font-black border-b border-white/5 pb-2">
                  <span className="text-slate-500">Guiraud Index</span>
                  <span className="text-cyan-400">7.0 - 12.0</span>
                </div>
                <div className="flex justify-between text-[10px] uppercase font-black">
                  <span className="text-slate-500">Normal Speed</span>
                  <span className="text-blue-400">120-150 WPM</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Overall Assessment */}
        {markers && (
          <div className={`bg-slate-900 border-l-8 ${getRiskBorder(markers.overall_assessment.risk_level)} rounded-[2.5rem] p-8 shadow-2xl`}>
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-black italic tracking-tighter uppercase flex items-center">
                <AlertTriangle className="h-8 w-8 mr-3 text-red-500" />
                {t.riskAssessment}
              </h2>
              <div className={`px-6 py-3 rounded-2xl font-black text-lg ${getRiskColor(markers.overall_assessment.risk_level)} text-white`}>
                {markers.overall_assessment.risk_level} {t.risk}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-slate-800/50 rounded-3xl p-6 border border-white/5 flex flex-col items-center">
                <p className="text-slate-500 text-[10px] mb-4 font-black uppercase tracking-widest w-full">{t.riskScore}</p>
                <TachometerGauge value={markers.overall_assessment.dementia_risk_score.toFixed(1)} label={t.riskLevel} unit="%" riskLevel={markers.overall_assessment.risk_level} />
              </div>
              <div className="bg-slate-800/50 rounded-3xl p-6 border border-white/5 flex flex-col items-center">
                <p className="text-slate-500 text-[10px] mb-4 font-black uppercase tracking-widest w-full">{t.confidence}</p>
                <TachometerGauge value={markers.overall_assessment.confidence.toFixed(1)} label={t.confidence} unit="%" riskLevel="NORMAL" />
              </div>
              <div className="bg-slate-800/50 rounded-3xl p-8 border border-white/5 flex flex-col justify-center">
                <p className="text-slate-500 text-[10px] mb-2 font-black uppercase tracking-widest">{t.recommendation}</p>
                <p className="text-2xl font-black text-white leading-tight italic uppercase">
                  {markers.overall_assessment.recommendation.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* GRI Breakdown */}
        {markers?.linguistic?.gri_score && (
          <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-8 shadow-2xl">
            <h2 className="text-xl font-black italic uppercase mb-8 flex items-center">
              <Activity className="h-6 w-6 mr-3 text-blue-400" />
              {t.conversationalAdherence}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(markers.linguistic.gri_score.subscores).map(([key, value]) => (
                <div key={key} className="bg-slate-950 p-6 rounded-3xl border border-white/5 group hover:border-blue-500/30 transition-all">
                  <p className="text-slate-500 text-[10px] font-black uppercase mb-4 tracking-widest group-hover:text-blue-400">
                    {griTranslations[key] || key}
                  </p>
                  <div className="flex items-end justify-between mb-2">
                    <span className="text-3xl font-black">{value}</span>
                    <span className="text-[10px] text-slate-600 font-black mb-1">/ 100</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div className={`h-full bg-blue-500 transition-all duration-1000`} style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Marker Categories */}
        {markers && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pb-12">
            <MarkerCategory title={t.fluencyTitle} icon={<MessageCircle className="h-6 w-6" />} color="blue" markers={markers.speech_fluency || {}} getRiskColor={getRiskColor} getRiskBorder={getRiskBorder} getRiskIcon={getRiskIcon} systemLanguage={systemLanguage} />
            <MarkerCategory title={t.cognitiveTitle} icon={<Brain className="h-6 w-6" />} color="red" markers={markers.cognitive || {}} getRiskColor={getRiskColor} getRiskBorder={getRiskBorder} getRiskIcon={getRiskIcon} systemLanguage={systemLanguage} />
            <MarkerCategory title={t.complexityTitle} icon={<BarChart3 className="h-6 w-6" />} color="purple" markers={markers.linguistic || {}} getRiskColor={getRiskColor} getRiskBorder={getRiskBorder} getRiskIcon={getRiskIcon} systemLanguage={systemLanguage} />
            <MarkerCategory title={t.semanticTitle} icon={<Zap className="h-6 w-6" />} color="yellow" markers={markers.semantic || {}} getRiskColor={getRiskColor} getRiskBorder={getRiskBorder} getRiskIcon={getRiskIcon} systemLanguage={systemLanguage} />
          </div>
        )}
      </div>
    </div>
  );
}

function MarkerCategory({ title, icon, color, markers, getRiskColor, getRiskBorder, getRiskIcon, systemLanguage }) {
  const colorClasses = {
    blue: 'border-blue-500/30',
    red: 'border-red-500/30',
    purple: 'border-purple-500/30',
    yellow: 'border-yellow-500/30'
  };

  return (
    <div className={`bg-slate-900 border ${colorClasses[color]} rounded-[2.5rem] shadow-2xl overflow-hidden`}>
      <div className="bg-slate-800/50 px-8 py-4 border-b border-slate-800">
        <h2 className="text-lg font-black uppercase italic flex items-center">
          {icon}
          <span className="ml-3">{title}</span>
        </h2>
      </div>
      <div className="p-8 space-y-4">
        {Object.values(markers).map((marker, idx) => (
          <MarkerCard key={idx} marker={marker} getRiskColor={getRiskColor} getRiskBorder={getRiskBorder} getRiskIcon={getRiskIcon} systemLanguage={systemLanguage} />
        ))}
      </div>
    </div>
  );
}

function MarkerCard({ marker, getRiskColor, getRiskBorder, getRiskIcon, systemLanguage }) {
  const normalLabel = systemLanguage === 'ja' ? '正常範囲:' : 'Normal:';
  let min = 0;
  let max = 100;
  if (marker.unit === 'ratio' || marker.marker_name.includes('Ratio') || marker.marker_name.includes('TTR')) max = 1.0;
  else if (marker.unit === 'ms') max = 2000;
  else if (marker.value > 100) max = marker.value * 1.5;

  return (
    <div className={`bg-slate-950 rounded-2xl p-4 border-l-4 ${getRiskBorder(marker.risk_level)} shadow-lg`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-white font-black text-xs uppercase italic">{marker.marker_name}</h3>
          <p className="text-slate-500 text-[10px] mt-1 font-medium">{marker.description}</p>
        </div>
        <div className={`flex items-center space-x-1 text-white ${getRiskColor(marker.risk_level)} px-2 py-0.5 rounded text-[8px] font-black uppercase`}>
          {getRiskIcon(marker.risk_level)}
          <span>{marker.judgment}</span>
        </div>
      </div>
      <div className="flex justify-center py-2 scale-90">
        <TachometerGauge value={marker.value} min={min} max={max} unit={marker.unit} riskLevel={marker.risk_level} />
      </div>
      <div className="text-right border-t border-white/5 pt-2">
        <p className="text-slate-600 text-[9px] font-black">{normalLabel} <span className="text-slate-400 font-mono">{marker.normal_range}</span></p>
      </div>
    </div>
  );
}

function TachometerGauge({ value, min = 0, max = 100, label, unit, riskLevel }) {
  const safeValue = isNaN(parseFloat(value)) ? 0 : parseFloat(value);
  const normalizedValue = Math.min(Math.max((safeValue - min) / (max - min), 0), 1);
  const strokeWidth = 10;
  const angle = -90 + (normalizedValue * 180);

  let strokeColor = '#94a3b8';
  if (riskLevel === 'HIGH') strokeColor = '#ef4444';
  else if (riskLevel === 'MEDIUM') strokeColor = '#eab308';
  else if (riskLevel === 'LOW') strokeColor = '#22c55e';
  else if (riskLevel === 'NORMAL') strokeColor = '#3b82f6';

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="100" viewBox="0 0 200 120">
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1e293b" strokeWidth={strokeWidth} strokeLinecap="round" />
        <path d={`M 20 100 A 80 80 0 0 1 ${100 + 80 * Math.cos((180 + normalizedValue * 180) * Math.PI / 180)} ${100 + 80 * Math.sin((180 + normalizedValue * 180) * Math.PI / 180)}`} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} strokeLinecap="round" />
        <g transform={`translate(100, 90) rotate(${angle})`}>
          <path d="M -1.5 0 L 0 -45 L 1.5 0 Z" fill="white" />
          <circle cx="0" cy="0" r="3" fill="white" />
        </g>
      </svg>
      <div className="text-center -mt-4">
        <div className="text-xl font-black text-white">{value}<span className="text-[10px] text-slate-500 ml-1 font-normal">{unit}</span></div>
      </div>
    </div>
  );
}

export default LanguageMarkersDashboard;