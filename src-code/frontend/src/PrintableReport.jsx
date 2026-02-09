import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Activity, Phone, User, AlertCircle, FileText, ClipboardList } from 'lucide-react';

const TRANSLATIONS = {
    en: {
        title: "EMERGENCY CLINICAL REPORT",
        generated: "Generated on",
        summary: "Call Summary",
        patient: "Patient Identity",
        triage: "Triage Assessment",
        soap: "Clinical SOAP Notes",
        transcript: "Full Transcript",
        reasoning: "Urgency Reasoning",
        callId: "Call ID",
        name: "Name",
        age: "Age",
        phone: "Phone",
        blood: "Blood Type",
        address: "Incident Address",
        urgency: "Urgency Level",
        score: "Urgency Score",
        subjective: "Subjective (S)",
        objective: "Objective (O)",
        assessment: "Assessment (A)",
        plan: "Plan (P)",
        critical: "CRITICAL",
        high: "HIGH",
        medium: "MEDIUM",
        low: "LOW",
        noData: "No data available for this call."
    },
    ja: {
        title: "救急臨床報告書 (MEDICAL REPORT)",
        generated: "作成日時",
        summary: "通報サマリー",
        patient: "患者基本情報",
        triage: "トリアージ評価",
        soap: "SOAP臨床記録",
        transcript: "臨床音声文字起こし",
        reasoning: "緊急度判定の根拠",
        callId: "通報ID",
        name: "氏名",
        age: "年齢",
        phone: "電話番号",
        blood: "血液型",
        address: "発生現場住所",
        urgency: "緊急度レベル",
        score: "緊急度スコア",
        subjective: "主観的所見 (S)",
        objective: "客観的所見 (O)",
        assessment: "評価 (A)",
        plan: "対応計画 (P)",
        critical: "最優先 (CRITICAL)",
        high: "緊急 (HIGH)",
        medium: "中等度 (MEDIUM)",
        low: "低緊急 (LOW)",
        noData: "該当するデータが見つかりません。"
    }
};

