import React, { useState, useEffect, useMemo } from 'react';
import { Target, Search, Wifi, MapPin } from 'lucide-react';
import JobCard from '../components/JobCard';

export default function Feed() {
  const [jobs, setJobs] = useState([]);
  const [queueSize, setQueueSize] = useState(0);
  const [displayLimit, setDisplayLimit] = useState(100); // UI Render Cap
  
  // Filters
  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(parseFloat(localStorage.getItem('cns_score') || 5));
  const [remoteOnly, setRemoteOnly] = useState(localStorage.getItem('cns_remote') === 'true');
  const [stateFilter, setStateFilter] = useState(localStorage.getItem('cns_state') || 'ALL');

  useEffect(() => { localStorage.setItem('cns_score', minScore) }, [minScore]);
  useEffect(() => { localStorage.setItem('cns_remote', remoteOnly) }, [remoteOnly]);
  useEffect(() => { localStorage.setItem('cns_state', stateFilter) }, [stateFilter]);

  // Reset display limit when a user actively filters (sends them back to top of new results)
  useEffect(() => {
    setDisplayLimit(100);
  }, [search, minScore, remoteOnly, stateFilter]);

  const fetchData = async () => {
    try {
      const [jobsRes, statusRes] = await Promise.all([
        fetch('/api/jobs'), 
        fetch('/data/status.json')
      ]);
      if (jobsRes.ok) setJobs(await jobsRes.json());
      if (statusRes.ok) setQueueSize((await statusRes.json()).queue_size);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleUpdateStatus = async (id, newStatus) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, status: newStatus } : j));
    await fetch('/api/update_status', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status: newStatus })
    });
  };

  const availableStates = useMemo(() => {
    const st = new Set();
    jobs.forEach(j => {
      if (!j.location) return;
      const match = j.location.match(/\b([A-Z]{2})\b/);
      if (match && match[1] !== 'US') st.add(match[1]);
    });
    return Array.from(st).sort();
  }, [jobs]);

  // --- FILTER LOGIC (Runs on full dataset) ---
  const filteredJobs = jobs.filter(j => {
    if (j.status !== 'TARGET') return false; 
    if (parseFloat(j.score) < minScore) return false;
    
    if (remoteOnly) {
      if (!((j.location+j.title).toLowerCase().includes('remote'))) return false;
    }

    if (stateFilter !== 'ALL') {
      const loc = (j.location || "").toUpperCase();
      const stateRegex = new RegExp(`\\b${stateFilter}\\b`);
      if (!stateRegex.test(loc)) return false;
    }
    
    if (search) {
      const query = search.toLowerCase();
      const content = (
        j.company + " " + 
        j.title + " " + 
        (j.location || "") + " " + 
        (j.search_term || "")
      ).toLowerCase();
      
      if (!content.includes(query)) return false;
    }
    return true;
  });

  // Render slice
  const visibleJobs = filteredJobs.slice(0, displayLimit);

  return (
    <div>
      {/* HEADER CONTROLS */}
      <div style={{ background: '#111', padding: '15px', border: '1px solid #333', borderRadius: '4px', display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexGrow: 1 }}>
          <Search size={16} color="#666" />
          <input 
            type="text" 
            placeholder="Search company, city, title..." 
            value={search} 
            onChange={(e) => setSearch(e.target.value)} 
            style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '8px', width: '100%', minWidth: '200px' }} 
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <MapPin size={16} color="#666" />
          <select 
            value={stateFilter} 
            onChange={(e) => setStateFilter(e.target.value)}
            style={{ background: '#000', color: '#fff', border: '1px solid #444', padding: '7px', outline: 'none' }}
          >
            <option value="ALL">ALL STATES</option>
            {availableStates.map(st => <option key={st} value={st}>{st}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Target size={16} color="#666" />
          <input type="range" min="1" max="10" step="0.5" value={minScore} onChange={(e) => setMinScore(parseFloat(e.target.value))} style={{ accentColor: 'var(--accent)' }} />
          <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{minScore}</span>
        </div>

        <button onClick={() => setRemoteOnly(!remoteOnly)} style={{ background: remoteOnly ? 'rgba(0,255,157,0.1)' : '#000', border: `1px solid ${remoteOnly ? 'var(--accent)' : '#444'}`, color: remoteOnly ? 'var(--accent)' : '#666', padding: '7px 12px', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
          <Wifi size={14} /> REMOTE ONLY
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', borderLeft: '1px solid #333', paddingLeft: '15px' }}>
           <div style={{ fontSize: '12px', color: '#666' }}>
             SHOWING: <span style={{ color: '#fff' }}>{visibleJobs.length}</span> / {filteredJobs.length}
           </div>
           <div style={{ fontSize: '12px', color: queueSize > 10 ? 'var(--warning)' : 'var(--accent)' }}>
             PENDING: {queueSize}
           </div>
        </div>
      </div>

      {/* GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))', gap: '15px' }}>
        {filteredJobs.length === 0 && <div style={{ color: '#666', padding: '20px' }}>No targets found. Try lowering score or widening search.</div>}
        {visibleJobs.map(job => (
          <JobCard key={job.id} job={job} onUpdateStatus={handleUpdateStatus} />
        ))}
      </div>

      {/* LOAD MORE */}
      {filteredJobs.length > displayLimit && (
        <div style={{ textAlign: 'center', marginTop: '30px', paddingBottom: '30px' }}>
            <button 
                onClick={() => setDisplayLimit(prev => prev + 100)}
                style={{ 
                    background: '#111', border: '1px solid var(--accent)', color: 'var(--accent)', 
                    padding: '10px 30px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer' 
                }}
            >
                LOAD MORE TARGETS ({filteredJobs.length - displayLimit} REMAINING)
            </button>
        </div>
      )}
    </div>
  )
}