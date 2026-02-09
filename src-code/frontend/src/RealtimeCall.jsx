import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Phone, Activity, AlertCircle, Loader, X, User } from 'lucide-react';

function RealtimeCall({ onCallComplete, onBack, patient = null, systemLanguage = 'en' }) {
  const [isRecording, setIsRecording] = useState(false);
  const [callId, setCallId] = useState(null);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [soap, setSoap] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [wordCount, setWordCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const TRANSLATIONS = {
    en: {
      title: "Real-Time Emergency Call",
      transcribing: "Transcribing...",
      connecting: "Connecting...",
      recording: "🔴 RECORDING",
      finalizing: "⏳ Finalizing...",
      completed: "✅ Completed",
      error: "❌ Error",
      ready: "Ready",
      startCall: "Start Live Call",
      endCall: "End Call",
      liveTranscript: "Live Transcript",
      wordsCaptured: "Words Captured",
      liveSoapAnalysis: "Live SOAP Analysis",
      subjective: "Subjective",
      objective: "Objective",
      assessment: "Assessment",
      plan: "Plan",
      listening: "Listening...",
      speakTip: "Speak into your microphone...",
      noTranscript: "No transcript available yet. Start speaking to see transcription.",
      tip: "Speak clearly. Updates every 1 second.",
      micError: "Microphone access denied. Please allow microphone access."
    },
    ja: {
      title: "緊急通報リアルタイム処理",
      transcribing: "文字起こし中...",
      connecting: "接続中...",
      recording: "🔴 通話中",
      finalizing: "⏳ 解析中...",
      completed: "✅ 完了",
      error: "❌ エラー",
      ready: "待機中",
      startCall: "ライブ通話開始",
      endCall: "通話終了",
      liveTranscript: "リアルタイム文字起こし",
      wordsCaptured: "取得単語数",
      liveSoapAnalysis: "リアルタイムSOAP解析",
      subjective: "主観的所見 (S)",
      objective: "客観的所見 (O)",
      assessment: "評価 (A)",
      plan: "計画 (P)",
      listening: "音声受領中...",
      speakTip: "マイクに向かって話してください...",
      noTranscript: "文字起こしデータがまだありません。話を始めるとここに表示されます。",
      tip: "はっきりと話してください。1秒ごとに更新されます。",
      micError: "マイクへのアクセスが拒否されました。設定を確認してください。"
    }
  };

  const t = TRANSLATIONS[systemLanguage] || TRANSLATIONS.en;

  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    // Cleanup only when component unmounts

    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        console.log('🔌 Cleaning up WebSocket...');
        wsRef.current.close();
      }
      if (mediaRecorderRef.current) {
        try {
          mediaRecorderRef.current.stop();
          mediaRecorderRef.current.stream?.getTracks().forEach(track => track.stop());
        } catch (e) {
          console.log('MediaRecorder already stopped');
        }
      }
    };
  }, []);

  const startCall = async () => {
    console.log('🎙️ START CALL CLICKED!');
    try {
      setStatus('connecting');
      setError(null);
      setLiveTranscript('');
      setSoap(null);
      setWordCount(0);

      const ws = new WebSocket('ws://localhost:8000/ws/realtime-call');
      wsRef.current = ws;

      ws.onopen = async () => {
        console.log('✅ WebSocket connected');

        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
              channelCount: 1,
              sampleRate: 16000,
              echoCancellation: true,
              noiseSuppression: true
            }
          });

          // PING-PONG RECORDING we have other recording options like single recorder or multiple recorders 
          // but ping-pong is the best option for real-time call because it allows us to switch between recorders every 5 seconds 
          // better than the others options because its more stable and less likely to drop the call
          const recorders = [
            new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' }),
            new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
          ];

          let activeIndex = 0;

          recorders.forEach((recorder) => {
            recorder.ondataavailable = async (event) => {
              if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                const reader = new FileReader();
                reader.onloadend = () => {
                  const base64 = reader.result.split(',')[1];
                  ws.send(JSON.stringify({ action: 'audio', data: base64 }));
                };
                reader.readAsDataURL(event.data);
              }
            };
          });

          mediaRecorderRef.current = {
            stop: () => {
              recorders.forEach(r => r.state !== 'inactive' && r.stop());
              clearInterval(window.recordingInterval);
              stream.getTracks().forEach(t => t.stop());
            }
          };

          const switchRecorders = () => {
            const nextIndex = (activeIndex + 1) % 2;
            const current = recorders[activeIndex];
            const next = recorders[nextIndex];

            next.start();
            if (current.state === 'recording') {
              current.stop();
            }
            activeIndex = nextIndex;
          };

          recorders[0].start();
          window.recordingInterval = setInterval(switchRecorders, 5000);
          console.log('🎙️ Recording started (Ping-Pong Mode)');

          ws.send(JSON.stringify({
            action: 'start',
            language: systemLanguage
          }));

          setStatus('recording');
          setIsRecording(true);
        } catch (err) {
          console.error('❌ Microphone error:', err);
          setError(t.micError);
          setStatus('error');
          ws.close();
        }
      };

      const bc = new BroadcastChannel('emergency_system_channel');

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 Received:', data);

        if (!mountedRef.current) return;

        // Broadcast live updates to other windows (like TransparentMonitor)
        if (data.status === 'processing' || data.status === 'completed' || data.status === 'started') {
          bc.postMessage({
            type: 'LIVE_UPDATE',
            call_id: data.call_id || callId,
            transcript: data.full_transcript || data.transcript || '',
            status: data.status,
            soap: data.soap,
            language: data.language || systemLanguage
          });
        }

        if (data.status === 'started') {
          setCallId(data.call_id);
          console.log('✅ Call started with ID:', data.call_id);
        }
        else if (data.status === 'buffering') {
          setIsProcessing(false);
          console.log('⏳ Buffering audio...');
        }
        else if (data.status === 'processing') {
          console.log('🔄 Processing audio chunk...');
          setIsProcessing(true);

          if (data.full_transcript) {
            setLiveTranscript(data.full_transcript);
          }

          if (data.word_count !== undefined) {
            setWordCount(data.word_count);
          }

          if (data.soap) {
            setSoap(data.soap);
          }

          setTimeout(() => setIsProcessing(false), 500);
        }
        else if (data.status === 'completed') {
          // Final broadcast with all data
          bc.postMessage({
            type: 'LIVE_UPDATE',
            ...data,
            language: systemLanguage
          });

          setStatus('completed');
          setIsRecording(false);
          setIsProcessing(false);

          if (data.transcript) {
            setLiveTranscript(data.transcript);
          }
          if (data.soap) {
            setSoap(data.soap);
          }

          if (onCallComplete) {
            onCallComplete(data);
          }
        }
        else if (data.status === 'error') {
          setError(data.error || 'An error occurred');
          setStatus('error');
          setIsRecording(false);
          setIsProcessing(false);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setError('Connection error');
        setStatus('error');
        setIsRecording(false);
        setIsProcessing(false);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket closed');
        setIsRecording(false);
        setIsProcessing(false);
      };

    } catch (err) {
      console.error('❌ Start call error:', err);
      setError(err.message);
      setStatus('error');
    }
  };

  const stopCall = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'end' }));
      setStatus('processing');
      setIsProcessing(true);
    }

    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }

    setIsRecording(false);
  };

  const getStatusColor = () => {
    switch (status) {
      case 'recording': return 'bg-red-600 animate-pulse';
      case 'connecting': return 'bg-yellow-600';
      case 'processing': return 'bg-blue-600 animate-pulse';
      case 'completed': return 'bg-green-600';
      case 'error': return 'bg-red-800';
      default: return 'bg-gray-600';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connecting': return t.connecting;
      case 'recording': return t.recording;
      case 'processing': return t.finalizing;
      case 'completed': return t.completed;
      case 'error': return t.error;
      default: return t.ready;
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-800 overflow-hidden h-full flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-900 to-red-800 px-6 py-4 border-b border-red-700 shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Phone className="h-6 w-6 mr-2" />
            {t.title}
          </h2>
          <div className="flex items-center space-x-3">
            {isProcessing && (
              <div className="flex items-center space-x-2 text-yellow-300">
                <Loader className="h-4 w-4 animate-spin" />
                <span className="text-sm">{t.transcribing}</span>
              </div>
            )}
            <div className={`px-4 py-2 rounded-lg ${getStatusColor()} text-white font-bold text-sm`}>
              {getStatusText()}
            </div>
            {onBack && (
              <button
                onClick={onBack}
                className="p-2 hover:bg-red-800 rounded-lg text-red-200 hover:text-white transition-colors ml-2"
                title="Close Live Call"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6 flex-1 overflow-y-auto">
        {/* Patient Identity (if from Journey View) */}
        {patient && (
          <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <User className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Active Patient</p>
                <h4 className="text-white font-bold">{patient.name}</h4>
              </div>
            </div>
            <div className="text-right">
              <p className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Condition</p>
              <p className="text-blue-300 text-sm font-semibold">{patient.primary_condition || 'Unknown'}</p>
            </div>
          </div>
        )}

        {/* Call ID & Stats */}
        {callId && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <p className="text-slate-400 text-xs mb-1">Call ID</p>
              <p className="text-white font-mono text-sm">{callId}</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <p className="text-slate-400 text-xs mb-1">{t.wordsCaptured}</p>
              <p className="text-white font-bold text-2xl">{wordCount}</p>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-semibold">{t.error}</p>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex space-x-4">
          {!isRecording ? (
            <button
              onClick={startCall}
              disabled={status === 'connecting' || status === 'processing'}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white rounded-xl font-bold text-lg flex items-center justify-center space-x-3 transition-all shadow-lg disabled:cursor-not-allowed"
            >
              <Mic className="h-6 w-6" />
              <span>{status === 'connecting' ? t.connecting : t.startCall}</span>
            </button>
          ) : (
            <button
              onClick={stopCall}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white rounded-xl font-bold text-lg flex items-center justify-center space-x-3 transition-all shadow-lg"
            >
              <Square className="h-6 w-6" />
              <span>{t.endCall}</span>
            </button>
          )}
        </div>

        {/* Live Transcript */}
        {(liveTranscript || isRecording || callId) && (
          <div className="bg-slate-800/70 rounded-xl p-5 border border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-bold flex items-center">
                <Activity className="h-5 w-5 mr-2 text-blue-400" />
                {t.liveTranscript}
              </h3>
              {isRecording && (
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-red-400 text-sm font-medium">{t.listening}</span>
                </div>
              )}
            </div>
            <div className="max-h-64 overflow-y-auto bg-slate-900/50 rounded-lg p-4">
              {liveTranscript && liveTranscript.trim() ? (
                <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
                  {liveTranscript}
                </p>
              ) : (
                <p className="text-slate-500 text-sm italic">
                  {isRecording
                    ? t.speakTip
                    : t.noTranscript}
                </p>
              )}
            </div>
            {wordCount > 0 && (
              <div className="mt-3 text-xs text-slate-400">
                {t.wordsCaptured}: <span className="font-semibold text-blue-400">{wordCount}</span>
              </div>
            )}
          </div>
        )}

        {/* Live SOAP */}
        {soap && (
          <div className="space-y-3">
            <h3 className="text-white font-bold flex items-center">
              <Activity className="h-5 w-5 mr-2 text-green-400" />
              {t.liveSoapAnalysis}
            </h3>
            {['subjective', 'objective', 'assessment', 'plan'].map((section) => (
              soap[section] && (
                <div key={section} className="bg-slate-800/50 rounded-lg p-4 border-l-4 border-blue-500">
                  <p className="text-white text-xs font-bold uppercase mb-2 tracking-wider">
                    {t[section]}
                  </p>
                  <div className="space-y-2">
                    <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                      {soap[section].split('[EN Summary]:')[0]?.trim()}
                    </p>
                    {soap[section].includes('[EN Summary]:') && (
                      <div className="mt-2 pt-2 border-t border-white/5 bg-black/20 p-2 rounded border border-white/10">
                        <p className="text-[9px] text-blue-400 font-bold uppercase tracking-tighter mb-1">English Summary</p>
                        <p className="text-[11px] text-zinc-300 leading-tight italic">
                          {soap[section].split('[EN Summary]:')[1]?.trim()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )
            ))}
          </div>
        )}

        {/* Instructions */}
        {!isRecording && !liveTranscript && status === 'idle' && (
          <div className="text-center py-8">
            <div className="bg-slate-800/50 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
              <Mic className="h-12 w-12 text-slate-600" />
            </div>
            <p className="text-slate-400 text-lg mb-2">{t.ready}</p>
            <p className="text-slate-500 text-sm mb-4">
              {t.waitingCall}
            </p>
            <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-blue-300 text-xs">
                💡 <strong>Tip:</strong> {t.tip}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RealtimeCall;