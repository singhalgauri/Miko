// Owner: Person 3
// Purpose: Document search and citation viewer interface

import React, { useState } from 'react';
import { api } from '../api/client';

export const Documents: React.FC = () => {
  const [query, setQuery] = useState('termination clause notice period');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      setLoading(true);
      const res = await api.runAgent('document', query);
      setResult(res.output);
    } catch (err: any) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="page-documents">
      <header>
        <h1>Document Search & Citations</h1>
        <p className="subtitle">
          Local semantic indexing powered by sqlite-vec with page-grounded citations.
        </p>
      </header>

      <div className="card">
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px' }}>
          <input
            id="input-doc-query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search within contracts, receipts, or notes..."
            style={{ flex: 1 }}
          />
          <button id="btn-search-docs" type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card" id="document-search-results">
          <div className="card-title">
            <span>Synthesized Answer</span>
            <span className="badge badge-completed">Grounded</span>
          </div>

          <p style={{ fontSize: '1rem', lineHeight: '1.6', marginBottom: '20px' }}>
            {result.answer || JSON.stringify(result)}
          </p>

          {result.citations && result.citations.length > 0 && (
            <div>
              <h4 style={{ marginBottom: '10px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                Verified Citations
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {result.citations.map((c: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid var(--border-color)',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span style={{ fontSize: '0.85rem' }}>"{c.snippet}"</span>
                    <span
                      className="badge"
                      style={{ background: 'rgba(99,102,241,0.2)', color: '#818cf8' }}
                    >
                      {c.source} (p.{c.page})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
