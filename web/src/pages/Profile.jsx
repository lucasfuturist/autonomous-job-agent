import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Profile() {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/api/stats').then(res => res.json()).then(setStats).catch(console.error);
    fetch('/api/logs').then(res => res.json()).then(setLogs).catch(console.error);
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

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
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

        {/* MISSION LOGS (NEW) */}
        <div style={{ background: '#0a0a0a', border: '1px solid #222', padding: '20px', overflowY: 'auto', height: '300px' }}>
            <h3 style={{ marginTop: 0 }}>MISSION LOGS (HISTORY)</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', fontSize: '10px', color: '#666', borderBottom: '1px solid #333', paddingBottom: '5px' }}>
                    <div style={{ flex: 1 }}>TIMESTAMP</div>
                    <div style={{ flex: 2 }}>TERM</div>
                    <div style={{ width: '50px', textAlign: 'right' }}>FOUND</div>
                    <div style={{ width: '50px', textAlign: 'right' }}>NEW</div>
                </div>
                {logs.map((log, i) => (
                    <div key={i} style={{ display: 'flex', fontSize: '11px', borderBottom: '1px solid #111', paddingBottom: '4px' }}>
                        <div style={{ flex: 1, color: '#888' }}>{new Date(log.run_at).toLocaleTimeString()}</div>
                        <div style={{ flex: 2, color: '#eee', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.term}</div>
                        <div style={{ width: '50px', textAlign: 'right', color: '#888' }}>{log.items_found}</div>
                        <div style={{ width: '50px', textAlign: 'right', color: log.items_new > 0 ? 'var(--accent)' : '#444' }}>{log.items_new}</div>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  )
}