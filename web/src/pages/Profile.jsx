
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Profile() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/stats').then(res => res.json()).then(setStats).catch(console.error);
  }, []);

  if (!stats) return <div>Loading Profile...</div>;

  const pipeData = Object.keys(stats.pipeline).map(k => ({ name: k, count: stats.pipeline[k] }));

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>COMMAND PROFILE</h1>
      
      {/* KPI ROW */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '30px' }}>
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px' }}>
          <div style={{ color: '#666', fontSize: '11px', marginBottom: '5px' }}>TOTAL SCANNED</div>
          <div style={{ fontSize: '28px', color: '#fff' }}>{stats.total_scanned}</div>
        </div>
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px' }}>
          <div style={{ color: '#666', fontSize: '11px', marginBottom: '5px' }}>APPLIED</div>
          <div style={{ fontSize: '28px', color: 'var(--applied)' }}>{stats.pipeline.APPLIED || 0}</div>
        </div>
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px' }}>
          <div style={{ color: '#666', fontSize: '11px', marginBottom: '5px' }}>INTERVIEWS</div>
          <div style={{ fontSize: '28px', color: 'var(--interview)' }}>{stats.pipeline.INTERVIEW || 0}</div>
        </div>
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px' }}>
          <div style={{ color: '#666', fontSize: '11px', marginBottom: '5px' }}>AVG QUALITY</div>
          <div style={{ fontSize: '28px', color: 'var(--accent)' }}>{parseFloat(stats.avg_quality).toFixed(1)}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* CHART */}
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px', height: '300px' }}>
            <h3 style={{ marginTop: 0 }}>PIPELINE DISTRIBUTION</h3>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pipeData}>
                    <XAxis dataKey="name" stroke="#444" fontSize={10} />
                    <YAxis stroke="#444" fontSize={10} />
                    <Tooltip contentStyle={{ background: '#111', border: '1px solid #333' }} />
                    <Bar dataKey="count" fill="var(--accent)" />
                </BarChart>
            </ResponsiveContainer>
        </div>

        {/* STRATEGIES */}
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px' }}>
            <h3 style={{ marginTop: 0 }}>TOP STRATEGIES</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {stats.strategies.map((s, i) => (
                    <div key={i} style={{ borderBottom: '1px solid #222', paddingBottom: '8px' }}>
                        <div style={{ fontWeight: 'bold', color: '#eee' }}>{s.term}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#666', marginTop: '2px' }}>
                            <span>FOUND: {s.total_found}</span>
                            <span style={{ color: s.avg_score > 7 ? 'var(--accent)' : '#888' }}>QUAL: {parseFloat(s.avg_score).toFixed(1)}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  )
}