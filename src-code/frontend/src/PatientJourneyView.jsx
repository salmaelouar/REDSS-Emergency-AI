import React, { useState, useEffect, useRef } from 'react';
import {
    ArrowLeft, Calendar, Clock, User, Mic, Save,
    Plus, Image as ImageIcon, Activity, AlertCircle,
    MessageSquare, Edit3, CheckCircle, Upload, Loader,
    Radio, Search, X, RefreshCw, Trash2, FileText
} from 'lucide-react';

export default function PatientJourneyView({ onBack, onStartLiveCall, systemLanguage = 'en' }) {
    const [patients, setPatients] = useState([]);
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [journeyEvents, setJourneyEvents] = useState([]);
    const [followUpNotes, setFollowUpNotes] = useState('');
    const [liveTranscript, setLiveTranscript] = useState('');
    const [newEvent, setNewEvent] = useState({ date: '', description: '' });
    const [editingIndex, setEditingIndex] = useState(null);
    const [showTextInput, setShowTextInput] = useState(false);
    const [textInputVal, setTextInputVal] = useState('');
    const [patientNameInput, setPatientNameInput] = useState('');
    const [doctorInput, setDoctorInput] = useState('');
    const [conditionInput, setConditionInput] = useState('');
    const [uploading, setUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const transcriptRef = useRef(null);
    const API_URL = 'http://localhost:8000';

    // Real-time Call Refs
    const wsRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const mountedRef = useRef(true);

    useEffect(() => {
        mountedRef.current = true;
        return () => {
            mountedRef.current = false;
            if (wsRef.current) wsRef.current.close();
            if (mediaRecorderRef.current) {
                try { mediaRecorderRef.current.stop(); } catch (e) { }
            }
        };
    }, []);

    const startRecordingCall = async () => {
        try {
            setIsRecording(true);
            const ws = new WebSocket('ws://localhost:8000/ws/realtime-call');
            wsRef.current = ws;

            ws.onopen = async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        audio: { channelCount: 1, sampleRate: 16000, echoCancellation: true, noiseSuppression: true }
                    });

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
                                    ws.send(JSON.stringify({ action: 'audio', data: reader.result.split(',')[1] }));
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
                        if (current.state === 'recording') current.stop();
                        activeIndex = nextIndex;
                    };

                    recorders[0].start();
                    window.recordingInterval = setInterval(switchRecorders, 5000);

                    ws.send(JSON.stringify({ action: 'start', language: systemLanguage }));
                } catch (err) {
                    console.error('Mic error:', err);
                    setIsRecording(false);
                    alert("Microphone access denied");
                }
            };

            ws.onmessage = (event) => {
                if (!mountedRef.current) return;
                const data = JSON.parse(event.data);

                // Handle different message types
                if (data.full_transcript) {
                    setLiveTranscript(data.full_transcript);
                } else if (data.transcript) {
                    setLiveTranscript(prev => prev + ' ' + data.transcript);
                }

                if (data.status === 'completed') {
                    setIsRecording(false);
                }
            };
        } catch (e) {
            console.error(e);
            setIsRecording(false);
        }
    };

    const stopRecordingCall = () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ action: 'end' }));
            wsRef.current.close();
        }
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
        setIsRecording(false);
    };

    const TRANSLATIONS = {
        en: {
            title: "Patient Journey Follow-Up",
            subtitle: "Track patient recovery and follow-up calls",
            selectPatient: "Select Patient",
            patientName: "Patient Name",
            callId: "ID",
            disease: "Condition",
            search: "Search patients...",
            journeyTimeline: "Journey Timeline",
            eventTimetable: "Event Timetable",
            followUpNotes: "Follow-Up Notes",
            liveTranscription: "Live Call Transcription",
            aiVisualization: "AI-Generated Journey Visualization",
            startRecording: "Start Recording",
            stopRecording: "Stop Recording",
            saveNotes: "Save Notes",
            addEvent: "Add Event",
            date: "Date",
            time: "Time",
            description: "Description",
            status: "Status",
            noPatientSelected: "Please select a patient to view their journey",
            segment: "Segment",
            summary: "Summary",
            timeline: "Timeline",
            visualOne: "Journey Overview",
            visualTwo: "Current Phase Detail",
            recordingActive: "Recording active...",
            notEmergency: "Follow-Up Call (Non-Emergency)",
            patientInfo: "Patient Information",
            lastContact: "Last Contact",
            nextFollowUp: "Next Follow-Up",
            liveCall: "Live Call",
            textInput: "Text Input",
            audioUpload: "Audio Upload",
            exportPDF: "Export PDF",
            newPatient: "New Patient",
            registerPatient: "Register Patient",
            age: "Age",
            sex: "Sex",
            phone: "Phone",
            street: "Street",
            bloodType: "Blood Type",
            allergies: "Allergies",
            medications: "Medications",
            medicalHistory: "Medical History",
            cancel: "Cancel",
            save: "Save",
            processing: "Processing...",
            processData: "Process Data",
            uploadAudio: "Upload Audio File",
            typeNotes: "Type observations or notes here...",
            patientExists: "Patient found in database!",
            noPatientFound: "No matching patient found",
            conditionStroke: "Stroke",
            conditionHeartAttack: "Heart Attack",
            conditionCOVID: "COVID-19",
            conditionTrauma: "Severe Fall",
            conditionRespiratory: "Respiratory Distress",
            conditionCardiac: "Cardiac Arrest",
            conditionAnaphylaxis: "Anaphylaxis",
            // New dashboard improvements
            overview: "Overview",
            totalPatients: "Total Patients",
            activeFollowUps: "Active Follow-Ups",
            completedEvents: "Completed Events",
            pendingEvents: "Pending Events",
            quickActions: "Quick Actions",
            recentActivity: "Recent Activity",
            patientStatus: "Patient Status",
            stable: "Stable",
            monitoring: "Monitoring",
            critical: "Critical",
            recovered: "Recovered",
            viewDetails: "View Details",
            editEvent: "Edit Event",
            deleteEvent: "Delete Event",
            markComplete: "Mark Complete",
            noEvents: "No events recorded",
            addFirstEvent: "Add your first event",
            syncAll: "Sync All Calls",
            clearAllData: "Clear All Data",
            confirmClear: "Are you sure you want to delete ALL patient data? This cannot be undone!",
            updateEvent: "Update Event",
            cancelEdit: "Cancel"
        },
        ja: {
            title: "患者の経過フォローアップ",
            subtitle: "患者の回復とフォローアップ通話を追跡",
            selectPatient: "患者を選択",
            patientName: "患者名",
            callId: "ID",
            disease: "症状",
            search: "患者を検索...",
            journeyTimeline: "経過タイムライン",
            eventTimetable: "イベント時刻表",
            followUpNotes: "フォローアップメモ",
            liveTranscription: "リアルタイム通話文字起こし",
            aiVisualization: "AI生成経過可視化",
            startRecording: "録音開始",
            stopRecording: "録音停止",
            saveNotes: "メモを保存",
            addEvent: "イベントを追加",
            date: "日付",
            time: "時刻",
            description: "説明",
            status: "状態",
            noPatientSelected: "経過を表示する患者を選択してください",
            segment: "セグメント",
            summary: "概要",
            timeline: "タイムライン",
            visualOne: "経過概要",
            visualTwo: "現在のフェーズ詳細",
            recordingActive: "録音中...",
            notEmergency: "フォローアップ通報（緊急ではない）",
            patientInfo: "患者情報",
            lastContact: "最終連絡",
            nextFollowUp: "次回フォローアップ",
            liveCall: "ライブ通話",
            textInput: "テキスト入力",
            audioUpload: "音声アップロード",
            exportPDF: "PDF出力",
            newPatient: "新規患者",
            registerPatient: "患者登録",
            age: "年齢",
            sex: "性別",
            phone: "電話番号",
            street: "住所",
            bloodType: "血液型",
            allergies: "アレルギー",
            medications: "服用薬",
            medicalHistory: "既往歴",
            cancel: "キャンセル",
            save: "保存",
            processing: "処理中...",
            processData: "データ処理",
            uploadAudio: "音声ファイルアップロード",
            typeNotes: "観察内容やメモを入力...",
            patientExists: "データベースに患者が見つかりました！",
            noPatientFound: "一致する患者が見つかりません",
            conditionStroke: "脳卒中",
            conditionHeartAttack: "心筋梗塞",
            conditionCOVID: "新型コロナウイルス",
            conditionTrauma: "転倒・外傷",
            conditionRespiratory: "呼吸困難",
            conditionCardiac: "心停止",
            conditionAnaphylaxis: "アナフィラキシー",
            // New dashboard improvements
            overview: "概要",
            totalPatients: "総患者数",
            activeFollowUps: "アクティブフォローアップ",
            completedEvents: "完了イベント",
            pendingEvents: "保留中イベント",
            quickActions: "クイックアクション",
            recentActivity: "最近のアクティビティ",
            patientStatus: "患者状態",
            stable: "安定",
            monitoring: "経過観察",
            critical: "重症",
            recovered: "回復",
            viewDetails: "詳細を表示",
            editEvent: "イベント編集",
            deleteEvent: "イベント削除",
            markComplete: "完了にする",
            noEvents: "イベント記録なし",
            addFirstEvent: "最初のイベントを追加",
            syncAll: "すべて同期",
            clearAllData: "すべてのデータを削除",
            confirmClear: "すべての患者データを削除してもよろしいですか？この操作は元に戻せません！",
            updateEvent: "イベント更新",
            cancelEdit: "キャンセル"
        }
    };

    const t = TRANSLATIONS[systemLanguage] || TRANSLATIONS.en;

    // Fetch patients on mount
    useEffect(() => {
        fetchPatients();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Auto-scroll transcript
    useEffect(() => {
        if (transcriptRef.current) {
            transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
        }
    }, [liveTranscript]);

    const fetchPatients = async () => {
        try {
            const response = await fetch(`${API_URL}/api/patients`);
            const data = await response.json();

            setPatients(data.patients || []);
            if (!data.patients || data.patients.length === 0) {
                console.log('No patients found.');
            } else if (selectedPatient) {
                // Auto-update selected patient if valid
                const updated = data.patients.find(p => p.patient_id === selectedPatient.patient_id);
                if (updated) setSelectedPatient(updated);
            }
        } catch (error) {
            console.error('Error fetching patients:', error);
        }
    };

    // Filter patients based on SEARCH (Name, ID, Street, Phone, DOB, Blood Type, etc.)
    const filteredPatients = patients.filter(patient => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            (patient.name && patient.name.toLowerCase().includes(query)) ||
            (patient.patient_id && patient.patient_id.toLowerCase().includes(query)) ||
            (patient.primary_condition && patient.primary_condition.toLowerCase().includes(query)) ||
            (patient.street && patient.street.toLowerCase().includes(query)) ||
            (patient.phone && patient.phone.toLowerCase().includes(query)) ||
            (patient.date_of_birth && patient.date_of_birth.toLowerCase().includes(query)) ||
            (patient.blood_type && patient.blood_type.toLowerCase().includes(query)) ||
            (patient.age && patient.age.toString().includes(query)) ||
            (patient.journey_events && (
                typeof patient.journey_events === 'string'
                    ? patient.journey_events.toLowerCase().includes(query)
                    : JSON.stringify(patient.journey_events).toLowerCase().includes(query)
            ))
        );
    });



    const syncAllCalls = async () => {
        if (!window.confirm(systemLanguage === 'ja'
            ? 'すべての緊急通話を同期しますか？これには時間がかかる場合があります。'
            : 'Sync all emergency calls (past and present) to Patient Journey? This might take a moment.')) return;

        try {
            const response = await fetch(`${API_URL}/api/patients/import-from-emergency-calls`, {
                method: 'POST'
            });

            if (response.ok) {
                const result = await response.json();
                alert(systemLanguage === 'ja'
                    ? `同期完了: ${result.imported} 件インポート, ${result.skipped} 件スキップ`
                    : `Sync complete: ${result.imported} imported, ${result.skipped} skipped.`);
                await fetchPatients();
            } else {
                throw new Error('Sync failed');
            }
        } catch (e) {
            console.error(e);
            alert(systemLanguage === 'ja' ? "同期に失敗しました" : "Sync failed");
        }
    };

    // Removed importFromEmergencyCalls - no longer needed

    const selectPatient = async (patient) => {
        // Parse and sort events first for consistency
        let events = patient.journey_events || [];
        if (typeof events === 'string') {
            try {
                events = JSON.parse(events);
            } catch (e) {
                console.error("Failed to parse journey events", e);
                events = [];
            }
        }

        // Sort by date and re-index
        events.sort((a, b) => new Date(a.date) - new Date(b.date));
        events = events.map((ev, i) => ({ ...ev, segment: i + 1 }));

        // Use sorted version for state and visualizations
        const sortedPatient = { ...patient, journey_events: events };

        setSelectedPatient(sortedPatient);
        setEditingIndex(null);
        setNewEvent({ date: '', description: '' });
        setJourneyEvents(events);

        // Load existing notes
        setFollowUpNotes(patient.follow_up_notes || '');
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

            if (!response.ok) throw new Error('Upload failed');

            alert('Audio processed successfully! Check emergency calls.');
            fetchPatients();
        } catch (err) {
            console.error(err);
            alert('Failed to process audio file');
        } finally {
            setUploading(false);
        }
    };


    const handleTextSubmit = async () => {
        if (!textInputVal.trim()) return;

        setIsProcessing(true);
        try {
            // First, process the text to extract patient info
            const processResponse = await fetch(`${API_URL}/api/process-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: textInputVal,
                    patient_name: patientNameInput || selectedPatient?.name || '',
                    doctor_name: doctorInput || '',
                    disease: conditionInput || selectedPatient?.primary_condition || '',
                    language: systemLanguage
                })
            });

            console.log("Patient Journey text process status:", processResponse.status);
            const processData = await processResponse.json();
            console.log("Patient Journey process result:", processData);

            if (processResponse.ok) {

                // Extract patient info
                const patientName = processData.patient_name || `Patient-${Date.now()}`;
                const condition = processData.disease || 'General care';
                const soapNotes = processData.soap || {};

                // Create patient directly in Patient Journey database
                const patientData = {
                    name: patientName,
                    primary_condition: condition,
                    medical_history: soapNotes.subjective || textInputVal,
                    clinical_notes: soapNotes.assessment || '',
                    follow_up_notes: soapNotes.plan || '',
                    journey_events: JSON.stringify([{
                        segment: 1,
                        date: new Date().toISOString().split('T')[0],
                        time: new Date().toLocaleTimeString(),
                        description: `Initial contact: ${condition}`,
                        status: 'completed'
                    }])
                };

                const createResponse = await fetch(`${API_URL}/api/patients`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(patientData)
                });

                console.log("Patient Journey create response:", createResponse.status);
                const createData = await createResponse.json();
                console.log("Patient Journey create data:", createData);

                if (createResponse.ok) {
                    // Update state and select the new patient immediately
                    const newPatient = createData.patient;
                    await fetchPatients();
                    if (newPatient) {
                        selectPatient(newPatient);
                    }

                    setShowTextInput(false);
                    setTextInputVal('');
                    setPatientNameInput('');
                    setDoctorInput('');
                    setConditionInput('');

                    alert(systemLanguage === 'ja'
                        ? `${patientName} を登録しました`
                        : `✓ Patient "${patientName}" registered successfully!`);
                } else {
                    alert(`Error creating patient: ${createData.detail || 'Unknown error'}`);
                }
            } else {
                alert(`Error processing text: ${processData.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error("Patient Journey process error:", err);
            alert(`System Error: ${err.message}`);
        } finally {
            setIsProcessing(false);
        }
    };


    const saveFollowUpNotes = async () => {
        if (!selectedPatient) {
            alert('Please select a patient first');
            return;
        }

        try {
            const updateData = {
                follow_up_notes: followUpNotes
            };

            if (liveTranscript) {
                updateData.clinical_notes = (selectedPatient.clinical_notes || '') + '\n\n[Follow-up]: ' + liveTranscript;
            }

            console.log('Saving notes for:', selectedPatient.patient_id, updateData);

            const response = await fetch(`${API_URL}/api/patients/${selectedPatient.patient_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                alert('✓ Notes saved successfully!');
                await fetchPatients();

                // Refresh selected patient
                const refreshResponse = await fetch(`${API_URL}/api/patients`);
                const data = await refreshResponse.json();
                const updated = data.patients?.find(p => p.patient_id === selectedPatient.patient_id);
                if (updated) {
                    setSelectedPatient(updated);
                }
            }
        } catch (error) {
            console.error('Error saving notes:', error);
            alert('Failed to save notes: ' + error.message);
        }
    };

    const addOrUpdateJourneyEvent = async () => {
        if (!newEvent.date || !newEvent.description || !selectedPatient) return;

        let updatedEvents = [...journeyEvents];

        if (editingIndex !== null && editingIndex >= 0) {
            // Update existing
            updatedEvents[editingIndex] = {
                ...updatedEvents[editingIndex],
                date: newEvent.date,
                description: newEvent.description
            };
        } else {
            // Add new
            const event = {
                segment: journeyEvents.length + 1,
                date: newEvent.date,
                time: new Date().toLocaleTimeString(),
                description: newEvent.description,
                status: 'pending'
            };
            updatedEvents.push(event);
        }

        // Sort by date and re-index segments to ensure chronological order
        updatedEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
        updatedEvents = updatedEvents.map((ev, i) => ({ ...ev, segment: i + 1 }));

        try {
            // Use PUT to update the entire list
            const updateBody = {
                journey_events: JSON.stringify(updatedEvents)
            };

            const response = await fetch(`${API_URL}/api/patients/${selectedPatient.patient_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateBody)
            });

            if (response.ok) {
                // Update local state
                setJourneyEvents(updatedEvents);
                setNewEvent({ date: '', description: '' });
                setEditingIndex(null);

                // Refresh full data
                await fetchPatients();

                // Manual update
                const updatedP = { ...selectedPatient, journey_events: updatedEvents };
                setSelectedPatient(updatedP);
                // No longer need to generate timeline image - using CSS timeline
            }
        } catch (error) {
            console.error('Error saving event:', error);
        }
    };

    const startEditEvent = (index) => {
        const ev = journeyEvents[index];
        setNewEvent({ date: ev.date, description: ev.description });
        setEditingIndex(index);
    };

    const exportToPDF = async () => {
        if (!selectedPatient) return;

        try {
            const { default: jsPDF } = await import('jspdf');
            const { default: autoTable } = await import('jspdf-autotable');

            const doc = new jsPDF('p', 'mm', 'a4');
            const pageWidth = doc.internal.pageSize.getWidth();
            const brandColor = [124, 58, 237]; // Purple 600

            // 1. BRANDED HEADER
            doc.setFillColor(brandColor[0], brandColor[1], brandColor[2]);
            doc.rect(0, 0, pageWidth, 40, 'F');

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(24);
            doc.setFont(undefined, 'bold');
            doc.text('PATIENT JOURNEY REPORT', 20, 20);

            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
            doc.text(`ID: ${selectedPatient.patient_id}`, pageWidth - 20, 30, { align: 'right' });

            // 2. PATIENT INFO HIGHLIGHT BOX
            let yPos = 50;
            doc.setDrawColor(brandColor[0], brandColor[1], brandColor[2]);
            doc.setLineWidth(0.5);
            doc.line(20, yPos, 190, yPos);
            yPos += 10;

            doc.setTextColor(0, 0, 0);
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text('PATIENT DETAILS', 20, yPos);
            yPos += 10;

            const infoData = [
                ['Name', selectedPatient.name || 'N/A', 'Age / Sex', `${selectedPatient.age || 'N/A'} / ${selectedPatient.sex || 'N/A'}`],
                ['Condition', selectedPatient.primary_condition || 'N/A', 'Phone', selectedPatient.phone || 'N/A'],
                ['Address', selectedPatient.street || 'N/A', 'Blood Type', selectedPatient.blood_type || 'N/A']
            ];

            autoTable(doc, {
                startY: yPos,
                body: infoData,
                theme: 'plain',
                styles: { fontSize: 10, cellPadding: 2 },
                columnStyles: {
                    0: { fontStyle: 'bold', textColor: brandColor, cellWidth: 30 },
                    1: { cellWidth: 60 },
                    2: { fontStyle: 'bold', textColor: brandColor, cellWidth: 30 },
                    3: { cellWidth: 60 }
                }
            });

            yPos = doc.lastAutoTable.finalY + 15;

            // 3. CLINICAL NOTES (Rich Text Simulation)
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.setTextColor(brandColor[0], brandColor[1], brandColor[2]);
            doc.text('CLINICAL SUMMARY', 20, yPos);
            yPos += 8;

            doc.setFontSize(10);
            doc.setTextColor(60, 60, 60);
            doc.setFont(undefined, 'normal');
            const summary = followUpNotes || 'No specific clinical observations recorded for this period.';
            const splitSummary = doc.splitTextToSize(summary, 170);
            doc.text(splitSummary, 20, yPos);
            yPos += (splitSummary.length * 5) + 15;

            // 4. TIMELINE (Using AutoTable for professional structure)
            if (journeyEvents && journeyEvents.length > 0) {
                doc.setFontSize(14);
                doc.setFont(undefined, 'bold');
                doc.setTextColor(brandColor[0], brandColor[1], brandColor[2]);
                doc.text('CARE TIMELINE & EVENTS', 20, yPos);

                const tableData = journeyEvents.map(ev => [
                    ev.segment,
                    `${ev.date}\n${ev.time || ''}`,
                    ev.description,
                    ev.status?.toUpperCase()
                ]);

                autoTable(doc, {
                    startY: yPos + 5,
                    head: [['#', 'Date / Time', 'Description of Event', 'Status']],
                    body: tableData,
                    headStyles: {
                        fillColor: brandColor,
                        textColor: [255, 255, 255],
                        halign: 'center'
                    },
                    alternateRowStyles: { fillColor: [245, 245, 250] },
                    styles: { fontSize: 9, cellPadding: 4 },
                    columnStyles: {
                        0: { halign: 'center', cellWidth: 10 },
                        1: { cellWidth: 30 },
                        3: { halign: 'center', cellWidth: 30, fontStyle: 'bold' }
                    }
                });
            }

            // 5. FOOTER
            const pageCount = doc.internal.getNumberOfPages();
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setTextColor(150, 150, 150);
                doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, 285, { align: 'center' });
                doc.text('Real-Time Emergency System - Clinical Documentation', 20, 285);
            }

            doc.save(`Clinical_Journey_${selectedPatient.name.replace(/\s+/g, '_')}.pdf`);
            alert(systemLanguage === 'ja' ? 'PDFをエクスポートしました' : '✓ PDF Exported in Professional Format');

        } catch (error) {
            console.error('PDF error:', error);
            alert('Failed to generate high-res PDF: ' + error.message);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white p-6 relative">
            {/* Ambient Background Glow - Fixed to screen */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-purple-600/20 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-blue-600/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>
            {/* Header */}
            <div className="flex items-center justify-between mb-8 relative z-10">
                <div className="flex items-center space-x-4">
                    <button
                        onClick={onBack}
                        className="group p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 hover:border-white/20 transition-all"
                    >
                        <ArrowLeft className="h-6 w-6" />
                    </button>
                    <div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                            {t.title}
                        </h1>
                        <p className="text-purple-300 text-sm mt-1">{t.subtitle}</p>
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    <div className="bg-orange-500/20 border border-orange-500/40 rounded-xl px-4 py-2 flex items-center space-x-2">
                        <AlertCircle className="h-5 w-5 text-orange-400" />
                        <span className="text-orange-200 text-sm font-semibold">{t.notEmergency}</span>
                    </div>

                    {/* Action Buttons - Professional Styling */}
                    <button
                        onClick={() => {
                            if (isRecording) {
                                stopRecordingCall();
                            } else {
                                startRecordingCall();
                            }
                        }}
                        className={`group relative px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-all duration-300 transform hover:scale-105 ${isRecording
                            ? 'bg-gradient-to-r from-red-600 to-red-500 animate-pulse text-white shadow-xl shadow-red-500/50 ring-2 ring-red-400/50'
                            : 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white shadow-lg shadow-red-600/30 hover:shadow-xl hover:shadow-red-500/40'
                            }`}
                    >
                        <Radio className={`h-4 w-4 ${isRecording ? 'animate-ping' : 'group-hover:rotate-12 transition-transform'}`} />
                        <span className="text-sm font-bold tracking-wide">
                            {isRecording ? t.stopRecording || 'Stop Call' : t.liveCall}
                        </span>
                        {isRecording && <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-ping"></div>}
                    </button>

                    <button
                        onClick={() => setShowTextInput(true)}
                        className="group px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 rounded-xl flex items-center space-x-2 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-emerald-600/30 hover:shadow-xl hover:shadow-emerald-500/40"
                    >
                        <MessageSquare className="h-4 w-4 group-hover:rotate-12 transition-transform" />
                        <span className="text-sm font-bold tracking-wide">{t.textInput}</span>
                    </button>

                    <label className="group px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 rounded-xl flex items-center space-x-2 cursor-pointer transition-all duration-300 transform hover:scale-105 shadow-lg shadow-blue-600/30 hover:shadow-xl hover:shadow-blue-500/40">
                        <Upload className="h-4 w-4 group-hover:-translate-y-1 transition-transform" />
                        <span className="text-sm font-bold tracking-wide">{t.audioUpload}</span>
                        <input type="file" className="hidden" accept=".wav,.mp3,.m4a" onChange={handleAudioUpload} disabled={uploading} />
                    </label>

                    <button
                        onClick={exportToPDF}
                        disabled={!selectedPatient}
                        className="group px-5 py-2.5 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 rounded-xl flex items-center space-x-2 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-purple-600/30 hover:shadow-xl hover:shadow-purple-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
                    >
                        <FileText className="h-4 w-4 group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-bold tracking-wide">{t.exportPDF}</span>
                    </button>
                </div>
            </div>

            {/* Statistics Overview Cards */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                {/* Total Patients */}
                <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-xl border border-blue-500/30 rounded-xl p-4 hover:scale-105 transition-transform">
                    <div className="flex items-center justify-between mb-2">
                        <User className="h-8 w-8 text-blue-400" />
                        <div className="text-3xl font-bold text-white">{patients.length}</div>
                    </div>
                    <div className="text-sm text-blue-200 font-semibold">{t.totalPatients}</div>
                </div>

                {/* Active Follow-Ups */}
                <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-xl border border-purple-500/30 rounded-xl p-4 hover:scale-105 transition-transform">
                    <div className="flex items-center justify-between mb-2">
                        <Activity className="h-8 w-8 text-purple-400" />
                        <div className="text-3xl font-bold text-white">
                            {patients.filter(p => {
                                const events = typeof p.journey_events === 'string' ? JSON.parse(p.journey_events || '[]') : (p.journey_events || []);
                                return events.some(e => e.status === 'pending');
                            }).length}
                        </div>
                    </div>
                    <div className="text-sm text-purple-200 font-semibold">{t.activeFollowUps}</div>
                </div>

                {/* Completed Events */}
                <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-xl border border-green-500/30 rounded-xl p-4 hover:scale-105 transition-transform">
                    <div className="flex items-center justify-between mb-2">
                        <CheckCircle className="h-8 w-8 text-green-400" />
                        <div className="text-3xl font-bold text-white">
                            {patients.reduce((sum, p) => {
                                const events = typeof p.journey_events === 'string' ? JSON.parse(p.journey_events || '[]') : (p.journey_events || []);
                                return sum + events.filter(e => e.status === 'completed').length;
                            }, 0)}
                        </div>
                    </div>
                    <div className="text-sm text-green-200 font-semibold">{t.completedEvents}</div>
                </div>

                {/* Pending Events */}
                <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/20 backdrop-blur-xl border border-orange-500/30 rounded-xl p-4 hover:scale-105 transition-transform">
                    <div className="flex items-center justify-between mb-2">
                        <Clock className="h-8 w-8 text-orange-400" />
                        <div className="text-3xl font-bold text-white">
                            {patients.reduce((sum, p) => {
                                const events = typeof p.journey_events === 'string' ? JSON.parse(p.journey_events || '[]') : (p.journey_events || []);
                                return sum + events.filter(e => e.status === 'pending').length;
                            }, 0)}
                        </div>
                    </div>
                    <div className="text-sm text-orange-200 font-semibold">{t.pendingEvents}</div>
                </div>
            </div>

            <div className="grid grid-cols-12 gap-6 min-h-[calc(100vh-140px)] relative z-10">
                {/* Left Sidebar - Patient Selection - Made full height */}
                <div className="col-span-3 space-y-4 h-full flex flex-col">
                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 h-full flex flex-col">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold flex items-center">
                                <User className="h-5 w-5 mr-2 text-purple-400" />
                                {t.selectPatient}
                            </h2>
                            <div className="flex space-x-2">
                                <button
                                    onClick={syncAllCalls}
                                    className="group px-3 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg text-white text-[10px] font-black uppercase tracking-widest shadow-lg shadow-purple-900/40 transition-all hover:scale-105 active:scale-95"
                                    title="Sync Data from Main Dashboard"
                                >
                                    <RefreshCw className="h-3.5 w-3.5 inline mr-1.5 group-hover:rotate-180 transition-transform duration-500" />
                                    Sync
                                </button>
                                <button
                                    onClick={async () => {
                                        if (window.confirm(t.confirmClear)) {
                                            try {
                                                const response = await fetch(`${API_URL}/api/patients/clear-all`, { method: 'DELETE' });
                                                if (response.ok) {
                                                    await fetchPatients();
                                                    setSelectedPatient(null);
                                                    setJourneyEvents([]);
                                                    alert(systemLanguage === 'ja' ? '全データを削除しました' : '✓ All data cleared');
                                                }
                                            } catch (e) {
                                                console.error('Clear error:', e);
                                            }
                                        }
                                    }}
                                    className="group px-3 py-1.5 bg-red-600 hover:bg-red-500 rounded-lg text-white text-[10px] font-black uppercase tracking-widest shadow-lg shadow-red-900/40 transition-all hover:scale-105 active:scale-95"
                                >
                                    <Trash2 className="h-3.5 w-3.5 inline mr-1.5" />
                                    Clear
                                </button>
                            </div>
                        </div>

                        {/* Search */}
                        <div className="relative mb-4">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4" />
                            <input
                                type="text"
                                placeholder="Search (Name, ID, DOB, Phone...)"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-purple-500 transition-colors"
                            />
                        </div>

                        <div className="space-y-2 flex-1 overflow-y-auto pr-1">
                            {filteredPatients.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    <p className="mb-2">No patients found</p>
                                    <p className="text-xs">Use "Text Input" above to add a patient</p>
                                </div>
                            ) : (
                                filteredPatients.map((patient) => {
                                    const events = typeof patient.journey_events === 'string'
                                        ? JSON.parse(patient.journey_events || '[]')
                                        : (patient.journey_events || []);
                                    const completedCount = events.filter(e => e.status === 'completed').length;
                                    const pendingCount = events.filter(e => e.status === 'pending').length;

                                    return (
                                        <div
                                            key={patient.patient_id}
                                            onClick={() => selectPatient(patient)}
                                            className={`p-4 rounded-xl cursor-pointer transition-all group ${selectedPatient?.patient_id === patient.patient_id
                                                ? 'bg-purple-500/30 border-2 border-purple-400 shadow-lg shadow-purple-500/20'
                                                : 'bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-400/50'
                                                }`}
                                        >
                                            <div className="flex items-start space-x-3">
                                                {/* Avatar */}
                                                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${selectedPatient?.patient_id === patient.patient_id
                                                    ? 'bg-gradient-to-br from-purple-400 to-purple-600'
                                                    : 'bg-gradient-to-br from-gray-600 to-gray-700 group-hover:from-purple-500 group-hover:to-purple-600'
                                                    }`}>
                                                    {patient.name ? patient.name.charAt(0).toUpperCase() : '?'}
                                                </div>

                                                {/* Patient Info */}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <span className="font-bold text-sm truncate">{patient.name || 'Unknown'}</span>
                                                        {selectedPatient?.patient_id === patient.patient_id && (
                                                            <CheckCircle className="h-4 w-4 text-purple-400 flex-shrink-0" />
                                                        )}
                                                    </div>

                                                    <div className="text-xs text-purple-300 font-mono mb-2">
                                                        ID: {patient.patient_id?.substring(0, 10)}
                                                    </div>

                                                    <div className="text-xs text-gray-300 mb-2 truncate">
                                                        {patient.primary_condition || 'No condition specified'}
                                                    </div>

                                                    {/* Event Counts */}
                                                    {events.length > 0 && (
                                                        <div className="flex items-center space-x-2 mt-2">
                                                            {completedCount > 0 && (
                                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-green-500/20 text-green-300">
                                                                    ✓ {completedCount}
                                                                </span>
                                                            )}
                                                            {pendingCount > 0 && (
                                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500/20 text-orange-300">
                                                                    ⏱ {pendingCount}
                                                                </span>
                                                            )}
                                                        </div>
                                                    )}

                                                    {patient.street && (
                                                        <div className="text-xs text-gray-500 mt-2 truncate">
                                                            📍 {patient.street}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="col-span-9 space-y-6">
                    {selectedPatient ? (
                        <>
                            {/* CSS-Based Timeline Visualization - Fast & Simple */}
                            <div className="mb-6">
                                <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                                    <div className="flex items-center justify-between mb-6">
                                        <h3 className="text-lg font-bold flex items-center">
                                            <ImageIcon className="h-5 w-5 mr-2 text-blue-400" />
                                            {t.eventTimetable}
                                        </h3>
                                        <div className="text-sm text-purple-300">
                                            {selectedPatient.name} • {selectedPatient.primary_condition || 'N/A'}
                                        </div>
                                    </div>

                                    {/* Horizontal Timeline - Compact & Responsive */}
                                    <div className="relative py-4 px-2">
                                        {journeyEvents.length > 0 ? (
                                            <div className="flex flex-wrap gap-4 justify-start relative">
                                                {/* Event Nodes */}
                                                {journeyEvents.map((event, index) => (
                                                    <div key={event.id || index} className="flex flex-col items-center relative" style={{ minWidth: '90px', maxWidth: '110px' }}>
                                                        {/* Connecting Line to Next */}
                                                        {index < journeyEvents.length - 1 && (
                                                            <div className="absolute top-4 left-[calc(50%+18px)] w-[calc(90px-36px)] h-0.5 bg-gradient-to-r from-purple-500 to-pink-500" style={{ zIndex: 0 }}></div>
                                                        )}

                                                        {/* Event Circle - Smaller */}
                                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border-2 border-slate-950 transition-all hover:scale-110 relative ${event.status === 'completed'
                                                            ? 'bg-gradient-to-br from-green-400 to-green-600 shadow-md shadow-green-500/50'
                                                            : 'bg-gradient-to-br from-purple-400 to-purple-600 shadow-md shadow-purple-500/50'
                                                            }`} style={{ zIndex: 10 }}>
                                                            {event.segment}
                                                        </div>

                                                        {/* Event Info - Compact */}
                                                        <div className="mt-2 text-center w-full">
                                                            <div className="text-[10px] font-bold text-purple-300 mb-1">
                                                                {event.date}
                                                            </div>
                                                            <div className="text-[10px] text-gray-400 leading-tight break-words px-1">
                                                                {event.description.length > 25
                                                                    ? event.description.substring(0, 25) + '...'
                                                                    : event.description}
                                                            </div>
                                                            <div className={`mt-1 inline-block px-1.5 py-0.5 rounded-full text-[9px] font-bold ${event.status === 'completed'
                                                                ? 'bg-green-500/20 text-green-300'
                                                                : 'bg-purple-500/20 text-purple-300'
                                                                }`}>
                                                                {event.status}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-center py-12 text-gray-500">
                                                <p className="text-lg italic">
                                                    {systemLanguage === 'ja' ? 'イベント記録なし' : 'No journey events recorded yet'}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>


                            {/* Patient Info Card */}
                            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6">
                                <h3 className="text-xl font-bold mb-4 flex items-center">
                                    <Activity className="h-6 w-6 mr-2 text-purple-400" />
                                    {t.patientInfo}
                                </h3>
                                <div className="grid grid-cols-4 gap-6">
                                    <div>
                                        <p className="text-gray-400 text-sm mb-1">{t.patientName}</p>
                                        <p className="font-bold text-lg">{selectedPatient.name}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400 text-sm mb-1">{t.disease}</p>
                                        <p className="font-bold text-lg">{selectedPatient.primary_condition || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400 text-sm mb-1">{t.lastContact}</p>
                                        <p className="font-bold text-lg">
                                            {selectedPatient.last_contact
                                                ? new Date(selectedPatient.last_contact).toLocaleDateString()
                                                : 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400 text-sm mb-1">{t.callId}</p>
                                        <p className="font-mono text-sm text-purple-300">{selectedPatient.patient_id?.substring(0, 12)}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Journey Timeline */}
                            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-xl font-bold flex items-center">
                                        <Calendar className="h-6 w-6 mr-2 text-blue-400" />
                                        {t.eventTimetable}
                                    </h3>
                                    <button
                                        onClick={addOrUpdateJourneyEvent}
                                        disabled={!newEvent.date || !newEvent.description}
                                        className={`group flex items-center space-x-2 px-5 py-2.5 rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none ${editingIndex !== null
                                            ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 shadow-lg shadow-green-600/30 hover:shadow-xl hover:shadow-green-500/40'
                                            : 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 shadow-lg shadow-purple-600/30 hover:shadow-xl hover:shadow-purple-500/40'}`}
                                    >
                                        {editingIndex !== null ? <Save className="h-4 w-4 group-hover:scale-110 transition-transform" /> : <Plus className="h-4 w-4 group-hover:rotate-90 transition-transform" />}
                                        <span className="font-bold">{editingIndex !== null ? t.updateEvent : t.addEvent}</span>
                                    </button>
                                </div>

                                {/* Add Event Form - Always visible at top */}
                                <div className={`grid grid-cols-2 gap-4 mb-6 p-4 rounded-xl border border-white/10 ${editingIndex !== null ? 'bg-green-500/10 border-green-500/30' : 'bg-white/5'}`}>
                                    <input
                                        type="date"
                                        value={newEvent.date}
                                        onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                                        className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500"
                                    />
                                    <input
                                        type="text"
                                        placeholder={t.description}
                                        value={newEvent.description}
                                        onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                                        className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500"
                                    />
                                    {editingIndex !== null && (
                                        <button
                                            onClick={() => {
                                                setEditingIndex(null);
                                                setNewEvent({ date: '', description: '' });
                                            }}
                                            className="col-span-2 px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg text-sm font-semibold transition-colors"
                                        >
                                            {t.cancelEdit}
                                        </button>
                                    )}
                                </div>

                                {/* Timeline */}
                                <div className="relative">
                                    <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 to-pink-500"></div>

                                    <div className="space-y-6">
                                        {journeyEvents.map((event, index) => (
                                            <div key={event.id || index} className="relative flex items-start space-x-6">
                                                <div className={`flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center font-bold text-lg z-10 ${event.status === 'completed'
                                                    ? 'bg-gradient-to-br from-green-400 to-green-600'
                                                    : 'bg-gradient-to-br from-purple-400 to-purple-600'
                                                    }`}>
                                                    {event.segment}
                                                </div>

                                                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <div className="flex items-center space-x-3">
                                                            <Clock className="h-4 w-4 text-purple-400" />
                                                            <span className="text-sm text-gray-400">{event.date}</span>
                                                            <span className="text-sm text-purple-300">{event.time}</span>
                                                        </div>
                                                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${event.status === 'completed'
                                                            ? 'bg-green-500/20 text-green-300'
                                                            : 'bg-purple-500/20 text-purple-300'
                                                            }`}>
                                                            {event.status}
                                                        </span>
                                                        <div className="flex items-center space-x-2">
                                                            <button
                                                                onClick={() => startEditEvent(index)}
                                                                className="group text-blue-400 hover:text-blue-300 p-2 hover:bg-blue-500/20 rounded-lg transition-all duration-200 hover:scale-110"
                                                                title={t.editEvent}
                                                            >
                                                                <Edit3 className="h-4 w-4 group-hover:rotate-6 transition-transform" />
                                                            </button>
                                                            <button
                                                                onClick={async () => {
                                                                    if (window.confirm(systemLanguage === 'ja' ? 'このイベントを削除しますか？' : 'Delete this event?')) {
                                                                        const updatedEvents = journeyEvents.filter((_, i) => i !== index);
                                                                        // Re-index segments
                                                                        const reindexedEvents = updatedEvents.map((ev, i) => ({ ...ev, segment: i + 1 }));

                                                                        try {
                                                                            const response = await fetch(`${API_URL}/api/patients/${selectedPatient.patient_id}`, {
                                                                                method: 'PUT',
                                                                                headers: { 'Content-Type': 'application/json' },
                                                                                body: JSON.stringify({ journey_events: JSON.stringify(reindexedEvents) })
                                                                            });

                                                                            if (response.ok) {
                                                                                setJourneyEvents(reindexedEvents);
                                                                                setSelectedPatient({ ...selectedPatient, journey_events: reindexedEvents });
                                                                                await fetchPatients();
                                                                            } else {
                                                                                alert(systemLanguage === 'ja' ? '削除に失敗しました' : 'Failed to delete event');
                                                                            }
                                                                        } catch (e) {
                                                                            console.error(e);
                                                                            alert(systemLanguage === 'ja' ? '削除エラー' : 'Delete error');
                                                                        }
                                                                    }
                                                                }}
                                                                className="group text-red-400 hover:text-red-300 p-2 hover:bg-red-500/20 rounded-lg transition-all duration-200 hover:scale-110"
                                                                title={t.deleteEvent}
                                                            >
                                                                <Trash2 className="h-4 w-4 group-hover:scale-110 transition-transform" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <p className="text-white font-medium">{event.description}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Live Transcription & Notes */}
                            <div className="grid grid-cols-2 gap-6">
                                <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-bold flex items-center">
                                            <Mic className="h-5 w-5 mr-2 text-red-400" />
                                            {t.liveTranscription}
                                        </h3>
                                    </div>
                                    <div
                                        ref={transcriptRef}
                                        className={`bg-black/40 border rounded-xl p-4 h-[300px] overflow-y-auto text-sm font-mono transition-colors ${isRecording ? 'border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]' : 'border-white/10'
                                            }`}
                                    >
                                        {isRecording && (
                                            <div className="flex items-center space-x-2 text-red-400 mb-2 animate-pulse">
                                                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                                <span className="text-xs uppercase font-bold tracking-wider">Recording Live Audio...</span>
                                            </div>
                                        )}
                                        {liveTranscript || (
                                            <p className="text-gray-500 italic">
                                                {isRecording ? 'Listening for speech...' : 'Click "Live Call" to start recording...'}
                                            </p>
                                        )}
                                    </div>
                                </div>

                                <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-bold flex items-center">
                                            <Edit3 className="h-5 w-5 mr-2 text-green-400" />
                                            {t.followUpNotes}
                                        </h3>
                                        <button
                                            onClick={saveFollowUpNotes}
                                            className="group flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 px-5 py-2.5 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg shadow-green-600/30 hover:shadow-xl hover:shadow-green-500/40"
                                        >
                                            <Save className="h-4 w-4 group-hover:scale-110 transition-transform" />
                                            <span className="font-bold">{t.saveNotes}</span>
                                        </button>
                                    </div>
                                    <textarea
                                        value={followUpNotes}
                                        onChange={(e) => setFollowUpNotes(e.target.value)}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl p-4 h-[300px] resize-none text-sm focus:outline-none focus:border-green-500 transition-colors"
                                        placeholder="Enter follow-up notes, observations, and next steps..."
                                    />
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12">
                            <div className="text-center max-w-2xl mx-auto">
                                <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <User className="h-12 w-12 text-purple-400" />
                                </div>
                                <h3 className="text-2xl font-bold mb-3">{t.noPatientSelected}</h3>
                                <p className="text-gray-400 mb-8">
                                    {systemLanguage === 'ja'
                                        ? '左側のリストから患者を選択するか、新しい患者を追加してください'
                                        : 'Select a patient from the list on the left or add a new patient to get started'}
                                </p>

                                {/* Quick Actions */}
                                <div className="grid grid-cols-3 gap-4">
                                    <button
                                        onClick={() => setShowTextInput(true)}
                                        className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30 rounded-xl p-6 hover:scale-105 transition-transform group"
                                    >
                                        <MessageSquare className="h-8 w-8 text-emerald-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                                        <div className="font-bold text-sm text-emerald-200">{t.textInput}</div>
                                        <div className="text-xs text-gray-400 mt-1">
                                            {systemLanguage === 'ja' ? 'テキストで追加' : 'Add via text'}
                                        </div>
                                    </button>

                                    <label className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6 hover:scale-105 transition-transform cursor-pointer group">
                                        <Upload className="h-8 w-8 text-blue-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                                        <div className="font-bold text-sm text-blue-200">{t.audioUpload}</div>
                                        <div className="text-xs text-gray-400 mt-1">
                                            {systemLanguage === 'ja' ? '音声で追加' : 'Add via audio'}
                                        </div>
                                        <input type="file" className="hidden" accept=".wav,.mp3,.m4a" onChange={handleAudioUpload} disabled={uploading} />
                                    </label>

                                    <button
                                        onClick={syncAllCalls}
                                        className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6 hover:scale-105 transition-transform group"
                                    >
                                        <Activity className="h-8 w-8 text-purple-400 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                                        <div className="font-bold text-sm text-purple-200">{t.syncAll}</div>
                                        <div className="text-xs text-gray-400 mt-1">
                                            {systemLanguage === 'ja' ? '緊急通話から同期' : 'Sync from calls'}
                                        </div>
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Text Input Modal */}
            {
                showTextInput && (
                    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-8">
                        <div className="bg-slate-900 border border-white/20 rounded-2xl p-8 max-w-2xl w-full">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-2xl font-bold">{t.textInput}</h2>
                                <button onClick={() => setShowTextInput(false)} className="p-2 hover:bg-white/10 rounded-lg">
                                    <X className="h-6 w-6" />
                                </button>
                            </div>
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1 ml-1">{t.patientName}</label>
                                    <input
                                        type="text"
                                        placeholder={t.patientName}
                                        value={patientNameInput}
                                        onChange={(e) => setPatientNameInput(e.target.value)}
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1 ml-1">Attending MD</label>
                                    <input
                                        type="text"
                                        placeholder="Doctor name..."
                                        value={doctorInput}
                                        onChange={(e) => setDoctorInput(e.target.value)}
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500"
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1 ml-1">{t.disease}</label>
                                    <select
                                        value={conditionInput}
                                        onChange={(e) => setConditionInput(e.target.value)}
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-purple-500"
                                    >
                                        <option value="">Select Condition...</option>
                                        <option value="Stroke">{t.conditionStroke || 'Stroke'}</option>
                                        <option value="Heart Attack">{t.conditionHeartAttack || 'Heart Attack'}</option>
                                        <option value="COVID-19">{t.conditionCOVID || 'COVID-19'}</option>
                                        <option value="Severe Fall">{t.conditionTrauma || 'Severe Fall'}</option>
                                        <option value="Respiratory Distress">{t.conditionRespiratory || 'Respiratory Distress'}</option>
                                        <option value="Cardiac Arrest">{t.conditionCardiac || 'Cardiac Arrest'}</option>
                                        <option value="Anaphylaxis">{t.conditionAnaphylaxis || 'Anaphylaxis'}</option>
                                    </select>
                                </div>
                            </div>
                            <label className="block text-xs font-bold text-gray-400 uppercase mb-1 ml-1">Observations / Transcription</label>
                            <textarea
                                value={textInputVal}
                                onChange={(e) => setTextInputVal(e.target.value)}
                                className="w-full bg-black/40 border border-white/10 rounded-xl p-4 h-[200px] resize-none text-sm focus:outline-none focus:border-purple-500"
                                placeholder={t.typeNotes}
                            />
                            <div className="flex justify-end space-x-4 mt-6">
                                <button
                                    onClick={() => {
                                        setShowTextInput(false);
                                        setPatientNameInput('');
                                        setDoctorInput('');
                                        setConditionInput('');
                                        setTextInputVal('');
                                    }}
                                    className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                                >
                                    {t.cancel}
                                </button>
                                <button
                                    onClick={handleTextSubmit}
                                    disabled={isProcessing || !textInputVal.trim()}
                                    className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                                >
                                    {isProcessing ? (
                                        <>
                                            <Loader className="h-4 w-4 animate-spin" />
                                            <span>{t.processing}</span>
                                        </>
                                    ) : (
                                        <>
                                            <Activity className="h-4 w-4" />
                                            <span>{t.processData}</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
}
