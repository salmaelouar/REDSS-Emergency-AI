import React, { useState, useEffect, useRef } from 'react';
import {
    MapPin, Phone, AlertTriangle, Pill, Clock, Maximize, Minimize, Activity
} from 'lucide-react';

const TransparentMonitor = () => {
    const [currentCall, setCurrentCall] = useState(null);
    // eslint-disable-next-line
    const [calls, setCalls] = useState([]);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [liveData, setLiveData] = useState(null); // { transcript, call_id, status }
    const [language, setLanguage] = useState('en');
    const currentCallRef = useRef(currentCall);

    const TRANSLATIONS = {
        en: {
            caseId: "CASE ID",
            patientIdentity: "Patient Identity",
            age: "Age",
            sex: "Sex",
            blood: "Blood",
            location: "Location",
            medicalAlerts: "Medical Alerts / Allergies",
            noAllergies: "No known allergies",
            medications: "Medications",
            noMedications: "No medications recorded",
            situationSummary: "Situation Summary",
            urgencyScore: "Urgency Score",
            connection: "Connection",
            live: "LIVE",
            unknownPatient: "Unknown Patient",
            locationUnknown: "Location Unknown",
            unknownNumber: "Unknown Number",
            liveEmergencyCall: "Live Emergency Call",
            interpretingAudio: "Interpreting Audio Stream...",
            waitingSpeech: "Waiting for speech detection...",
            aiTranscription: "AI Transcription Active",
            realtimeSoap: "Real-Time SOAP Processing",
            autoSaving: "Auto-Saving Analysis",
            ready: "READY",
            waitingCall: "Waiting for emergency call",
            status: "STATUS",
            critical: "Critical",
            high: "High",
            medium: "Medium",
            low: "Low"
        },
        ja: {
            caseId: "ケースID",
            patientIdentity: "患者基本情報",
            age: "年齢",
            sex: "性別",
            blood: "血液型",
            location: "場所",
            medicalAlerts: "アレルギー・警告事項",
            noAllergies: "既知のアレルギーなし",
            medications: "服用薬",
            noMedications: "服用薬の情報なし",
            situationSummary: "状況概要",
            urgencyScore: "緊急度スコア",
            connection: "接続状態",
            live: "ライブ",
            unknownPatient: "不明な患者",
            locationUnknown: "場所不明",
            unknownNumber: "不明な番号",
            liveEmergencyCall: "緊急通話ライブ",
            interpretingAudio: "音声ストリーム解析中...",
            waitingSpeech: "音声検出待機中...",
            aiTranscription: "AI文字起こし稼働中",
            realtimeSoap: "リアルタイムSOAP解析",
            autoSaving: "自動保存中",
            ready: "待機中",
            waitingCall: "緊急通報を待っています",
            status: "ステータス",
            critical: "最優先(重症)",
            high: "高緊急度",
            medium: "中緊急度",
            low: "低緊急度"
        }
    };

    const t = TRANSLATIONS[language] || TRANSLATIONS.en;

    const translateUrgency = (level) => {
        if (!level) return level;
        const key = level.toLowerCase();
        return t[key] || level;
    };

    //Update clock every second
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        currentCallRef.current = currentCall;
    }, [currentCall]);

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            setIsFullscreen(true);
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
                setIsFullscreen(false);
            }
        }
    };

    useEffect(() => {
        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
    }, []);

    useEffect(() => {
        const channel = new BroadcastChannel('emergency_system_channel');

        channel.onmessage = (event) => {
            if (event.data && event.data.language) {
                setLanguage(event.data.language);
            }

            if (event.data && event.data.type === 'UPDATE_CALLS') {
                const incomingCalls = event.data.calls || [];
                setCalls(incomingCalls);
            }

            if (event.data && event.data.type === 'SELECT_CALL') {
                console.log("DNP Window selected call:", event.data.call);
                // When explicitly selected from dashboard, clear live mode and show info
                setLiveData(null);
                setCurrentCall(event.data.call);
            }

            if (event.data && event.data.type === 'LIVE_UPDATE') {
                console.log("DNP Window live update:", event.data);
                setLiveData(event.data);

                // If the call is completed, we can also update the currentCall to show details
                if (event.data.status === 'completed') {
                    // Update currentCall so the display switches to info grid
                    setCurrentCall(event.data);
                }
            }
        };

        channel.postMessage({ type: 'DNP_READY' });
        const ping = setInterval(() => channel.postMessage({ type: 'DNP_READY' }), 5000);

        return () => {
            clearInterval(ping);
            channel.close();
        };
    }, []);

    // Show Live Transcript Screen if there is live data and it's not completed
    if (liveData && (liveData.status === 'started' || liveData.status === 'processing')) {
        return <LiveTranscriptScreen liveData={liveData} currentTime={currentTime} t={t} language={language} />;
    }

    // Show NoCallScreen when no call is selected and no live data
    if (!currentCall) {
        return <NoCallScreen currentTime={currentTime} t={t} language={language} />;
    }

    // Get urgency level
    const urgencyLevel = currentCall.urgency_level || currentCall.urgency?.level || 'UNKNOWN';
    const isCritical = urgencyLevel === 'CRITICAL';
    const isHigh = urgencyLevel === 'HIGH';

    // Enhanced field parsing with Japanese/English support
    const parseSoapData = (field) => {
        if (currentCall[field]) return currentCall[field];
        const soapText = currentCall.soap_objective || currentCall.soap?.objective || '';
        if (!soapText) return null;

        // Field translation mappings for both languages
        const fieldMappings = {
            caller_name: ['Name', '氏名', '名前', '患者名', 'Patient name', 'Patient'],
            address: ['Address', '住所', '現場', '場所', 'Location', 'Incident location'],
            blood_type: ['Blood', '血液型', 'Blood type', 'Blood Type'],
            caller_phone: ['Phone', '電話', '連絡先', 'Contact', 'Mobile', 'Callback'],
            age: ['Age', '年齢', '歳', 'Patient age'],
            sex: ['Sex', 'Gender', '性別']
        };

        const keys = fieldMappings[field] || [field];

        for (const key of keys) {
            const patterns = [
                new RegExp(`${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'i'),
                new RegExp(`\\*\\s*${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'i'),
                new RegExp(`^${key}\\s*[:：]\\s*([^\\n\\r\\.、\\|]+)`, 'im'),
            ];

            for (const pattern of patterns) {
                const match = soapText.match(pattern);
                if (match && match[1]) {
                    const val = match[1].trim()
                        .replace(/^[:：\s*-]+/, '')
                        .replace(/\s*\*+\s*$/, '');

                    // Filter out placeholder values
                    if (val.length > 0 &&
                        val !== 'N/A' &&
                        !val.match(/^\\[.*\\]$/) &&  // Avoid [Name], [不明], [Not provided]
                        !val.toLowerCase().includes('not provided') &&
                        !val.includes('不明')) {
                        // For phone numbers, validate pattern
                        if (field === 'caller_phone') {
                            if (/[0-9-+()\\s]+/.test(val)) {
                                return val;
                            }
                        } else {
                            return val;
                        }
                    }
                }
            }
        }
        return null;
    };

    // Derived Data
    const derivedName = parseSoapData('caller_name') || t.unknownPatient;
    const derivedAddress = parseSoapData('address') || t.locationUnknown;
    const derivedBlood = parseSoapData('blood_type') || '--';
    const derivedAge = parseSoapData('age') || '--';
    const derivedSex = parseSoapData('sex') || '--';
    const derivedPhone = parseSoapData('caller_phone') || currentCall.caller_phone || t.unknownNumber;

    // Allergy Extraction
    const soapObjective = currentCall.soap_objective || currentCall.soap?.objective || '';
    // Try to find explicit "Allergies: ..." line or use structured data
    const derivedAllergies = (currentCall.allergies && currentCall.allergies.length > 0)
        ? currentCall.allergies
        : (soapObjective.match(/Allergies:\s*([^.\n]+)/i)?.[1]?.split(',').map(s => s.trim()) || []);

    // Medication Extraction (Fallback)
    const derivedMedications = (currentCall.medications && currentCall.medications.length > 0)
        ? currentCall.medications
        : (soapObjective.match(/Medications:\s*([^.\n]+)/i)?.[1]?.split(',').map(s => s.trim()) || []);

    // Urgency Score Logic (ensure 0-100)
    let urgencyScore = currentCall.urgency_score || currentCall.urgency?.score || 0;
    // If score is 0-10 (e.g. 9/10), scale to 100
    if (urgencyScore > 0 && urgencyScore <= 10) urgencyScore *= 10;

    // Colors
    const urgencyColor = isCritical ? 'bg-red-600' : isHigh ? 'bg-orange-600' : urgencyLevel === 'MEDIUM' ? 'bg-yellow-600' : 'bg-green-600';

    return (
        <div className="w-full h-full bg-slate-950 text-white overflow-hidden font-sans relative flex flex-col" style={{ width: '1440px', height: '540px' }}>

            {/* TOP BAR */}
            <div className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
                <div className="flex items-center space-x-4">
                    <div className={`px-4 py-1 rounded font-black text-xl tracking-wider ${urgencyColor} animate-pulse`}>
                        {translateUrgency(urgencyLevel)}
                    </div>
                    <div className="text-slate-400 font-mono text-lg">{t.caseId}: {currentCall.call_id ? (currentCall.call_id.includes('_') ? currentCall.call_id.split('_')[1] : currentCall.call_id) : '---'}</div>
                </div>
                <div className="flex items-center space-x-6">
                    <div className="flex items-center text-slate-300">
                        <Clock className="w-5 h-5 mr-2 text-slate-500" />
                        <span className="text-xl font-mono font-bold">
                            {new Date().toLocaleTimeString(language === 'ja' ? 'ja-JP' : 'en-US', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    </div>
                    <button onClick={toggleFullscreen} className="p-2 hover:bg-slate-800 rounded-full text-slate-400">
                        {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                    </button>
                </div>
            </div>

            {/* MAIN CONTENT GRID */}
            <div className="flex-1 grid grid-cols-12 gap-0">

                {/* COL 1: PATIENT IDENTITY */}
                <div className="col-span-4 border-r border-slate-800 p-6 flex flex-col justify-between bg-slate-900/50">
                    <div>
                        <div className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">{t.patientIdentity}</div>
                        <h1 className="text-3xl font-black text-sky-100 leading-tight mb-4 truncate drop-shadow-md" title={derivedName}>
                            {derivedName}
                        </h1>

                        {/* Phone Number Display */}
                        <div className="flex items-center space-x-3 mb-6 bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                            <Phone className="w-5 h-5 text-emerald-400" />
                            <span className="text-2xl font-mono font-bold text-emerald-100 tracking-wider">
                                {derivedPhone}
                            </span>
                        </div>

                        <div className="grid grid-cols-3 gap-3 mb-6">
                            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 text-center">
                                <div className="text-slate-400 text-[10px] uppercase font-bold">{t.age}</div>
                                <div className="text-xl font-bold text-cyan-400">{derivedAge}</div>
                            </div>
                            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 text-center">
                                <div className="text-slate-400 text-[10px] uppercase font-bold">{t.sex}</div>
                                <div className={`text-xl font-bold ${derivedSex.toLowerCase().includes('female') ? 'text-pink-400' : 'text-blue-400'}`}>
                                    {derivedSex}
                                </div>
                            </div>
                            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700 text-center">
                                <div className="text-slate-400 text-[10px] uppercase font-bold">{t.blood}</div>
                                <div className="text-xl font-bold text-red-500">{derivedBlood}</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700">
                        <div className="flex items-start space-x-3">
                            <MapPin className="w-6 h-6 text-indigo-400 shrink-0 mt-1" />
                            <div>
                                <div className="text-xs uppercase text-slate-400 font-bold">{t.location}</div>
                                {/* REMOVED SEPARATE CITY FIELD - ONLY FULL ADDRESS NOW */}
                                <div className="text-lg font-bold text-indigo-100 leading-snug">{derivedAddress}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* COL 2: CLINICAL / ALERTS */}
                <div className="col-span-4 border-r border-slate-800 p-6 flex flex-col bg-slate-900/30">
                    <div className="mb-6">
                        <div className="flex items-center space-x-2 mb-3">
                            <AlertTriangle className="w-5 h-5 text-orange-400" />
                            <span className="text-xs uppercase tracking-widest text-orange-400 font-bold">{t.medicalAlerts}</span>
                        </div>
                        <div className="bg-orange-900/10 border border-orange-500/20 p-4 rounded-xl h-32 overflow-y-auto">
                            {derivedAllergies.length > 0 ? (
                                <div className="flex flex-wrap gap-2">
                                    {derivedAllergies.map((a, i) => (
                                        <span key={i} className="bg-orange-900/40 text-orange-200 px-2 py-1 rounded text-sm font-bold border border-orange-500/30">
                                            {a}
                                        </span>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-lg text-slate-300 leading-snug font-medium italic">
                                    {t.noAllergies}
                                </p>
                            )}
                        </div>
                    </div>

                    <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-3">
                            <Pill className="w-5 h-5 text-blue-400" />
                            <span className="text-xs uppercase tracking-widest text-blue-400 font-bold">{t.medications}</span>
                        </div>
                        <div className="bg-blue-900/10 border border-blue-500/20 p-4 rounded-xl h-full max-h-[140px] overflow-y-auto">
                            {derivedMedications.length > 0 ? (
                                <ul className="space-y-2">
                                    {derivedMedications.map((m, i) => (
                                        <li key={i} className="flex items-center text-blue-100 font-medium">
                                            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-2"></span>
                                            {m}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="text-slate-500 italic">{t.noMedications}</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* COL 3: LIVE SITUATION */}
                <div className="col-span-4 p-0 flex flex-col bg-slate-900 relative">
                    <div className={`absolute top-0 right-0 w-2 h-full ${urgencyColor} opacity-50`}></div>

                    <div className="p-6 flex-1 flex flex-col">
                        <div className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-3">{t.situationSummary}</div>
                        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            <p className="text-xl leading-relaxed text-slate-200 font-medium">
                                {/* Combined Subjective + Objective Summary */}
                                {(() => {
                                    const subjective = currentCall.soap_subjective || currentCall.call_summary || '';
                                    const objective = currentCall.soap_objective || '';

                                    // Combine S+O if both exist (joined as one paragraph)
                                    if (subjective && objective) {
                                        return `${subjective} ${objective}`;
                                    }

                                    // Fallback to what's available
                                    return subjective || objective || currentCall.urgency?.reasoning || 'Analyzing situation...';
                                })()}
                            </p>
                        </div>
                    </div>

                    {/* Footer Stats */}
                    <div className="h-20 border-t border-slate-800 bg-slate-950 flex">
                        <div className="flex-1 flex flex-col justify-center items-center border-r border-slate-800">
                            <div className="text-4xl font-black text-white">{parseInt(urgencyScore)}<span className="text-lg text-slate-500">%</span></div>
                            <div className="text-[10px] uppercase text-slate-500 font-bold">{t.urgencyScore}</div>
                        </div>
                        <div className="flex-1 flex flex-col justify-center items-center">
                            <div className="text-emerald-400 font-black text-xl">{t.live}</div>
                            <div className="text-[10px] uppercase text-emerald-600 font-bold">{t.connection}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const LiveTranscriptScreen = ({ liveData, currentTime, t, language }) => (
    <div className="w-full h-full bg-slate-950 text-white overflow-hidden font-sans relative flex flex-col" style={{ width: '1440px', height: '540px' }}>
        {/* Header */}
        <div className="h-16 bg-red-900/40 border-b border-red-500/30 flex items-center justify-between px-8">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-red-400 font-black tracking-widest text-xl uppercase">{t.liveEmergencyCall}</span>
                </div>
                <div className="h-6 w-px bg-slate-700 mx-2"></div>
                <div className="text-slate-400 font-mono text-lg uppercase tracking-tight">ID: {liveData.call_id || '---'}</div>
            </div>
            <div className="flex items-center space-x-6">
                <div className="flex bg-slate-800/80 px-4 py-1.5 rounded-lg border border-slate-700">
                    <span className="text-blue-400 font-bold mr-2">{t.status}:</span>
                    <span className="text-white font-bold animate-pulse uppercase">{liveData.status}</span>
                </div>
                <div className="flex items-center text-slate-300">
                    <Clock className="w-6 h-6 mr-2 text-slate-500" />
                    <span className="text-2xl font-mono font-bold">
                        {currentTime.toLocaleTimeString(language === 'ja' ? 'ja-JP' : 'en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                </div>
            </div>
        </div>

        {/* Main Transcript Body */}
        <div className="flex-1 p-8 flex flex-col justify-center items-center bg-gradient-to-b from-slate-950 to-slate-900">
            <div className="w-full max-w-6xl">
                <div className="flex items-center space-x-3 mb-6">
                    <Activity className="text-blue-500 w-8 h-8 animate-pulse" />
                    <h2 className="text-2xl font-bold text-slate-400 uppercase tracking-widest italic">{t.interpretingAudio}</h2>
                </div>
                <div className="bg-slate-900/50 border-2 border-slate-800 rounded-3xl p-10 shadow-2xl min-h-[300px] flex items-center">
                    <p className="text-5xl font-bold leading-tight text-white tracking-tight text-center w-full drop-shadow-lg">
                        {liveData.transcript ? (
                            liveData.transcript
                        ) : (
                            <span className="text-slate-600 italic animate-pulse">{t.waitingSpeech}</span>
                        )}
                    </p>
                </div>
            </div>
        </div>

        {/* Footer Guidance */}
        <div className="h-12 bg-slate-900/80 border-t border-slate-800 px-8 flex items-center justify-center">
            <div className="flex items-center space-x-8 text-slate-500 text-sm font-bold uppercase tracking-widest">
                <div className="flex items-center"><div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div> {t.aiTranscription}</div>
                <div className="flex items-center"><div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div> {t.realtimeSoap}</div>
                <div className="flex items-center"><div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div> {t.autoSaving}</div>
            </div>
        </div>
    </div>
);

const NoCallScreen = ({ currentTime, t, language }) => (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900" style={{ width: '1440px', height: '540px' }}>
        <div className="text-center">
            {/* Large Clock */}
            <div className="mb-8">
                <div className="flex items-center justify-center space-x-2 mb-4">
                    <Clock className="h-16 w-16 text-blue-500 animate-pulse" strokeWidth={2} />
                </div>
                <h1 className="text-9xl font-black text-white mb-2 font-mono tracking-tight">
                    {currentTime.toLocaleTimeString(language === 'ja' ? 'ja-JP' : 'en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false
                    })}
                </h1>
                <p className="text-3xl text-gray-500 font-semibold">
                    {currentTime.toLocaleDateString(language === 'ja' ? 'ja-JP' : 'en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    })}
                </p>
            </div>

            {/* Status */}
            <div className="mt-12">
                <Activity className="h-20 w-20 text-gray-700 mx-auto mb-4 animate-pulse" strokeWidth={2} />
                <h2 className="text-4xl font-bold text-gray-600 mb-3 tracking-tight">{t.ready}</h2>
                <p className="text-xl text-gray-700">{t.waitingCall}</p>
            </div>
        </div>
    </div>
);

export default TransparentMonitor;
