// Owner: Person 3
// Purpose: Main dashboard displaying agent status, quick action triggers, and active jobs

import React, { useState } from 'react';
import { api } from '../api/client';

interface DashboardProps {
  provider: string;
  onNavigate: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ provider, onNavigate }) => {
  const [runningAgent, setRunningAgent] = useState<string | null>(null);
  const [agentOutput, setAgentOutput] = useState<string | null>(null);

  const handleRunAgent = async (name: string, inputText = '') => {
    try {
      setRunningAgent(name);
      setAgentOutput(null);
      const res = await api.runAgent(name, inputText);
      setAgentOutput(JSON.stringify(res.output, null, 2));
    } catch (err: any) {
      setAgentOutput(`Error: ${err.message}`);
    } finally {
      setRunningAgent(null);
    }
  };

  return (
    <section id="page-dashboard">
      <header>
        <h1>Personal AI Workspace</h1>
        <p className="subtitle">
          Autonomous, local-first intelligence running securely on your machine.
        </p>
      </header>

      <div className="grid-3" style={{ marginBottom: '28px' }}>
        <article className="card" id="card-stat-mode">
          <div className="card-title">Active Provider</div>
          <p style={{ fontSize: '1.25rem', fontWeight: 600, color: '#818cf8' }}>
            {provider.toUpperCase()}
          </p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {provider === 'local'
              ? 'Ollama 127.0.0.1 (Offline)'
              : provider === 'nebius'
              ? 'Nebius Token Factory (Nemotron)'
              : 'Deterministic mock development mode'}
          </p>
        </article>

        <article className="card" id="card-stat-security">
          <div className="card-title">Permission Gateway</div>
          <p style={{ fontSize: '1.25rem', fontWeight: 600, color: '#10b981' }}>
            ENFORCING
          </p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            File moves & emails intercept at gateway
          </p>
        </article>

        <article className="card" id="card-stat-privacy">
          <div className="card-title">Telemetry</div>
          <p style={{ fontSize: '1.25rem', fontWeight: 600, color: '#9ca3af' }}>
            DISABLED
          </p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Zero logs or analytics sent off device
          </p>
        </article>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Core Agent Jobs (v1)</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            One-click invocation
          </span>
        </div>

        <div className="grid-2">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4>Inbox Triage</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Scan unread emails, classify urgency, and propose draft replies.
            </p>
            <button
              id="btn-run-inbox"
              className="btn btn-primary"
              style={{ alignSelf: 'flex-start' }}
              onClick={() => handleRunAgent('inbox')}
              disabled={runningAgent !== null}
            >
              {runningAgent === 'inbox' ? 'Triaging...' : 'Run Inbox Triage'}
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4>File Organiser</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Scan clutter in Downloads and propose structured moves with undo.
            </p>
            <button
              id="btn-run-files"
              className="btn btn-secondary"
              style={{ alignSelf: 'flex-start' }}
              onClick={() => handleRunAgent('file_organiser')}
              disabled={runningAgent !== null}
            >
              {runningAgent === 'file_organiser' ? 'Planning...' : 'Organise Downloads'}
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4>Document Search</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Semantic retrieval across local PDFs and notes with page citations.
            </p>
            <button
              id="btn-goto-documents"
              className="btn btn-secondary"
              style={{ alignSelf: 'flex-start' }}
              onClick={() => onNavigate('documents')}
            >
              Open Document Search
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <h4>Daily Briefing</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Morning synthesis of calendar, unread items, and while-you-were-away catchup.
            </p>
            <button
              id="btn-goto-briefing"
              className="btn btn-secondary"
              style={{ alignSelf: 'flex-start' }}
              onClick={() => onNavigate('briefing')}
            >
              Generate Daily Briefing
            </button>
          </div>
        </div>

        {agentOutput && (
          <div style={{ marginTop: '20px' }}>
            <h4>Agent Output</h4>
            <pre
              id="agent-output-box"
              style={{
                background: 'rgba(0,0,0,0.4)',
                padding: '14px',
                borderRadius: '8px',
                overflowX: 'auto',
                fontSize: '0.85rem',
                color: '#a5b4fc',
                marginTop: '8px',
              }}
            >
              {agentOutput}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
};
