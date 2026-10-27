// Owner: Person 3
// Purpose: Activity log view with action history, model provider column, and one-click undo

import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ActivityLogItem } from '../api/types';

export const ActivityLog: React.FC = () => {
  const [activities, setActivities] = useState<ActivityLogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [undoMessage, setUndoMessage] = useState<string | null>(null);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const res = await api.getActivity();
      setActivities(res.activities);
    } catch (err: any) {
      console.error('Failed to load activity logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  const handleUndo = async (actionId: string) => {
    try {
      setUndoMessage(null);
      const res = await api.undoAction(actionId);
      setUndoMessage(res.message);
      await fetchActivities();
    } catch (err: any) {
      setUndoMessage(`Undo error: ${err.message}`);
    }
  };

  return (
    <section id="page-activity-log">
      <header>
        <h1>Activity Log & Audit Trail</h1>
        <p className="subtitle">
          Every tool invocation is tracked with its model provider provenance. Easily revert
          mutating actions with one click.
        </p>
      </header>

      {undoMessage && (
        <div
          id="undo-status-banner"
          style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            color: '#c7d2fe',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
          }}
        >
          {undoMessage}
        </div>
      )}

      <div className="card">
        <div className="card-title">
          <span>Recent System Actions</span>
          <button className="btn btn-secondary" onClick={fetchActivities} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        <div className="table-container">
          <table id="activity-table">
            <thead>
              <tr>
                <th>Action Type</th>
                <th>Agent</th>
                <th>Provider</th>
                <th>Status</th>
                <th>Time</th>
                <th>Undo Action</th>
              </tr>
            </thead>
            <tbody>
              {activities.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    No activity recorded yet. Run an agent or reset sample data.
                  </td>
                </tr>
              ) : (
                activities.map((item) => (
                  <tr key={item.id} id={`activity-row-${item.id}`}>
                    <td style={{ fontWeight: 600, color: '#e0e7ff' }}>{item.action_type}</td>
                    <td>{item.agent}</td>
                    <td>
                      <span
                        className={
                          item.provider === 'nebius'
                            ? 'badge badge-nebius'
                            : item.provider === 'local'
                            ? 'badge badge-local'
                            : 'badge badge-mock'
                        }
                      >
                        {item.provider}
                      </span>
                    </td>
                    <td>
                      <span
                        className={
                          item.status === 'completed'
                            ? 'badge badge-completed'
                            : 'badge badge-pending'
                        }
                      >
                        {item.status}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {item.created_at || 'Just now'}
                    </td>
                    <td>
                      {item.undo_payload && item.status !== 'undone' ? (
                        <button
                          id={`btn-undo-${item.id}`}
                          className="btn btn-undo"
                          onClick={() => handleUndo(item.id)}
                        >
                          Undo
                        </button>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {item.status === 'undone' ? 'Undone' : 'None'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
