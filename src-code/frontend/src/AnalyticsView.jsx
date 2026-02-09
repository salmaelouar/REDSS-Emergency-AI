import React, { useState, useMemo } from 'react';
import {
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
    Activity, AlertTriangle, Phone, Clock, TrendingUp, TrendingDown,
    ArrowLeft, Eye, X, Radio, Calendar
} from 'lucide-react';

const COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#22c55e'
};

export default function AnalyticsView({ stats = {}, calls = [], onBack, systemLanguage = 'en' }) {
    const [selectedImage, setSelectedImage] = useState(null);

    const TRANSLATIONS = {
        en: {
            title: "Emergency Operations",
            liveMonitoring: "Live Monitoring",
            systemTime: "System Time",
            totalCalls: "Total Calls",
            critical: "Critical",
            avgResponse: "Avg Response",
            activeUnits: "Active Units",
            liveCallAnalysis: "Live Call Analysis",
            active: "Active",
            callVolume: "Call Volume",
            urgencyLevels: "Urgency Levels",
            callLog: "Call Log",
            id: "ID",
            dateTime: "Date & Time",
            summary: "Summary",
            status: "Status",
            viewJourneyImage: "View Journey Image",
            waitingForCalls: "Waiting for calls...",
            high: "High",
            medium: "Medium",
            low: "Low"
        },
        ja: {
            title: "緊急オペレーション",
            liveMonitoring: "ライブ監視中",
            systemTime: "システム時刻",
            totalCalls: "総通報数",
            critical: "最優先(重症)",
            avgResponse: "平均対応時間",
            activeUnits: "活動部隊",
            liveCallAnalysis: "リアルタイム通話解析",
            active: "活動中",
            callVolume: "通報件数推移",
            urgencyLevels: "緊急度分布",
            callLog: "通報履歴",
            id: "ID",
            dateTime: "日時",
            summary: "概要",
            status: "状態",
            viewJourneyImage: "旅程画像を表示",
            waitingForCalls: "通報待機中...",
            high: "高緊急度",
            medium: "中緊急度",
            low: "低緊急度"
        }
    };

    const t = TRANSLATIONS[systemLanguage] || TRANSLATIONS.en;

    const translateUrgency = React.useCallback((level) => {
        if (!level) return level;
        const key = level.toLowerCase();
        return t[key] || level;
    }, [t]);

    // Helper to resolve specific filenames for COVID journeys
    const resolveImagePath = (num) => {
        const base = "/dashboard-assets/English_en_Interview_Interview_";
        if (num === 1) return base + "1_Covid_General.png";
        if (num === 2) return base + "2_Covid_Recovery.png";
        if (num === 3) return base + "3_Covid_Hospital.png";
        if (num === 4) return base + "4_Covid_Diagnosis.png";
        return base + num + ".png";
    };

    const getSmartImage = (c) => {
        if (!c) return null;
        const text = (c.soap_subjective || c.transcript || "").toLowerCase();
        const callId = c.call_id || "";

        // 1. AI Generated Journey Priority (Specific to User Request)
        if (c.disease === "COVID-19" || text.includes("covid") || text.includes("virus") || text.includes("infection")) {
            return "/dashboard-assets/AI_Generated_COVID_Journey.png";
        }
        if (c.disease === "Heart Attack" || text.includes("heart attack") || text.includes("myocardial") || (text.includes("chest") && text.includes("crushing"))) {
            return "/dashboard-assets/AJ_Heart_Attack.png";
        }
        if (c.disease === "Stroke" || text.includes("stroke") || text.includes("facial") || text.includes("slurred")) {
            return "/dashboard-assets/AJ_Stroke.png";
        }
        if (c.disease === "Severe Fall" || text.includes("fall") || text.includes("trauma") || text.includes("broken") || text.includes("fracture")) {
            return "/dashboard-assets/AJ_Fall_Trauma.png";
        }
        if (c.disease === "Respiratory Distress" || text.includes("breathe") || text.includes("asthma") || text.includes("oxygen") || text.includes("choking")) {
            return "/dashboard-assets/AJ_Respiratory.png";
        }
        if (c.disease === "Anaphylaxis" || text.includes("allergy") || text.includes("allergic") || text.includes("sting") || text.includes("hives")) {
            return "/dashboard-assets/AJ_Allergic.png";
        }

        // 2. Direct Interview ID Match
        const match = callId.match(/Interview\s*(\d+)/i);
        if (match && match[1]) {
            return resolveImagePath(parseInt(match[1]));
        }

        // 3. Fallbacks
        if (text.includes("heart") || text.includes("chest")) return resolveImagePath(5);
        if (text.includes("confused") || text.includes("memory") || text.includes("dementia")) return resolveImagePath(1);
        if (text.includes("child") || text.includes("bead") || text.includes("pediatric")) return resolveImagePath(12);
        if (text.includes("seizure") || text.includes("shaking")) return resolveImagePath(3);
        if (text.includes("unconscious") || text.includes("fainted")) return resolveImagePath(8);
        if (text.includes("pregnant") || text.includes("baby")) return resolveImagePath(10);

        const hash = callId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return resolveImagePath((hash % 14) + 1);
    };

    const urgencyData = useMemo(() => {
        if (!stats?.urgency_distribution) return [];
        return Object.entries(stats.urgency_distribution).map(([key, value]) => ({
            name: translateUrgency(key),
            value: value,
            fill: COLORS[key]
        }));
    }, [stats, translateUrgency]);

    const callsOverTimeData = useMemo(() => {
        if (!calls?.length) return [];
        const grouped = {};
        calls.forEach(call => {
            if (!call.created_at) return;
            const hour = new Date(call.created_at).getHours();
            const timeLabel = `${hour}:00`;
            if (!grouped[timeLabel]) {
                grouped[timeLabel] = { time: timeLabel, count: 0, critical: 0 };
            }
            grouped[timeLabel].count += 1;
            if ((call.urgency_level || call.urgency?.level) === 'CRITICAL') {
                grouped[timeLabel].critical += 1;
            }
        });
        return Object.values(grouped).sort((a, b) => parseInt(a.time) - parseInt(b.time));
    }, [calls]);

    return (
        <div className="min-h-screen bg-black text-white p-6 relative overflow-hidden">
            {/* Animated Background */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={onBack}
                            className="group p-3 bg-zinc-900 hover:bg-zinc-800 rounded-xl border border-zinc-800 hover:border-zinc-600 transition-all"
                        >
                            <ArrowLeft className="h-6 w-6 text-zinc-400 group-hover:text-white" />
                        </button>
                        <div className="flex items-center space-x-4">
                            <div className="relative">
                                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-75"></div>
                                <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-xl">
                                    <Activity className="h-8 w-8 text-white" />
                                </div>
                            </div>
                            <div>
                                <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
                                    {t.title}
                                </h1>
                                <div className="flex items-center space-x-2 mt-1">
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                    <span className="text-sm text-zinc-400">{t.liveMonitoring}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-zinc-900/90 backdrop-blur-xl border border-zinc-800 rounded-xl px-6 py-3">
                        <span className="text-zinc-500 text-sm mr-2">{t.systemTime}</span>
                        <span className="text-blue-400 font-mono font-semibold">{new Date().toLocaleTimeString()}</span>
                    </div>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-4 gap-2 lg:gap-6 mb-8">
                    <MetricCard
                        title={t.totalCalls}
                        value={stats.total_calls || 0}
                        icon={<Phone className="h-7 w-7" />}
                        trend="+12%"
                        trendUp={true}
                        color="blue"
                    />
                    <MetricCard
                        title={t.critical}
                        value={stats.urgency_distribution?.CRITICAL || 0}
                        icon={<AlertTriangle className="h-7 w-7" />}
                        trend="+5%"
                        trendUp={true}
                        color="red"
                    />
                    <MetricCard
                        title={t.avgResponse}
                        value={`${Math.round(stats.average_duration || 0)}s`}
                        icon={<Clock className="h-7 w-7" />}
                        trend="-8%"
                        trendUp={false}
                        color="green"
                    />
                    <MetricCard
                        title={t.activeUnits}
                        value={calls.length}
                        icon={<Radio className="h-7 w-7" />}
                        trend="Live"
                        color="purple"
                    />
                </div>

                {/* Recent Calls Gallery */}
                <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6 mb-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-3">
                            <div className="bg-blue-500/20 p-2 rounded-lg">
                                <Activity className="h-6 w-6 text-blue-400" />
                            </div>
                            <h2 className="text-2xl font-bold">{t.liveCallAnalysis}</h2>
                        </div>
                        <span className="text-xs text-zinc-500 bg-zinc-800 px-3 py-1.5 rounded-full border border-zinc-700">
                            {calls.length} {t.active}
                        </span>
                    </div>

                    <div className="flex overflow-x-auto gap-4 pb-4 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                        {calls.length > 0 ? calls.slice(0, 15).map((call, index) => {
                            const imagePath = getSmartImage(call, index);
                            const urgency = call.urgency_level || call.urgency?.level || 'UNKNOWN';

                            return (
                                <div key={call.call_id || index} className="group min-w-[340px] bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-xl overflow-hidden border border-zinc-700 hover:border-zinc-600 transition-all hover:scale-105">
                                    <div className="relative h-48 bg-black">
                                        <img
                                            src={imagePath}
                                            alt="Analysis"
                                            className="w-full h-full object-contain"
                                        />
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent"></div>

                                        <div className="absolute top-3 right-3">
                                            <span className="px-3 py-1 rounded-lg text-xs font-bold uppercase text-white shadow-lg"
                                                style={{ backgroundColor: COLORS[urgency] || COLORS.LOW }}>
                                                {translateUrgency(urgency)}
                                            </span>
                                        </div>

                                        <button
                                            onClick={() => setSelectedImage(imagePath)}
                                            className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <div className="bg-white/10 backdrop-blur-md p-4 rounded-full">
                                                <Eye className="h-6 w-6 text-white" />
                                            </div>
                                        </button>
                                    </div>

                                    <div className="p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-blue-400 font-mono text-xs font-semibold">
                                                {call.call_id || 'N/A'}
                                            </span>
                                            <span className="text-zinc-500 text-xs">
                                                {call.created_at ? new Date(call.created_at).toLocaleTimeString() : 'N/A'}
                                            </span>
                                        </div>
                                        <p className="text-zinc-300 text-sm line-clamp-2">
                                            {call.soap_subjective || call.transcript || "Processing..."}
                                        </p>
                                        <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-700">
                                            <div className="flex items-center text-zinc-500 text-xs">
                                                <Clock className="h-3.5 w-3.5 mr-1.5" />
                                                {call.audio_duration ? `${call.audio_duration.toFixed(0)}s` : 'N/A'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        }) : (
                            <div className="w-full flex flex-col items-center justify-center py-20 border-2 border-dashed border-zinc-800 rounded-xl">
                                <Activity className="h-16 w-16 text-zinc-700 mb-4 animate-pulse" />
                                <p className="text-xl text-zinc-400">{t.waitingForCalls}</p>
                            </div>
                        )
                        }
                    </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    {/* Call Volume */}
                    <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
                        <h3 className="text-xl font-bold mb-4 flex items-center">
                            <div className="bg-blue-500/20 p-2 rounded-lg mr-3">
                                <Activity className="h-5 w-5 text-blue-400" />
                            </div>
                            {t.callVolume}
                        </h3>
                        <div className="h-[180px] lg:h-[280px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={callsOverTimeData}>
                                    <defs>
                                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                    <XAxis dataKey="time" stroke="#71717a" />
                                    <YAxis stroke="#71717a" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                                    />
                                    <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="url(#colorCount)" strokeWidth={2} />
                                    <Area type="monotone" dataKey="critical" stroke="#ef4444" fill="none" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Urgency Distribution */}
                    <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
                        <h3 className="text-xl font-bold mb-4 flex items-center">
                            <div className="bg-orange-500/20 p-2 rounded-lg mr-3">
                                <AlertTriangle className="h-5 w-5 text-orange-400" />
                            </div>
                            {t.urgencyLevels}
                        </h3>
                        <div className="h-[180px] lg:h-[280px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={urgencyData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={3}
                                        dataKey="value"
                                    >
                                        {urgencyData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.fill} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                                    />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Call Log Table */}
                <div className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6">
                    <div className="flex items-center space-x-3 mb-6">
                        <div className="bg-purple-500/20 p-2 rounded-lg">
                            <Calendar className="h-6 w-6 text-purple-400" />
                        </div>
                        <h2 className="text-2xl font-bold">{t.callLog}</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-zinc-800/80 text-zinc-300 text-sm uppercase">
                                <tr>
                                    <th className="px-4 py-3 text-left rounded-tl-lg">{t.id}</th>
                                    <th className="px-4 py-3 text-left">{t.dateTime}</th>
                                    <th className="px-4 py-3 text-left">{t.summary}</th>
                                    <th className="px-4 py-3 text-left rounded-tr-lg">{t.status}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {calls.slice(0, 10).map((call, index) => {
                                    const urgency = call.urgency_level || call.urgency?.level || 'UNKNOWN';
                                    const imagePath = getSmartImage(call, index);
                                    return (
                                        <tr
                                            key={call.call_id || index}
                                            className="hover:bg-blue-900/20 transition-colors cursor-pointer group/row"
                                            onClick={() => setSelectedImage(imagePath)}
                                        >
                                            <td className="px-2 lg:px-4 py-2 lg:py-3 font-mono text-[10px] lg:text-xs text-blue-400 whitespace-nowrap align-top">
                                                {call.call_id?.substring(0, 4) || 'N/A'}
                                            </td>
                                            <td className="px-2 lg:px-4 py-2 lg:py-3 text-[10px] lg:text-sm text-zinc-400 whitespace-nowrap align-top">
                                                <div className="flex flex-col">
                                                    <span className="text-zinc-500 text-[10px]">{call.created_at ? new Date(call.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}</span>
                                                    <span>{call.created_at ? new Date(call.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}</span>
                                                </div>
                                            </td>
                                            <td className="px-2 lg:px-4 py-2 lg:py-3 text-[10px] lg:text-sm text-zinc-300 break-words whitespace-normal leading-tight max-w-[140px] lg:max-w-md align-top">
                                                <div className="flex flex-col">
                                                    <span>{call.soap_subjective || 'Processing...'}</span>
                                                    <span className="text-[10px] text-blue-500 opacity-0 group-hover/row:opacity-100 transition-opacity mt-1 flex items-center">
                                                        <Eye className="h-3 w-3 mr-1" /> {t.viewJourneyImage}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-2 lg:px-4 py-2 lg:py-3 align-top text-right">
                                                <span className="px-2 lg:px-3 py-0.5 lg:py-1 rounded-lg text-[8px] lg:text-xs font-bold text-white whitespace-nowrap inline-block"
                                                    style={{ backgroundColor: COLORS[urgency] || COLORS.LOW }}>
                                                    {translateUrgency(urgency)}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Image Lightbox */}
            {selectedImage && (
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
            )}
        </div>
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
