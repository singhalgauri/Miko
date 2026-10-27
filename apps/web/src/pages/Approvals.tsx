// Owner: Person 3
// Purpose: Human-in-the-loop approval management interface

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ApprovalItem } from '../api/types';

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      const res = await api.getApprovals();
      setApprovals(res.approvals);
    } catch (err: any) {
      console.error('Failed to load approvals:', err);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleDecision = async (id: string, approved: boolean) => {
    try {
      const res = await api.decideApproval(id, approved);
      setMessage(res.message);
      setApprovals((prev) => prev.filter((a) => a.id !== id));
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <section id="page-approvals">
      <header>
        <h1>Pending Approvals</h1>
        <p className="subtitle">
          Actions flagged as 'ask_first' by the Permission Gateway require your manual review.
        </p>
      </header>

      {message && (
        <div
          id="approval-decision-alert"
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#6ee7b7',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
          }}
        >
          {message}
        </div>
      )}

      {approvals.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--text-muted)' }}>No actions waiting for approval right now.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {approvals.map((appr) => (
            <div key={appr.id} className="card" id={`approval-card-${appr.id}`}>
              <div className="card-title">
                <span>
                  Action Request: <span style={{ color: '#818cf8' }}>{appr.action_type}</span>
                </span>
                <span className="badge badge-pending">Requires Approval</span>
              </div>

              <p style={{ fontSize: '1rem', marginBottom: '16px' }}>{appr.prompt}</p>

              <div
                style={{
                  background: 'rgba(0,0,0,0.3)',
                  padding: '12px',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  fontFamily: 'monospace',
                  marginBottom: '20px',
                }}
              >
                {JSON.stringify(appr.params, null, 2)}
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  id={`btn-approve-${appr.id}`}
                  className="btn btn-primary"
                  onClick={() => handleDecision(appr.id, true)}
                >
                  Approve Action
                </button>
                <button
                  id={`btn-reject-${appr.id}`}
                  className="btn btn-danger"
                  onClick={() => handleDecision(appr.id, false)}
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
