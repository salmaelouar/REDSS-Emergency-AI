import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Upload, Phone, FileText, RefreshCw, Download, AlertTriangle, X,
  Activity, Clock, TrendingUp, TrendingDown, Radio, Zap, Brain, Search, MessageSquare, Loader, Trash2,
  User, Languages
} from 'lucide-react';

import './App.css';
import LanguageMarkersDashboard from './LanguageMarkersDashboard';
import BleuScoreQualityMetrics from './BleuScoreQualityMetrics';
import RealtimeCall from './RealtimeCall';
import PatientJourneyView from './PatientJourneyView';

const COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#22c55e'
};

const TRANSLATIONS = {
  en: {
    title: "Real-Time Emergency System",
    subtitle: "AI-Powered Analysis & Dispatch",
    liveCall: "Live Call",
    textInput: "Text Input",
    qualityCenter: "Quality Center",
    analytics: "Analytics",
    operations: "Operations",
    dnpMonitor: "DNP Monitor",
    totalCalls: "Total Calls",
    critical: "Critical",
    high: "High",
    medium: "Medium",
    low: "Low",
    avgDuration: "Avg Duration",
    activeUnits: "Active Units",
    emergencyCalls: "Emergency Calls",
    searchPlaceholder: "Search calls, transcripts or IDs...",
    waitingForCalls: "Waiting for calls...",
    patientIdentity: "Patient Identity",
    age: "Age",
    blood: "Blood",
    sex: "Sex",
    phone: "Phone",
    address: "Address",
    triageMarkers: "Triage & Language Markers",
    viewMarkers: "View Language Markers",
    soapAnalysis: "SOAP Clinical Analysis",
    systemPerformance: "System Performance (BLEU)",
    viewQuality: "System Performance (BLEU)",
    clinicalTranscription: "Clinical Transcription",
    exportReport: "Export Report",
    downloadPDF: "Download Clinical Report (PDF)",
    hospital: "Assigned Hospital",
    score: "Score",
    all: "ALL",
    upload: "Upload",
    exportAll: "Export All",
    monitor: "Monitor",
    autoRefresh: "Auto Refresh",
    clearData: "Clear Data",
    viewDetails: "View Details",
    callDetails: "Call Details",
    exportCasePDF: "Export Case PDF",
    name: "Name",
    attendingMD: "Attending MD",
    unassigned: "Unassigned",
    general: "General",
    triageLanguageMarkers: "Triage & Language Markers",
    urgencyConfidence: "Urgency Confidence",
    noReasoningProvided: "No reasoning provided",
    cognitiveCheck: "Cognitive Check",
    viewLanguageMarkers: "View Language Markers",
    stable: "STABLE",
    noDementia: "No Dementia",
    soapClinicalAnalysis: "SOAP Clinical Analysis",
    subjective: "Subjective",
    objective: "Objective",
    assessment: "Assessment",
    plan: "Plan",
    systemPerformanceBLEU: "System Performance (BLEU)",
    extractionQuality: "Extraction Quality",
    systemValidated: "System Validated",
    bleuOK: "BLEU OK",
    noTranscriptionAvailable: "No transcription available.",
    english: "English",
    japanese: "Japanese",
    selectCallToViewDetails: "Select a call to view details",
    manualMedicalInput: "Manual Medical Input",
    callProcessedSuccessfully: "Call processed successfully",
    failedToProcessAudio: "Failed to process audio file",
    textProcessedSuccessfully: "Text processed successfully",
    failedToProcessText: "Failed to process text",
    errorProcessingText: "Error processing text",
    confirmClearData: "ARE YOU SURE? This will permanently delete ALL calls from the database. This action cannot be undone.",
    databaseClearedSuccessfully: "Database cleared successfully",
    failedToClearDatabase: "Failed to clear database",
    errorConnectingToServer: "Error connecting to server",
    enterPatientName: "Enter patient name...",
    enterDoctorName: "Enter doctor name...",
    selectCondition: "Select a condition...",
    typeObservations: "Type the doctor's observations or patient's statement here...",
    medicalCondition: "Medical Condition / Disease",
    clinicalTranscript: "Clinical Transcript / Observation",
    processData: "Process & Analyze Data",
    cancel: "Cancel",
    processing: "Processing...",
    timestamp: "Call Timestamp",
    conditionStroke: "Stroke",
    conditionHeartAttack: "Heart Attack",
    conditionCOVID: "COVID-19",
    conditionTrauma: "Severe Fall / Trauma",
    conditionRespiratory: "Respiratory Distress",
    conditionCardiac: "Cardiac Arrest",
    conditionHypo: "Hypoglycemia",
    conditionAnaphylaxis: "Anaphylaxis",
    conditionUnknown: "Other / Undefined",
    dualMode: "Dual Mode",
    patientJourney: "Patient Journey"
  },
  ja: {
    title: "救急意思決定支援システム",
    subtitle: "AI解析・迅速指令センター",
    liveCall: "ライブ通話",
    textInput: "手動入力",
    qualityCenter: "品質分析",
    analytics: "統計解析",
    operations: "運用状況",
    dnpMonitor: "DNPモニター",
    totalCalls: "総通報数",
    critical: "最優先(重症)",
    high: "高緊急度",
    medium: "中緊急度",
    low: "低緊急度",
    avgDuration: "平均通話時間",
    activeUnits: "活動部隊",
    emergencyCalls: "緊急通報リスト",
    searchPlaceholder: "通報内容やIDで検索...",
    waitingForCalls: "通報を待機中...",
    patientIdentity: "患者基本情報",
    age: "年齢",
    blood: "血液型",
    sex: "性別",
    phone: "連絡先",
    address: "現場住所",
    triageMarkers: "トリアージ・言語指標",
    viewMarkers: "抽出精度データ表示",
    soapAnalysis: "SOAP臨床解析",
    systemPerformance: "抽出品質 (BLEU)",
    viewQuality: "抽出基準データ表示",
    clinicalTranscription: "臨床文字起こし",
    exportReport: "報告書出力",
    downloadPDF: "保存 (PDF)",
    hospital: "搬送先病院",
    score: "スコア",
    all: "全件",
    upload: "アップロード",
    exportAll: "一括出力",
    monitor: "モニター表示",
    autoRefresh: "自動更新",
    clearData: "データ消去",
    viewDetails: "詳細を表示",
    callDetails: "通報詳細内容",
    exportCasePDF: "PDFレポート作成",
    name: "氏名",
    attendingMD: "担当医師",
    unassigned: "未割当",
    general: "一般疾患",
    triageLanguageMarkers: "トリアージと言語指標",
    urgencyConfidence: "緊急度確信度",
    noReasoningProvided: "根拠データなし",
    cognitiveCheck: "認知能力チェック",
    viewLanguageMarkers: "言語マーカー分析表示",
    stable: "安定",
    noDementia: "認知症疑いなし",
    soapClinicalAnalysis: "SOAP臨床解析レポート",
    subjective: "主観的所見 (S)",
    objective: "客観的所見 (O)",
    assessment: "評価 (A)",
    plan: "対応計画 (P)",
    systemPerformanceBLEU: "システム性能 (BLEU)",
    extractionQuality: "抽出品質レベル",
    systemValidated: "システム検証済み",
    bleuOK: "精度良好",
    noTranscriptionAvailable: "文字起こしデータなし",
    english: "英語",
    japanese: "日本語",
    selectCallToViewDetails: "詳細を表示する通報を選択してください",
    manualMedicalInput: "医療情報の直接入力",
    callProcessedSuccessfully: "通報の処理が完了しました",
    failedToProcessAudio: "オーディオファイルの処理に失敗しました",
    textProcessedSuccessfully: "テキストの処理が完了しました",
    failedToProcessText: "テキストの処理に失敗しました",
    errorProcessingText: "テキスト処理中にエラーが発生しました",
    confirmClearData: "本当によろしいですか？データベース内のすべての通報が完全に削除されます。この操作は取り消せません。",
    databaseClearedSuccessfully: "データベースを消去しました",
    failedToClearDatabase: "データベースの消去に失敗しました",
    errorConnectingToServer: "サーバーへの接続エラーが発生しました",
    enterPatientName: "患者の氏名を入力...",
    enterDoctorName: "医師の氏名を入力...",
    selectCondition: "疾患・状態を選択...",
    typeObservations: "医師の所見または患者の訴えをここに入力してください...",
    medicalCondition: "疾患・現在の状態",
    clinicalTranscript: "臨床文字起こし / 観察事項",
    processData: "データを解析する",
    cancel: "キャンセル",
    processing: "解析中...",
    timestamp: "通報日時",
    conditionStroke: "脳卒中",
    conditionHeartAttack: "心筋梗塞",
    conditionCOVID: "新型コロナウイルス",
    conditionTrauma: "転倒・外傷",
    conditionRespiratory: "呼吸困難",
    conditionCardiac: "心停止",
    conditionHypo: "低血糖",
    conditionAnaphylaxis: "アナフィラキシー",
    conditionUnknown: "その他・不明",
    dualMode: "Dual Mode",
    patientJourney: "患者経過"
  }
};