const PrintableReport = () => {
    const [searchParams] = useSearchParams();
    const lang = searchParams.get('lang') || 'en';
    const callId = searchParams.get('id'); // if null, export all
    const [calls, setCalls] = useState([]);
    const [loading, setLoading] = useState(true);
    const t = TRANSLATIONS[lang] || TRANSLATIONS.en;

    useEffect(() => {
        const API_BASE = `http://${window.location.hostname}:8000`; //we call 8000 port and not 3000because we need back end for pdf report to bring data from database 

        const fetchAllData = async () => {
            try {
                let url = `${API_BASE}/api/calls?lang=${lang}`;
                if (callId) {
                    url = `${API_BASE}/api/calls/${callId}?lang=${lang}`;
                }

                const response = await fetch(url); //fetch means get data from the server
                const data = await response.json();

                const normalizeCall = (raw) => {
                    return {
                        ...raw, //raw means the data we get from the server is the original object from the server 
                        // the 3 points copies all existing fields from raw- into the new object->so nothing is lost 
                        urgency_level: raw.urgency?.level || raw.urgency_level, //If raw.urgency exists → use .level else If raw.urgency is null or undefined → don’t crash, return undefined then comes the nested property after or raw.urgency_level
                        urgency_score: raw.urgency?.score || raw.urgency_score,
                        urgency_reasoning: raw.urgency?.reasoning || raw.urgency_reasoning,
                        soap_subjective: raw.soap?.subjective || raw.soap_subjective,
                        soap_objective: raw.soap?.objective || raw.soap_objective,
                        soap_assessment: raw.soap?.assessment || raw.soap_assessment,
                        soap_plan: raw.soap?.plan || raw.soap_plan,
                    };
                };

                if (callId) {
                    // API returns a single object for details, normalize it
                    setCalls([normalizeCall(data)]);
                } else {
                    const normalizedList = (data.calls || []).map(c => normalizeCall(c));
                    setCalls(normalizedList);
                }

                setLoading(false);
                // Auto trigger print after a small delay for rendering - reduced delay for faster UX
                setTimeout(() => {
                    window.print();
                }, 500);
            } catch (err) {
                console.error("Failed to fetch report data", err);
                setLoading(false);
            }
        };
        fetchAllData();
    }, [callId, lang]);

    const parseField = (text, fieldName) => {
        if (!text) return 'N/A';
        const translations = {
            'Name': ['Name', '氏名', '名前', '患者名'],
            'Age': ['Age', '年齢', '歳'],
            'Address': ['Address', '住所', '現場', '場所', 'Location', 'Incident location'],
            'Phone': ['Phone', '電話', '連絡先', 'Callback', 'Contact'],
            'Blood': ['Blood', '血液型', 'Blood type', 'Blood Type'],
            'Sex': ['Sex', 'Gender', '性別']
        };
        const keys = translations[fieldName] || [fieldName];
        for (const key of keys) {
            const patterns = [
                new RegExp(`${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'i'),
                new RegExp(`\\*\\s*${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'i'),
                new RegExp(`^${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'im'),
            ];
            for (const pattern of patterns) {
                const match = text.match(pattern);
                if (match && match[1]) {
                    const val = match[1].trim()
                        .replace(/^[:：\s*-]+/, '')
                        .replace(/\s*\*+\s*$/, '');

                    // Filter out placeholder values and ensure it's valid data
                    if (val.length > 0 &&
                        val !== 'N/A' &&
                        !val.match(/^\\[.*\\]$/) &&  // Avoid [Name], [不明], etc.
                        !val.toLowerCase().includes('not provided') &&
                        !val.includes('不明')) {
                        return val;
                    }
                }
            }
        }
        return lang === 'ja' ? '[不明]' : 'N/A';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-white flex flex-col items-center justify-center p-10">
                <div className="w-12 h-12 border-4 border-zinc-200 border-t-red-600 rounded-full animate-spin mb-4"></div>
                <p className="text-zinc-500 font-bold uppercase tracking-widest text-[10px] animate-pulse">
                    {lang === 'ja' ? 'レポートを準備中...' : 'PREPARING MEDICAL REPORT...'}
                </p>
            </div>
        );
    }

    if (!calls || calls.length === 0) return <div className="p-10 text-zinc-500 font-mono italic">{t.noData}</div>;

    return (
        <div className="bg-white min-h-screen text-black p-4 font-sans selection:bg-blue-100">
            <style>{`
        @media print {
          body { background: white; }
          .no-print { display: none; }
          .page-break { page-break-after: always; }
          @page { margin: 1cm; }
        }
      `}</style>

            {calls.map((call, index) => (
                <div key={call.call_id} className={`max-w-4xl mx-auto ${index < calls.length - 1 ? 'page-break' : ''} mb-4`}>
                    {/* Header */}
                    <div className="border-b-2 border-black pb-3 mb-4 flex justify-between items-end">
                        <div>
                            <div className="flex items-center space-x-2 mb-1">
                                <Activity className="h-5 w-5 text-red-600" />
                                <span className="font-black text-[9px] tracking-widest text-zinc-400 uppercase">REDSS MEDICAL NETWORK</span>
                            </div>
                            <h1 className="text-xl font-black tracking-tighter uppercase">{t.title}</h1>
                        </div>
                        <div className="text-right">
                            <div className="text-[8px] font-bold text-zinc-400 uppercase mb-0.5">{t.generated}</div>
                            <div className="text-[10px] font-mono">{new Date().toLocaleString(lang === 'ja' ? 'ja-JP' : 'en-US')}</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                        {/* Call Info */}
                        <div className="bg-zinc-50 p-3 border border-zinc-200">
                            <div className="flex items-center space-x-2 mb-2 border-b border-zinc-200 pb-1">
                                <Phone size={12} className="text-zinc-400" />
                                <span className="text-[10px] font-bold uppercase tracking-widest">{t.summary}</span>
                            </div>
                            <div className="space-y-1">
                                <div className="flex justify-between items-baseline">
                                    <span className="text-[8px] font-bold text-zinc-500 uppercase">{t.callId}</span>
                                    <span className="text-[10px] font-mono font-bold tracking-tight">{call.call_id}</span>
                                </div>
                                <div className="flex justify-between items-baseline pt-1 mt-1 border-t border-zinc-100">
                                    <span className="text-[8px] font-bold text-zinc-500 uppercase">{t.urgency}</span>
                                    <span className="text-xs font-black text-red-600 uppercase italic tracking-tighter">
                                        {t[call.urgency_level?.toLowerCase()] || call.urgency_level}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Patient Identity */}
                        <div className="bg-zinc-50 p-3 border border-zinc-200">
                            <div className="flex items-center space-x-2 mb-2 border-b border-zinc-200 pb-1">
                                <User size={12} className="text-zinc-400" />
                                <span className="text-[10px] font-bold uppercase tracking-widest">{t.patient}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                                <div>
                                    <div className="text-[8px] font-bold text-zinc-400 uppercase">{t.name}</div>
                                    <div className="text-[10px] font-bold">{call.patient_name || parseField(call.soap_objective, 'Name')}</div>
                                </div>
                                <div>
                                    <div className="text-[8px] font-bold text-zinc-400 uppercase">{t.age}</div>
                                    <div className="text-[10px] font-bold">{parseField(call.soap_objective, 'Age')}</div>
                                </div>
                                <div className="col-span-2 pt-1 mt-1 border-t border-zinc-100">
                                    <div className="text-[8px] font-bold text-zinc-400 uppercase">{t.address}</div>
                                    <div className="text-[10px] leading-tight truncate">{parseField(call.soap_objective, 'Address')}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mb-4">
                        <div className="flex items-center space-x-2 mb-2 border-b-2 border-black pb-1">
                            <ClipboardList size={16} />
                            <h2 className="text-md font-black uppercase italic tracking-tighter">{t.soap}</h2>
                        </div>

                        <div className="space-y-3">
                            <section>
                                <h3 className="text-[10px] font-black uppercase text-blue-800 mb-0.5 flex items-center">
                                    <span className="w-1 h-1 bg-blue-800 rounded-full mr-1.5"></span>
                                    {t.subjective}
                                </h3>
                                <p className="text-[11px] leading-snug text-zinc-700 whitespace-pre-wrap line-clamp-4">{call.soap_subjective || 'N/A'}</p>
                            </section>

                            <section>
                                <h3 className="text-[10px] font-black uppercase text-emerald-800 mb-0.5 flex items-center">
                                    <span className="w-1 h-1 bg-emerald-800 rounded-full mr-1.5"></span>
                                    {t.objective}
                                </h3>
                                <p className="text-[11px] leading-snug text-zinc-700 whitespace-pre-wrap line-clamp-4">{call.soap_objective || 'N/A'}</p>
                            </section>

                            <section>
                                <h3 className="text-[10px] font-black uppercase text-yellow-800 mb-0.5 flex items-center">
                                    <span className="w-1 h-1 bg-yellow-800 rounded-full mr-1.5"></span>
                                    {t.assessment}
                                </h3>
                                <p className="text-[11px] leading-snug text-zinc-700 whitespace-pre-wrap line-clamp-3">{call.soap_assessment || 'N/A'}</p>
                            </section>

                            <section>
                                <h3 className="text-[10px] font-black uppercase text-purple-800 mb-0.5 flex items-center">
                                    <span className="w-1 h-1 bg-purple-800 rounded-full mr-1.5"></span>
                                    {t.plan}
                                </h3>
                                <p className="text-[11px] leading-snug text-zinc-700 whitespace-pre-wrap line-clamp-3">{call.soap_plan || 'N/A'}</p>
                            </section>
                        </div>
                    </div>

                    {/* Reasoning & Transcript */}
                    <div className="border-t border-zinc-100 pt-4">
                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <div className="flex items-center space-x-2 mb-2">
                                    <AlertCircle size={14} className="text-red-500" />
                                    <h3 className="text-[10px] font-black uppercase tracking-widest">{t.reasoning}</h3>
                                </div>
                                <p className="text-[10px] text-zinc-500 italic leading-tight line-clamp-4">{call.urgency_reasoning || 'N/A'}</p>
                            </div>
                            <div>
                                <div className="flex items-center space-x-2 mb-2">
                                    <FileText size={14} className="text-zinc-400" />
                                    <h3 className="text-[10px] font-black uppercase tracking-widest">{t.transcript}</h3>
                                </div>
                                <p className="text-[9px] text-zinc-400 font-mono leading-tight bg-zinc-50 p-2 rounded line-clamp-5 border border-zinc-100 whitespace-pre-wrap">
                                    {call.transcript || 'N/A'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Bottom Footer */}
                    <div className="mt-12 pt-4 border-t border-zinc-100 text-[10px] text-zinc-400 flex justify-between uppercase font-bold tracking-widest">
                        <span>OFFICIAL MEDICAL RECORD</span>
                        <span>SYSTEM ID: {call.id}</span>
                        <span>CONFIDENTIAL</span>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default PrintableReport;
