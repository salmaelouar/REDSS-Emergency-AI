import React from 'react';
import { Routes, Route } from 'react-router-dom';
import EmergencyManager from './EmergencyManager';
import TransparentMonitor from './TransparentMonitor';
import PrintableReport from './PrintableReport';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<EmergencyManager />} />
      <Route path="/dnp" element={<TransparentMonitor />} />
      <Route path="/report" element={<PrintableReport />} />
      {/* Fallback to main dashboard for any other route */}
      <Route path="*" element={<EmergencyManager />} />
    </Routes>
  );
}

export default App;