// Main App component
function EmergencyManager() {
  // Existing states
  const [calls, setCalls] = useState([]);
  const [filteredCalls, setFilteredCalls] = useState([]);
  const [selectedCall, setSelectedCall] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState(null);
  const [urgencyFilter, setUrgencyFilter] = useState('ALL');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [notification, setNotification] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // VIEW STATES
  const [showQualityDashboard, setShowQualityDashboard] = useState(false);
  const [qualityCallId, setQualityCallId] = useState(null);
  const [showRealtimeCall, setShowRealtimeCall] = useState(false);
  const [showMarkersFullscreen, setShowMarkersFullscreen] = useState(false);
  const [showPatientJourney, setShowPatientJourney] = useState(false);
  const [patientJourneyStatus, setPatientJourneyStatus] = useState(null);

  useEffect(() => {
    const name = selectedCall?.patient_name;
    const isPlaceholder = !name || name.includes('[Not provided]') || name.includes('[不明]') || name.includes('N/A');

    if (name && !isPlaceholder) {
      fetch(`http://localhost:8000/api/patients/check?name=${encodeURIComponent(name)}`)
        .then(res => res.json())
        .then(data => setPatientJourneyStatus(data))
        .catch(err => setPatientJourneyStatus(null));
    } else {
      setPatientJourneyStatus(null);
    }
  }, [selectedCall]);

  // Text Input State
  const [showTextInput, setShowTextInput] = useState(false);
  const [textInputVal, setTextInputVal] = useState('');
  const [patientInput, setPatientInput] = useState('');
  const [doctorInput, setDoctorInput] = useState('');
  const [diseaseInput, setDiseaseInput] = useState('');
  const [systemLanguage, setSystemLanguage] = useState('en');
  const [isProcessingText, setIsProcessingText] = useState(false);
  const [showMobileDetails, setShowMobileDetails] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [dualLanguage, setDualLanguage] = useState(false);
  const [activeCallPatient, setActiveCallPatient] = useState(null);

  const API_URL = 'http://localhost:8000';

  // --- SKELETON COMPONENT ---
  const Skeleton = ({ className }) => (
    <div className={`animate-shimmer ${className}`}></div>
  );

  // --- BROADCAST CHANNEL LOGIC ---
  const channelRef = useRef(null);
  const callsRef = useRef(calls);

  const parseField = (text, fieldName) => {
    if (!text) return 'N/A';

    // Map English field names to potential Japanese equivalents found in transcripts
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
    return systemLanguage === 'ja' ? '[不明]' : 'N/A';
  };

  const translateCondition = (condition) => {
    if (!condition) return 'N/A';
    const mapping = {
      'Stroke': 'conditionStroke',
      'Heart Attack': 'conditionHeartAttack',
      'COVID-19': 'conditionCOVID',
      'Severe Fall / Trauma': 'conditionTrauma',
      'Respiratory Distress': 'conditionRespiratory',
      'Cardiac Arrest': 'conditionCardiac',
      'Hypoglycemia': 'conditionHypo',
      'Anaphylaxis': 'conditionAnaphylaxis'
    };
    const key = mapping[condition] || 'conditionUnknown';
    return TRANSLATIONS[systemLanguage][key] || condition;
  };

  useEffect(() => {
    callsRef.current = calls;
  }, [calls]);

  useEffect(() => {
    channelRef.current = new BroadcastChannel('emergency_system_channel');
    channelRef.current.onmessage = (event) => {
      if (event.data && event.data.type === 'DNP_READY') {
        if (callsRef.current.length > 0) {
          channelRef.current.postMessage({ type: 'UPDATE_CALLS', calls: callsRef.current, language: systemLanguage });
        }
      }
    };
    return () => {
      if (channelRef.current) {
        channelRef.current.close();
      }
    };
  }, [systemLanguage]);

  useEffect(() => {
    if (calls.length > 0 && channelRef.current) {
      channelRef.current.postMessage({ type: 'UPDATE_CALLS', calls, language: systemLanguage });
    }
  }, [calls, systemLanguage]);

  const fetchCalls = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/calls?limit=100&lang=${systemLanguage}`);
      const data = await response.json();
      setCalls(data.calls || []);
    } catch (error) {
      console.error('Error fetching calls:', error);
    }
  }, [API_URL, systemLanguage]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, [API_URL]);

  useEffect(() => {
    fetchCalls();
    fetchStats();
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchCalls();
        fetchStats();
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, fetchCalls, fetchStats]);

  useEffect(() => {
    fetchCalls(); // Fetch translated calls immediately fetch means get the data from the server or write it in the database
    if (selectedCall && selectedCall.call_id) {
      handleCallSelect(selectedCall);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [systemLanguage]);

  useEffect(() => {
    let filtered = calls;
    if (urgencyFilter !== 'ALL') {
      filtered = filtered.filter(call => call.urgency_level === urgencyFilter);
    }
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(call =>
        (call.soap_subjective && call.soap_subjective.toLowerCase().includes(query)) ||
        (call.transcript && call.transcript.toLowerCase().includes(query)) ||
        (call.call_id && call.call_id.toLowerCase().includes(query))
      );
    }
    setFilteredCalls(filtered);
  }, [calls, urgencyFilter, searchQuery]);

  const exportToPDF = (specificCall = null, targetLanguage = systemLanguage) => {
    // We are switching from jsPDF to a high-quality browser Print system.
    // This fixes the Japanese mojibake (mangled text) issues and provides 
    // a professional clinical layout that supports all medical data.

    let url = `/report?lang=${targetLanguage}`;
    if (specificCall) {
      url += `&id=${specificCall.call_id}`;
    }

    // Open in a new window to trigger the print view
    window.open(url, '_blank');
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleAudioUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await fetch(`${API_URL}/api/upload?language=${systemLanguage}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      // Auto-switch UI language if different from detected
      if (data.language && data.language !== systemLanguage) {
        setSystemLanguage(data.language);
      }

      if (!response.ok) throw new Error('Upload failed');

      fetchCalls(); // Refresh list to show new call
      showNotification(TRANSLATIONS[systemLanguage].callProcessedSuccessfully, 'success');
    } catch (err) {
      console.error(err);
      showNotification(TRANSLATIONS[systemLanguage].failedToProcessAudio, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textInputVal.trim()) return;
    setIsProcessingText(true);
    try {
      const response = await fetch(`${API_URL}/api/process-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textInputVal,
          patient_name: patientInput,
          doctor_name: doctorInput,
          disease: diseaseInput,
          language: systemLanguage
        })
      });
      console.log("Text process response status:", response.status);
      const resData = await response.json();
      console.log("Text process result:", resData);

      if (response.ok) {
        showNotification(TRANSLATIONS[systemLanguage].textProcessedSuccessfully, 'success');
        setShowTextInput(false);
        setTextInputVal('');
        setPatientInput('');
        setDoctorInput('');
        setDiseaseInput('');
        fetchCalls(); // Refresh
      } else {
        showNotification(TRANSLATIONS[systemLanguage].failedToProcessText, 'error');
        alert(`API Error: ${TRANSLATIONS[systemLanguage].failedToProcessText}`);
      }
    } catch (e) {
      console.error("Text process catch error:", e);
      showNotification(TRANSLATIONS[systemLanguage].errorProcessingText, 'error');
      alert(`System Error: ${e.message}`);
    } finally {
      setIsProcessingText(false);
    }
  };

  const handleClearData = async () => {
    if (!window.confirm(TRANSLATIONS[systemLanguage].confirmClearData)) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/calls/clear`, {
        method: 'DELETE'
      });
      if (response.ok) {
        showNotification(TRANSLATIONS[systemLanguage].databaseClearedSuccessfully, 'success');
        setSelectedCall(null);
        fetchCalls();
        fetchStats();
      } else {
        showNotification(TRANSLATIONS[systemLanguage].failedToClearDatabase, 'error');
      }
    } catch (err) {
      console.error(err);
      showNotification(TRANSLATIONS[systemLanguage].errorConnectingToServer, 'error');
    }
  };

  const clearSelection = () => {
    setSelectedCall(null);
    setShowQualityDashboard(false);
    setShowRealtimeCall(false);
    setActiveCallPatient(null);
  };

  const openTransparentMonitor = () => {
    const dnpWindow = window.open('/dnp', 'DNP_Display', 'width=1440,height=540,menubar=no,toolbar=no,location=no,status=no');
    if (dnpWindow) {
      dnpWindow.focus();
    }
  };

  const handleCallSelect = async (call) => {
    // If selecting same call just for language change, mark as translating
    setIsTranslating(true);

    // Immediate UI update with available data (to keep it interactive)
    setSelectedCall(call);
    setShowMobileDetails(true);

    try {
      const response = await fetch(`${API_URL}/api/calls/${call.call_id}?lang=${systemLanguage}`);
      if (response.ok) {
        const data = await response.json();
        // Normalize nested API response to flat structure
        const fullData = {
          ...data,
          urgency_level: data.urgency?.level || data.urgency_level,
          urgency_score: data.urgency?.score || data.urgency_score,
          urgency_reasoning: data.urgency?.reasoning || data.urgency_reasoning,
          soap_subjective: data.soap?.subjective || data.soap_subjective,
          soap_objective: data.soap?.objective || data.soap_objective,
          soap_assessment: data.soap?.assessment || data.soap_assessment,
          soap_plan: data.soap?.plan || data.soap_plan,
        };

        // Update with full details
        setSelectedCall(fullData);
        if (channelRef.current) {
          channelRef.current.postMessage({ type: 'SELECT_CALL', call: fullData, language: systemLanguage });
        }
      }
    } catch (err) {
      console.error("Error fetching full call details", err);
    } finally {
      setIsTranslating(false);
    }
  };



  if (showPatientJourney) {
    return (
      <PatientJourneyView
        systemLanguage={systemLanguage}
        onBack={() => setShowPatientJourney(false)}
        onStartLiveCall={(patient) => {
          setShowPatientJourney(false);
          setActiveCallPatient(patient);
          setShowRealtimeCall(true);
        }}
      />
    );
  }



  return (
    <div className="min-h-screen lg:h-screen flex flex-col bg-black text-white relative lg:overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="relative z-10 p-6 flex flex-col lg:h-full lg:overflow-hidden">
        {/* Header */}
        <div className="flex flex-col xl:flex-row xl:items-center justify-between mb-8 gap-6 shrink-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-75"></div>
              <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-xl">
                <Activity className="h-8 w-8 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
                {TRANSLATIONS[systemLanguage].title}
              </h1>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-sm text-zinc-400">{TRANSLATIONS[systemLanguage].subtitle}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-10 gap-4 w-full xl:w-auto">
            <button
              onClick={() => {
                setShowRealtimeCall(true);
                setShowMobileDetails(true);
              }}
              className="h-10 w-full px-2 md:px-4 rounded-lg bg-red-600 hover:bg-red-500 font-semibold text-xs md:text-sm transition-all flex items-center justify-center space-x-1 md:space-x-2 whitespace-nowrap"
            >
              <Radio size={16} />
              <span>{TRANSLATIONS[systemLanguage].liveCall}</span>
            </button>

            <button
              onClick={() => setSystemLanguage(l => l === 'en' ? 'ja' : 'en')}
              className={`flex items-center space-x-2 px-3 py-1.5 h-10 rounded-lg border transition-all ${systemLanguage === 'ja'
                ? 'bg-red-500/10 border-red-500/50 text-red-400'
                : 'bg-blue-500/10 border-blue-500/50 text-blue-400'
                }`}
            >
              <Languages size={16} />
              <span className="text-xs font-bold uppercase tracking-tight hidden sm:inline">
                {systemLanguage === 'en' ? 'English' : '日本語'}
              </span>
            </button>

            <button
              onClick={() => setDualLanguage(!dualLanguage)}
              className={`flex items-center space-x-2 px-3 py-1.5 h-10 rounded-lg border transition-all ${dualLanguage
                ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                : 'bg-zinc-800/50 border-zinc-700 text-zinc-400'
                }`}
            >
              <div className={`w-2 h-2 rounded-full ${dualLanguage ? 'bg-purple-400 animate-pulse' : 'bg-zinc-600'}`}></div>
              <span className="text-xs font-bold uppercase tracking-tight hidden sm:inline">
                {TRANSLATIONS[systemLanguage].dualMode}
              </span>
            </button>

            <button
              onClick={() => setShowTextInput(true)}
              className="h-10 w-full px-2 md:px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs md:text-sm transition-all flex items-center justify-center space-x-1 md:space-x-2 whitespace-nowrap"
            >
              <MessageSquare className="h-5 w-5 lg:h-6 lg:w-6" />
              <span>{TRANSLATIONS[systemLanguage].textInput}</span>
            </button>

            <label className="h-10 w-full px-2 md:px-4 rounded-lg bg-blue-600 hover:bg-blue-500 font-semibold text-xs md:text-sm transition-all cursor-pointer flex items-center justify-center space-x-1 md:space-x-2 whitespace-nowrap">
              <Upload size={16} />
              <span>{TRANSLATIONS[systemLanguage].upload}</span>
              <input type="file" className="hidden" accept=".wav,.mp3,.m4a" onChange={handleAudioUpload} disabled={uploading} />
            </label>

            <div className="flex space-x-1 h-10 w-full xl:w-auto xl:col-span-2">
              <button
                onClick={() => exportToPDF(null, 'en')}
                className="flex-1 px-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 font-semibold text-[10px] md:text-xs transition-all flex items-center justify-center space-x-1 whitespace-nowrap"
              >
                <Download size={14} />
                <span>PDF EN</span>
              </button>
              <button
                onClick={() => exportToPDF(null, 'ja')}
                className="flex-1 px-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 font-semibold text-[10px] md:text-xs transition-all flex items-center justify-center space-x-1 whitespace-nowrap"
              >
                <Download size={14} />
                <span>PDF JA</span>
              </button>
            </div>

            <button
              onClick={() => setShowPatientJourney(true)}
              className="col-span-1 xl:col-span-2 h-10 w-full px-4 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 font-semibold text-xs md:text-sm transition-all flex items-center justify-center space-x-2 whitespace-nowrap"
            >
              <User size={16} />
              <span>{TRANSLATIONS[systemLanguage].patientJourney}</span>
            </button>

            <button
              onClick={openTransparentMonitor}
              className="h-10 w-full px-2 md:px-4 rounded-lg bg-purple-600 hover:bg-purple-500 font-semibold text-xs md:text-sm transition-all flex items-center justify-center space-x-1 md:space-x-2 whitespace-nowrap"
            >
              <Phone size={16} />
              <span>{TRANSLATIONS[systemLanguage].monitor}</span>
            </button>



          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-2 lg:gap-6 mb-4 lg:mb-8 shrink-0">
          <MetricCard
            title={TRANSLATIONS[systemLanguage].totalCalls}
            value={stats?.total_calls || 0}
            icon={<Phone className="h-7 w-7" />}
            trend="+12%"
            trendUp={true}
            color="blue"
          />
          <MetricCard
            title={TRANSLATIONS[systemLanguage].critical}
            value={stats?.urgency_distribution?.CRITICAL || 0}
            icon={<AlertTriangle className="h-7 w-7" />}
            trend="+5%"
            trendUp={true}
            color="red"
          />
          <MetricCard
            title={TRANSLATIONS[systemLanguage].avgDuration}
            value={`${Math.round(stats?.average_duration || 0)}s`}
            icon={<Clock className="h-7 w-7" />}
            trend="-8%"
            trendUp={false}
            color="green"
          />
          <MetricCard
            title={TRANSLATIONS[systemLanguage].activeUnits}
            value={calls.length}
            icon={<Radio className="h-7 w-7" />}
            trend="Live"
            color="purple"
          />
        </div>



        {/* Main Dashboard Grid - Responsive 2-panel layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 xl:grid-cols-5 gap-6 mb-0 lg:flex-1 lg:min-h-0">
          {/* Left Column - Vertical Call List (Responsive sizing) */}
          <div className="lg:col-span-7 xl:col-span-3 bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl flex flex-col overflow-hidden h-full">
            <div className="bg-zinc-900 border-b border-zinc-800 z-20 p-3 shadow-xl shrink-0">
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center space-x-2 lg:space-x-3 shrink-0">
                  <div className="bg-blue-500/20 p-2 rounded-lg">
                    <Activity className="h-5 w-5 lg:h-6 lg:w-6 text-blue-400" />
                  </div>
                  <h2 className="text-lg font-bold whitespace-nowrap">{TRANSLATIONS[systemLanguage].emergencyCalls}</h2>
                  <span className="text-xs text-zinc-500 bg-zinc-800 px-3 py-1.5 rounded-full border border-zinc-700 ml-2">
                    {filteredCalls.length}
                  </span>
                  <button
                    onClick={() => setAutoRefresh(!autoRefresh)}
                    className={`ml-3 p-2 rounded-lg transition-all flex items-center space-x-2 ${autoRefresh ? 'bg-green-600/20 text-green-400 border border-green-500/30' : 'bg-zinc-800 text-zinc-500 border border-zinc-700'
                      }`}
                    title={TRANSLATIONS[systemLanguage].autoRefresh}
                  >
                    <RefreshCw size={14} className={autoRefresh ? 'animate-spin-slow' : ''} />
                    <span className="text-[10px] font-bold uppercase hidden sm:inline">{TRANSLATIONS[systemLanguage].autoRefresh}</span>
                  </button>

                  <button
                    onClick={handleClearData}
                    className="ml-2 p-2 rounded-lg bg-zinc-800 border border-red-900/30 hover:bg-red-950/30 text-red-500/70 hover:text-red-500 transition-all flex items-center space-x-2"
                    title={TRANSLATIONS[systemLanguage].clearData}
                  >
                    <Trash2 size={14} />
                    <span className="text-[10px] font-bold uppercase hidden sm:inline">{TRANSLATIONS[systemLanguage].clearData}</span>
                  </button>
                </div>

                {/* Urgency Filters - Adjusted to be on same level/row when space allows */}
                <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-hide">
                  {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
                    <button
                      key={level}
                      onClick={() => setUrgencyFilter(level)}
                      className={`px-2 py-1 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${urgencyFilter === level
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 border border-zinc-700'
                        }`}
                    >
                      {TRANSLATIONS[systemLanguage][level.toLowerCase()] || level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-500 h-3.5 w-3.5" />
                <input
                  type="text"
                  placeholder={TRANSLATIONS[systemLanguage].searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500 transition-colors placeholder-zinc-500"
                />
              </div>
            </div>

            {/* Vertical Call List */}
            <div className="space-y-3 p-3 lg:p-6 pt-2 lg:pt-4 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 hover:scrollbar-thumb-zinc-600">
              {filteredCalls.length > 0 ? filteredCalls.map((call, index) => {
                const urgency = call.urgency_level || call.urgency?.level || 'UNKNOWN';
                const isSelected = selectedCall?.call_id === call.call_id;

                return (
                  <div
                    key={call.call_id || index}
                    onClick={() => handleCallSelect(call)}
                    className={`group p-4 rounded-xl cursor-pointer transition-all border-l-4 relative overflow-hidden ${isSelected
                      ? `bg-gradient-to-r ${urgency === 'CRITICAL' ? 'from-red-900/40 to-zinc-900/50 border-red-500 shadow-red-900/20' :
                        urgency === 'HIGH' ? 'from-orange-900/40 to-zinc-900/50 border-orange-500 shadow-orange-900/20' :
                          urgency === 'MEDIUM' ? 'from-yellow-900/40 to-zinc-900/50 border-yellow-500 shadow-yellow-900/20' :
                            urgency === 'LOW' ? 'from-green-900/40 to-zinc-900/50 border-green-500 shadow-green-900/20' :
                              'from-blue-900/40 to-zinc-900/50 border-blue-500'
                      } shadow-lg`
                      : 'bg-zinc-800/50 hover:bg-zinc-800 border-zinc-700 hover:border-zinc-600'
                      }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full animate-pulse`}
                          style={{ backgroundColor: COLORS[urgency] || COLORS.LOW }}>
                        </div>
                        <span className="px-2 py-1 rounded-md text-xs font-bold text-white"
                          style={{ backgroundColor: COLORS[urgency] || COLORS.LOW }}>
                          {TRANSLATIONS[systemLanguage][urgency.toLowerCase()] || urgency}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {/* Quick Actions */}
                        <div className="flex space-x-1 mr-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCallSelect(call); // Ensure selected
                              setQualityCallId(call.call_id);
                              setShowQualityDashboard(true);
                            }}
                            className="p-1.5 bg-zinc-700 hover:bg-zinc-600 rounded-md text-yellow-500 transition-colors"
                            title="BLEU Score"
                          >
                            <Zap size={14} />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCallSelect(call); // Ensure selected
                              setShowMarkersFullscreen(true);
                            }}
                            className="p-1.5 bg-zinc-700 hover:bg-zinc-600 rounded-md text-purple-400 transition-colors"
                            title="Language Markers"
                          >
                            <Brain size={14} />
                          </button>
                        </div>
                        <span className="text-zinc-500 text-xs font-mono">
                          {call.created_at ? new Date(call.created_at).toLocaleString([], { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                        </span>
                      </div>
                    </div>

                    <div className="text-blue-400 font-mono text-[10px] lg:text-xs mb-1 font-semibold">
                      {call.call_id || 'N/A'}
                    </div>

                    <div className="mb-3 space-y-1.5">
                      <p className="text-zinc-300 text-xs lg:text-sm line-clamp-2 leading-relaxed">
                        {call.soap_subjective || call.transcript || TRANSLATIONS[systemLanguage].processing}
                      </p>
                      {dualLanguage && call.original && (
                        <div className="bg-black/20 p-2 rounded border-l border-zinc-700/50 mt-1">
                          <p className="text-zinc-500 text-[11px] line-clamp-2 leading-relaxed italic">
                            {call.original.soap_subjective || call.original.transcript}
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-zinc-700/50">
                      <div className="flex items-center text-xs text-zinc-500">
                        <Clock className="h-3 w-3 mr-1" />
                        {call.audio_duration ? `${call.audio_duration.toFixed(0)}s` : (systemLanguage === 'ja' ? '提供なし' : 'Not Provided')}
                      </div>
                      {call.urgency_score > 0 && (
                        <div className="text-xs font-bold whitespace-nowrap" style={{ color: COLORS[urgency] || COLORS.LOW }}>
                          {call.urgency_score}/100 {TRANSLATIONS[systemLanguage].score}
                        </div>
                      )}

                      <button className="lg:hidden px-3 py-1 bg-zinc-700 hover:bg-zinc-600 rounded-md text-xs font-semibold text-white transition-colors">
                        {TRANSLATIONS[systemLanguage].viewDetails}
                      </button>
                    </div>
                  </div>
                );
              }) : (
                <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-zinc-800 rounded-xl">
                  <Activity className="h-16 w-16 text-zinc-700 mb-4 animate-pulse" />
                  <p className="text-xl text-zinc-400">{TRANSLATIONS[systemLanguage].waitingForCalls}</p>
                </div>
              )}
            </div>
          </div>



          {/* Right Column - Call Details (Responsive sizing) */}
          <div className={`${showMobileDetails ? 'fixed inset-0 z-50 bg-zinc-900 flex flex-col' : 'hidden lg:flex lg:flex-col'} lg:static lg:col-span-5 xl:col-span-2 lg:bg-zinc-900/50 lg:backdrop-blur-xl lg:border lg:border-zinc-800 lg:rounded-2xl p-4 lg:p-6 overflow-y-auto h-full scrollbar-thin scrollbar-thumb-zinc-700 hover:scrollbar-thumb-zinc-600`}>

            <button
              onClick={() => setShowMobileDetails(false)}
              className="lg:hidden absolute top-4 right-4 p-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-white z-50 shadow-lg border border-zinc-700"
            >
              <X size={20} />
            </button>
            {showRealtimeCall ? (
              <RealtimeCall
                systemLanguage={systemLanguage}
                patient={activeCallPatient}
                onBack={() => {
                  setShowRealtimeCall(false);
                  setActiveCallPatient(null);
                }}
                onCallComplete={() => {
                  fetchCalls();
                  fetchStats();
                }}
              />
            ) : selectedCall ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold text-white flex items-center">
                    <FileText className="h-6 w-6 mr-3 text-blue-400" />
                    {TRANSLATIONS[systemLanguage].callDetails}
                  </h3>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={clearSelection}
                      className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
                    >
                      <X size={20} />
                    </button>
                  </div>
                </div>

                {/* Patient Identity (Compact) */}
                <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 rounded-xl p-4 border border-blue-500/20 shadow-sm mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <User className="h-4 w-4 text-blue-400" />
                      <span className="text-white font-bold text-sm tracking-tight">{TRANSLATIONS[systemLanguage].patientIdentity}</span>
                      {patientJourneyStatus?.exists && (
                        <span
                          className="ml-2 px-1.5 py-0.5 bg-purple-500/20 border border-purple-500/50 text-purple-300 text-[9px] rounded-full flex items-center gap-1 cursor-pointer hover:bg-purple-500/30 transition-colors"
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowPatientJourney(true);
                          }}
                          title={`Found ${patientJourneyStatus.event_count} past visits`}
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
                          History
                        </span>
                      )}
                    </div>
                    <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 rounded text-[10px] font-black border border-indigo-500/20 uppercase">
                      {translateCondition(selectedCall.disease)}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                    <div className="flex flex-col">
                      <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">{TRANSLATIONS[systemLanguage].name}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-20 mt-1" /> : (
                        <span className="text-white text-xs font-semibold truncate">{selectedCall.patient_name || parseField(selectedCall.soap_objective, 'Name')}</span>
                      )}
                    </div>
                    <div className="flex flex-col text-right">
                      <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">{TRANSLATIONS[systemLanguage].age}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-8 mt-1 ml-auto" /> : (
                        <span className="text-blue-300 text-xs font-semibold truncate">{parseField(selectedCall.soap_objective, 'Age')}</span>
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">{TRANSLATIONS[systemLanguage].phone}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-16 mt-1" /> : (
                        <span className="text-white text-xs font-semibold truncate">{selectedCall.phone || parseField(selectedCall.soap_objective, 'Phone')}</span>
                      )}
                    </div>
                    <div className="flex flex-col text-right">
                      <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">{TRANSLATIONS[systemLanguage].blood}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-6 mt-1 ml-auto" /> : (
                        <span className="text-red-400 text-xs font-black truncate">{parseField(selectedCall.soap_objective, 'Blood')}</span>
                      )}
                    </div>
                    <div className="flex flex-col col-span-2 mt-1 pt-1 border-t border-white/5">
                      <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">{TRANSLATIONS[systemLanguage].address}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-full mt-1" /> : (
                        <span className="text-zinc-300 text-[10px] leading-tight line-clamp-1">{parseField(selectedCall.soap_objective, 'Address')}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* 1. Triage Assessment */}
                <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700 mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-white font-bold flex items-center text-md">
                      <AlertTriangle className="h-5 w-5 mr-2 text-orange-400" />
                      {TRANSLATIONS[systemLanguage].triageLanguageMarkers}
                    </h4>
                  </div>
                  <div className="mb-3">
                    <div className="flex justify-between text-[10px] text-zinc-500 mb-1.5 uppercase font-bold tracking-wider">
                      <span>{TRANSLATIONS[systemLanguage].urgencyConfidence}</span>
                      {isTranslating ? <Skeleton className="skeleton-text w-8" /> : <span>{selectedCall.urgency_score || 0}%</span>}
                    </div>
                    <div className="w-full bg-zinc-700 rounded-full h-1.5">
                      <div
                        className={`h-full rounded-full transition-all duration-1000 ${isTranslating ? 'animate-pulse opacity-40' : ''}`}
                        style={{
                          width: `${selectedCall.urgency_score || 0}%`,
                          backgroundColor: COLORS[selectedCall.urgency_level] || COLORS.LOW
                        }}
                      />
                    </div>
                  </div>
                  {isTranslating ? (
                    <div className="space-y-2 mb-4">
                      <Skeleton className="skeleton-text w-full" />
                      <Skeleton className="skeleton-text w-5/6" />
                    </div>
                  ) : (
                    <div className="space-y-2 mb-4">
                      <p className="text-zinc-300 text-xs leading-relaxed italic">"{selectedCall.urgency_reasoning || TRANSLATIONS[systemLanguage].noReasoningProvided}"</p>
                      {dualLanguage && selectedCall.original?.urgency?.reasoning && selectedCall.original.urgency.reasoning !== selectedCall.urgency_reasoning && (
                        <p className="text-zinc-500 text-[11px] leading-relaxed italic border-t border-white/5 pt-2">"{selectedCall.original.urgency.reasoning}"</p>
                      )}
                    </div>
                  )}

                  <button
                    onClick={() => setShowMarkersFullscreen(true)}
                    className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 text-white rounded-xl shadow-lg shadow-purple-900/20 group transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-white/10 rounded-lg group-hover:scale-110 transition-transform">
                          <Brain className="h-5 w-5 text-purple-200" />
                        </div>
                        <div className="text-left font-bold">
                          <div className="text-[10px] text-purple-300 uppercase tracking-widest">{TRANSLATIONS[systemLanguage].cognitiveCheck}</div>
                          <div className="text-sm">{TRANSLATIONS[systemLanguage].viewLanguageMarkers}</div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-[8px] bg-white/10 px-1.5 py-0.5 rounded text-white font-black uppercase tracking-tighter mb-1 border border-white/10">{TRANSLATIONS[systemLanguage].stable}</span>
                        <span className="text-[7px] text-purple-300 font-bold uppercase">{TRANSLATIONS[systemLanguage].noDementia}</span>
                      </div>
                    </div>
                  </button>
                </div>

                {/* 2. SOAP Assessment */}
                <div className="mb-6">
                  <h4 className="text-white font-bold mb-4 flex items-center text-md">
                    <FileText className="h-5 w-5 mr-2 text-indigo-400" />
                    {TRANSLATIONS[systemLanguage].soapClinicalAnalysis}
                  </h4>
                  <div className="space-y-2.5">
                    <SOAPSection
                      title={TRANSLATIONS[systemLanguage].subjective}
                      content={selectedCall.soap_subjective}
                      color="blue"
                      isTranslating={isTranslating}
                      dualMode={dualLanguage}
                      originalContent={selectedCall.original?.soap?.subjective}
                      originalLang={selectedCall.language}
                    />
                    <SOAPSection
                      title={TRANSLATIONS[systemLanguage].objective}
                      content={selectedCall.soap_objective}
                      color="green"
                      isTranslating={isTranslating}
                      dualMode={dualLanguage}
                      originalContent={selectedCall.original?.soap?.objective}
                      originalLang={selectedCall.language}
                    />
                    <SOAPSection
                      title={TRANSLATIONS[systemLanguage].assessment}
                      content={selectedCall.soap_assessment}
                      color="yellow"
                      isTranslating={isTranslating}
                      dualMode={dualLanguage}
                      originalContent={selectedCall.original?.soap?.assessment}
                      originalLang={selectedCall.language}
                    />
                    <SOAPSection
                      title={TRANSLATIONS[systemLanguage].plan}
                      content={selectedCall.soap_plan}
                      color="purple"
                      isTranslating={isTranslating}
                      dualMode={dualLanguage}
                      originalContent={selectedCall.original?.soap?.plan}
                      originalLang={selectedCall.language}
                    />
                  </div>
                </div>

                {/* 3. BLEU Score / Quality */}
                <div className="mb-6">
                  <h4 className="text-white font-bold mb-3 flex items-center text-md">
                    <Zap className="h-5 w-5 mr-2 text-yellow-400" />
                    {TRANSLATIONS[systemLanguage].systemPerformanceBLEU}
                  </h4>
                  <button
                    onClick={() => {
                      setQualityCallId(selectedCall.call_id);
                      setShowQualityDashboard(true);
                    }}
                    className="w-full px-4 py-3 bg-zinc-800/80 border border-blue-500/30 hover:border-blue-500/60 hover:bg-blue-900/20 text-blue-100 rounded-xl flex items-center justify-between transition-all group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-500/20 rounded-lg group-hover:scale-110 transition-transform">
                        <Activity className="h-5 w-5 text-blue-400" />
                      </div>
                      <div className="text-left font-bold">
                        <div className="text-[10px] text-zinc-400 uppercase tracking-tighter">{TRANSLATIONS[systemLanguage].extractionQuality}</div>
                        <div className="text-sm text-blue-400 tracking-tight">{TRANSLATIONS[systemLanguage].systemValidated}</div>
                      </div>
                    </div>
                    <div className="bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-lg">
                      <span className="text-[10px] text-emerald-400 font-black tracking-widest uppercase italic">{TRANSLATIONS[systemLanguage].bleuOK}</span>
                    </div>
                  </button>
                </div>

                {/* 4. Full Transcription */}
                <div className="bg-cyan-500/5 rounded-xl p-4 border-l-4 border-cyan-500/50 shadow-inner">
                  <h4 className="text-white font-bold mb-3 flex items-center text-md">
                    <MessageSquare className="h-5 w-5 mr-2 text-cyan-400" />
                    {TRANSLATIONS[systemLanguage].clinicalTranscription}
                  </h4>
                  {isTranslating ? (
                    <div className="space-y-2">
                      <Skeleton className="skeleton-text w-full h-20" />
                    </div>
                  ) : (
                    <>
                      <div className="p-3 bg-black/40 rounded-lg text-xs text-cyan-100/70 max-h-40 overflow-y-auto whitespace-pre-wrap leading-relaxed font-mono border border-cyan-500/10 scrollbar-thin scrollbar-thumb-cyan-500/20">
                        {selectedCall.transcript || TRANSLATIONS[systemLanguage].noTranscriptionAvailable}
                      </div>
                      {dualLanguage && selectedCall.original?.transcript && selectedCall.original.transcript !== selectedCall.transcript && (
                        <div className="mt-2 p-3 bg-zinc-900 rounded-lg text-[10px] text-zinc-500 italic max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed border border-white/5">
                          <p className="font-bold mb-1 uppercase text-[#666] tracking-tighter">Original Transcript</p>
                          {selectedCall.original.transcript}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-zinc-500">
                <Activity className="h-20 w-20 mb-4 opacity-20" />
                <p className="text-xl">{TRANSLATIONS[systemLanguage].selectCallToViewDetails}</p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Fullscreen Language Markers */}
      {
        showMarkersFullscreen && selectedCall && (
          <div className="fixed inset-0 z-50 overflow-auto bg-slate-950">
            <LanguageMarkersDashboard
              callId={selectedCall.call_id}
              onBack={() => setShowMarkersFullscreen(false)}
              systemLanguage={systemLanguage}
            />
          </div>
        )
      }

      {
        showQualityDashboard && (
          <div className="fixed inset-0 z-50 overflow-auto bg-slate-950">
            <BleuScoreQualityMetrics
              callId={qualityCallId}
              onBack={() => setShowQualityDashboard(false)}
              systemLanguage={systemLanguage}
            />
          </div>
        )
      }

      {/* Image Lightbox */}
      {
        selectedImage && (
          <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-8" onClick={() => setSelectedImage(null)}>
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute top-6 right-6 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-all"
            >
              <X className="h-6 w-6" />
            </button>
            <img
              src={selectedImage}
              alt="Enlarged"
              className="max-w-full max-h-full object-contain rounded-xl"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        )
      }

      {/* Text Input Modal */}
      {
        showTextInput && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-6 w-full max-w-3xl shadow-2xl overflow-y-auto max-h-[90vh]">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-600/20 rounded-lg">
                    <MessageSquare className="h-6 w-6 text-blue-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-white">{TRANSLATIONS[systemLanguage].manualMedicalInput}</h3>
                </div>
                <button onClick={() => setShowTextInput(false)} className="p-2 hover:bg-zinc-800 rounded-full text-zinc-400 hover:text-white transition-colors">
                  <X size={24} />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1.5 ml-1">{TRANSLATIONS[systemLanguage].name}</label>
                  <input
                    type="text"
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    placeholder={TRANSLATIONS[systemLanguage].enterPatientName}
                    value={patientInput}
                    onChange={(e) => setPatientInput(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1.5 ml-1">{TRANSLATIONS[systemLanguage].attendingMD}</label>
                  <input
                    type="text"
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    placeholder={TRANSLATIONS[systemLanguage].enterDoctorName}
                    value={doctorInput}
                    onChange={(e) => setDoctorInput(e.target.value)}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1.5 ml-1">{TRANSLATIONS[systemLanguage].medicalCondition}</label>
                  <select
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    value={diseaseInput}
                    onChange={(e) => setDiseaseInput(e.target.value)}
                  >
                    <option value="">{TRANSLATIONS[systemLanguage].selectCondition}</option>
                    <option value="COVID-19">{TRANSLATIONS[systemLanguage].conditionCOVID}</option>
                    <option value="Heart Attack">{TRANSLATIONS[systemLanguage].conditionHeartAttack}</option>
                    <option value="Stroke">{TRANSLATIONS[systemLanguage].conditionStroke}</option>
                    <option value="Severe Fall">{TRANSLATIONS[systemLanguage].conditionTrauma}</option>
                    <option value="Respiratory Distress">{TRANSLATIONS[systemLanguage].conditionRespiratory}</option>
                    <option value="Cardiac Arrest">{TRANSLATIONS[systemLanguage].conditionCardiac}</option>
                    <option value="Hypoglycemia">{TRANSLATIONS[systemLanguage].conditionHypo}</option>
                    <option value="Anaphylaxis">{TRANSLATIONS[systemLanguage].conditionAnaphylaxis}</option>
                    <option value="Unknown">{TRANSLATIONS[systemLanguage].conditionUnknown}</option>
                  </select>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1.5 ml-1">{TRANSLATIONS[systemLanguage].clinicalTranscript}</label>
                <textarea
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-4 text-white h-48 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-y"
                  placeholder={TRANSLATIONS[systemLanguage].typeObservations}
                  value={textInputVal}
                  onChange={(e) => setTextInputVal(e.target.value)}
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={handleTextSubmit}
                  disabled={isProcessingText || !textInputVal.trim()}
                  className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-700 text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  {isProcessingText ? (
                    <>
                      <Loader className="h-5 w-5 animate-spin" />
                      <span>{TRANSLATIONS[systemLanguage].processing}</span>
                    </>
                  ) : (
                    <>
                      <Activity className="h-5 w-5" />
                      <span>{TRANSLATIONS[systemLanguage].processData}</span>
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowTextInput(false)}
                  className="px-6 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-bold py-3 rounded-lg transition-colors"
                >
                  {TRANSLATIONS[systemLanguage].cancel}
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Notification */}
      {
        notification && (
          <div className={`fixed bottom-6 right-6 px-6 py-4 rounded-xl shadow-2xl text-white font-medium flex items-center bg-zinc-800 border border-zinc-700 animate-in slide-in-from-bottom-4 z-50`}>
            {notification.type === 'error' ? <AlertTriangle className="mr-3 text-red-400" size={20} /> : <div className="w-2 h-2 rounded-full bg-green-400 mr-3"></div>}
            {notification.message}
          </div>
        )
      }
    </div >
  );
}

function MetricCard({ title, value, icon, trend, trendUp, color }) {
  const colorMap = {
    blue: { bg: 'from-blue-500/20 to-blue-600/10', border: 'border-blue-500/30', text: 'text-blue-400' },
    red: { bg: 'from-red-500/20 to-red-600/10', border: 'border-red-500/30', text: 'text-red-400' },
    green: { bg: 'from-green-500/20 to-green-600/10', border: 'border-green-500/30', text: 'text-green-400' },
    purple: { bg: 'from-purple-500/20 to-purple-600/10', border: 'border-purple-500/30', text: 'text-purple-400' }
  };

  const colors = colorMap[color] || colorMap.blue;

  return (
    <div className={`relative bg-gradient-to-br ${colors.bg} border ${colors.border} rounded-xl p-2 lg:p-6 overflow-hidden group hover:scale-105 transition-transform`}>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

      <div className="relative flex justify-between items-start">
        <div>
          <p className="text-zinc-400 text-[10px] lg:text-sm font-semibold mb-1 lg:mb-2 uppercase whitespace-normal leading-tight">{title}</p>
          <h4 className="text-xl lg:text-4xl font-bold text-white mb-0 lg:mb-2">{value}</h4>
          {trend && (
            <div className="hidden lg:flex items-center text-xs">
              <div className={`flex items-center px-2 py-1 rounded-full font-bold ${trendUp !== undefined
                ? trendUp ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                : 'bg-blue-500/20 text-blue-400'
                }`}>
                {trendUp !== undefined && (
                  trendUp ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {trend}
              </div>
            </div>
          )}
        </div>
        <div className={`hidden lg:block p-3 bg-white/5 rounded-xl border border-white/10 ${colors.text}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function SOAPSection({ title, content, color, isTranslating, dualMode, originalContent, originalLang }) {
  const colors = {
    blue: 'border-blue-500 bg-blue-500/10',
    green: 'border-green-500 bg-green-500/10',
    yellow: 'border-yellow-500 bg-yellow-500/10',
    purple: 'border-purple-500 bg-purple-500/10'
  };

  if (isTranslating) {
    return (
      <div className={`rounded-lg p-3 lg:p-4 border-l-4 ${colors[color]} mb-2 opacity-50`}>
        <div className="skeleton-title w-24 mb-3 animate-shimmer"></div>
        <div className="space-y-2">
          <div className="skeleton-text w-full animate-shimmer"></div>
          <div className="skeleton-text w-5/6 animate-shimmer"></div>
          <div className="skeleton-text w-4/6 animate-shimmer"></div>
        </div>
      </div>
    );
  }

  if (!content) return null;

  return (
    <div className={`rounded-lg p-3 lg:p-4 border-l-4 ${colors[color]} mb-2 translation-content ${isTranslating ? 'translation-switching' : ''}`}>
      <div className="flex justify-between items-center mb-1 lg:mb-2">
        <p className="text-white text-[10px] lg:text-xs font-bold uppercase tracking-wider">{title}</p>
        {dualMode && originalContent && (
          <span className="text-[8px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-zinc-500 uppercase font-bold tracking-tighter">
            DUAL VIEW
          </span>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-slate-200 text-xs lg:text-sm leading-relaxed whitespace-pre-wrap">
          {content}
        </p>

        {dualMode && originalContent && originalContent !== content && (
          <div className="mt-3 pt-3 border-t border-white/5">
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-[8px] text-zinc-500 font-bold uppercase">{originalLang === 'ja' ? 'Original (Japanese)' : 'Original (English)'}</span>
            </div>
            <p className="text-zinc-500 text-[11px] lg:text-xs leading-relaxed italic whitespace-pre-wrap">
              {originalContent}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default EmergencyManager;