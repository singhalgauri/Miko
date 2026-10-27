// Owner: Person 3
// Purpose: Daily briefing and catch-up synthesis interface

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';

export const Briefing: React.FC = () => {
  const [briefingData, setBriefingData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchBriefing = async () => {
    try {
      setLoading(true);
      const res = await api.runAgent('briefing');
      setBriefingData(res.output);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBriefing();
  }, []);

  return (
    <section id="page-briefing">
      <header>
        <h1>Daily Briefing & Catch-up</h1>
        <p className="subtitle">
          Morning synthesis of your agenda, priority emails, and events while your PC was idle.
        </p>
      </header>

      <div className="card">
        <div className="card-title">
          <span>Morning Overview</span>
          <button className="btn btn-secondary" onClick={fetchBriefing} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Briefing'}
          </button>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <p style={{ fontSize: '1.05rem', lineHeight: '1.7', color: '#e0e7ff' }}>
            {briefingData?.briefing_text ||
              'Good morning! You have 3 meetings and 2 high-priority follow-ups scheduled for today.'}
          </p>
        </div>

        <div className="grid-2">
          <div className="card" style={{ background: 'rgba(0,0,0,0.2)', marginBottom: 0 }}>
            <h4 style={{ marginBottom: '12px', color: '#818cf8' }}>Today's Agenda Highlights</h4>
            <ul style={{ listStylePosition: 'inside', fontSize: '0.9rem', color: '#d1d5db', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <li>10:00 AM — Engineering Sprint Sync</li>
              <li>12:30 PM — Hackathon Check-in</li>
              <li>03:00 PM — Nebius Demo Walkthrough</li>
            </ul>
          </div>

          <div className="card" style={{ background: 'rgba(0,0,0,0.2)', marginBottom: 0 }}>
            <h4 style={{ marginBottom: '12px', color: '#10b981' }}>While You Were Away</h4>
            <p style={{ fontSize: '0.85rem', color: '#9ca3af', marginBottom: '8px' }}>
              Catch-up service evaluated 3 incoming items:
            </p>
            <ul style={{ listStylePosition: 'inside', fontSize: '0.9rem', color: '#d1d5db', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <li>Sarah requested milestone review</li>
              <li>Calendar invite: Demo Recording confirmed</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};
