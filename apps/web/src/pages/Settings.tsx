// Owner: Person 3
// Purpose: Settings configuration interface for model provider selection and network options

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { SettingsResponse } from '../api/types';

interface SettingsProps {
  onProviderChange: (provider: string) => void;
}

export const Settings: React.FC<SettingsProps> = ({ onProviderChange }) => {
  const [config, setConfig] = useState<SettingsResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    api.getSettings().then(setConfig).catch(console.error);
  }, []);

  const handleProviderSelect = async (newProvider: string) => {
    try {
      setStatusMessage(null);
      const updated = await api.updateSettings({ provider: newProvider });
      setConfig(updated);
      onProviderChange(updated.provider);
      setStatusMessage(`Provider switched to: ${updated.provider.toUpperCase()}`);
    } catch (err: any) {
      setStatusMessage(`Failed to switch provider: ${err.message}`);
    }
  };

  const handleToggleOffline = async (enabled: boolean) => {
    try {
      const updated = await api.updateSettings({ offline_mode: enabled });
      setConfig(updated);
    } catch (err: any) {
      console.error(err);
    }
  };

  if (!config) {
    return <div className="card">Loading settings...</div>;
  }

  return (
    <section id="page-settings">
      <header>
        <h1>System Settings</h1>
        <p className="subtitle">
          Manage your inference engine, privacy posture, and connection parameters.
        </p>
      </header>

      {statusMessage && (
        <div
          id="settings-status-alert"
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#6ee7b7',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
          }}
        >
          {statusMessage}
        </div>
      )}

      <div className="card">
        <div className="card-title">Inference Engine / Model Provider</div>
        <div className="grid-3">
          <div
            id="provider-card-mock"
            className="card"
            style={{
              cursor: 'pointer',
              borderColor: config.provider === 'mock' ? 'var(--primary)' : 'var(--border-color)',
            }}
            onClick={() => handleProviderSelect('mock')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="dot dot-purple" />
              <strong>Mock Mode</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Deterministic canned answers. Zero GPU or model installation needed.
            </p>
          </div>

          <div
            id="provider-card-local"
            className="card"
            style={{
              cursor: 'pointer',
              borderColor: config.provider === 'local' ? 'var(--accent-local)' : 'var(--border-color)',
            }}
            onClick={() => handleProviderSelect('local')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="dot dot-green" />
              <strong>Local (Ollama)</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              100% private. Strict 127.0.0.1 binding. No prompts leave this computer.
            </p>
          </div>

          <div
            id="provider-card-nebius"
            className="card"
            style={{
              cursor: 'pointer',
              borderColor: config.provider === 'nebius' ? 'var(--accent-nebius)' : 'var(--border-color)',
            }}
            onClick={() => handleProviderSelect('nebius')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="dot dot-orange" />
              <strong>Nebius Token Factory</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              NVIDIA Nemotron via OpenAI-compatible endpoint. High token velocity.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Connection Endpoints</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              Nebius Base URL
            </label>
            <input type="text" readOnly value={config.nebius_base_url} />
          </div>

          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              Ollama Host (Strict 127.0.0.1)
            </label>
            <input type="text" readOnly value={config.ollama_host} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
            <input
              type="checkbox"
              id="chk-offline"
              checked={config.offline_mode}
              style={{ width: 'auto' }}
              onChange={(e) => handleToggleOffline(e.target.checked)}
            />
            <label htmlFor="chk-offline" style={{ fontSize: '0.9rem' }}>
              Strict Offline Mode (hard-block any outbound WAN requests)
            </label>
          </div>
        </div>
      </div>
    </section>
  );
};
