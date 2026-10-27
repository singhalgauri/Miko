// Owner: Person 3
// Purpose: Permissions policy configuration interface for action types

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';

export const Permissions: React.FC = () => {
  const [permissions, setPermissions] = useState<Record<string, string>>({});
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  const fetchPermissions = async () => {
    try {
      const res = await api.getPermissions();
      setPermissions(res.permissions);
    } catch (err: any) {
      console.error('Failed to load permissions:', err);
    }
  };

  useEffect(() => {
    fetchPermissions();
  }, []);

  const handlePolicyChange = async (actionType: string, newPolicy: string) => {
    try {
      setSaveStatus(null);
      await api.updatePermission(actionType, newPolicy);
      setPermissions((prev) => ({ ...prev, [actionType]: newPolicy }));
      setSaveStatus(`Updated '${actionType}' to '${newPolicy}'`);
    } catch (err: any) {
      setSaveStatus(`Failed to update: ${err.message}`);
    }
  };

  return (
    <section id="page-permissions">
      <header>
        <h1>Security & Permissions Gateway</h1>
        <p className="subtitle">
          Configure autonomy levels for each tool action: <strong>act_alone</strong> (autonomous),{' '}
          <strong>ask_first</strong> (pause for approval), or <strong>never</strong> (hard block).
        </p>
      </header>

      {saveStatus && (
        <div
          id="permission-save-banner"
          style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            color: '#c7d2fe',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
          }}
        >
          {saveStatus}
        </div>
      )}

      <div className="card">
        <div className="card-title">Action Permission Rules</div>
        <div className="table-container">
          <table id="permissions-table">
            <thead>
              <tr>
                <th>Action Identifier</th>
                <th>Security Rule</th>
                <th>Policy Description</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(permissions).map(([action, policy]) => (
                <tr key={action} id={`perm-row-${action}`}>
                  <td style={{ fontWeight: 600 }}>{action}</td>
                  <td style={{ width: '220px' }}>
                    <select
                      id={`select-perm-${action}`}
                      value={policy}
                      onChange={(e) => handlePolicyChange(action, e.target.value)}
                    >
                      <option value="act_alone">act_alone (Autonomous)</option>
                      <option value="ask_first">ask_first (Require Approval)</option>
                      <option value="never">never (Disallowed)</option>
                    </select>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {policy === 'act_alone' && 'Executes without interrupting your workflow.'}
                    {policy === 'ask_first' && 'Shows interactive card in Approvals tab.'}
                    {policy === 'never' && 'Denied automatically with security exception.'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
