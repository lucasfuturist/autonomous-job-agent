import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Search, MapPin, Wifi, Inbox } from 'lucide-react';
import JobCard from '../components/JobCard';
import JobModal from '../components/JobModal';

export default function Board() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null); 
  
  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState(localStorage.getItem('cns_board_state') || 'ALL');
  const [remoteOnly, setRemoteOnly] = useState(false);

  const lastJobsRaw = useRef("");
  const isTriaging = useRef(false);

  useEffect(() => { localStorage.setItem('cns_board_state', stateFilter) }, [stateFilter]);

  // Lock background updates if Modal is open
  useEffect(() => {
      isTriaging.current = !!selectedJob;
  }, [selectedJob]);

  const fetchData = async () => {
    try {
      const res = await fetch('/api/jobs');
      if (res.ok) {
          const text = await res.text();
          if (text !== lastJobsRaw.current && !isTriaging.current) {
              lastJobsRaw.current = text;
              setJobs(JSON.parse(text));
          }
      }
    } catch (e) { console.error("Board sync failed:", e); } 
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); 
    return () => clearInterval(interval);
  }, []);

  const handleUpdateStatus = async (id, newStatus) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, status: newStatus } : j));
    await fetch('/api/update_status', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status: newStatus })
    });
  };

  const handleToggleStar = async (id, starred) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, starred: starred } : j));
    await fetch('/api/star', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, starred })
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

  const filteredJobs = jobs.filter(j => {
    if (search) {
      if (!((j.company + " " + j.title).toLowerCase().includes(search.toLowerCase()))) return false;
    }
    if (stateFilter !== 'ALL') {
      const stateRegex = new RegExp(`\\b${stateFilter}\\b`);
      if (!stateRegex.test((j.location || "").toUpperCase())) return false;
    }
    if (remoteOnly) {
      const txt = (j.location + j.title).toLowerCase();
      if (!txt.includes('remote') && !txt.includes('united states')) return false;
    }
    return true;
  });

  const handleNext = () => {
    if (!selectedJob) return;
    const colJobs = filteredJobs.filter(j => j.status === selectedJob.status);
    const idx = colJobs.findIndex(j => j.id === selectedJob.id);
    if(idx >= 0 && idx < colJobs.length - 1) setSelectedJob(colJobs[idx + 1]);
    else setSelectedJob(null);
  };

  const handlePrev = () => {
    if (!selectedJob) return;
    const colJobs = filteredJobs.filter(j => j.status === selectedJob.status);
    const idx = colJobs.findIndex(j => j.id === selectedJob.id);
    if(idx > 0) setSelectedJob(colJobs[idx - 1]);
  };

  const columns = [
    { id: 'TARGET', title: '🎯 TARGETS', color: '#fff' },
    { id: 'APPLIED', title: '✅ APPLIED', color: 'var(--applied)' },
    { id: 'INTERVIEW', title: '🎤 INTERVIEW', color: 'var(--interview)' },
    { id: 'OFFER', title: '🏆 OFFER', color: 'var(--accent)' },
    { id: 'REJECTED', title: '❌ TRASH', color: 'var(--danger)' }
  ];

  const renderSkeletonBoard = () => {
    return (
      <div style={{ display: 'flex', gap: '15px', overflowX: 'auto', flexGrow: 1, paddingBottom: '10px' }} className="fade-in">
        {columns.map((col, idx) => (
          <div key={idx} style={{ minWidth: '350px', width: '350px', background: '#0a0a0a', border: '1px solid #222', borderRadius: '6px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '15px', borderBottom: '1px solid #222', display: 'flex', justifyContent: 'space-between' }}>
               <div className="skeleton" style={{ height: '16px', width: '40%' }}></div>
               <div className="skeleton" style={{ height: '16px', width: '20px', borderRadius: '10px' }}></div>
            </div>
            <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div className="skeleton" style={{ height: '80px', width: '100%', borderRadius: '4px' }}></div>
                <div className="skeleton" style={{ height: '80px', width: '100%', borderRadius: '4px' }}></div>
                <div className="skeleton" style={{ height: '80px', width: '100%', borderRadius: '4px' }}></div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{ height: 'calc(100vh - 40px)', display: 'flex', flexDirection: 'column' }} className="fade-in">
      <JobModal job={selectedJob} onClose={() => setSelectedJob(null)} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onNext={handleNext} onPrev={handlePrev} />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', margin: 0 }}>WAR ROOM</h1>

        <div style={{ background: '#111', padding: '10px', border: '1px solid #333', borderRadius: '4px', display: 'flex', gap: '15px' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Search size={14} color="#666" />
            <input type="text" placeholder="Filter company..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ background: 'transparent', border: 'none', color: '#fff', width: '120px', fontSize: '12px', outline: 'none' }} />
          </div>

          <div style={{ width: '1px', background: '#333' }}></div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={14} color="#666" />
            <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: '12px', outline: 'none', cursor: 'pointer' }}>
              <option value="ALL">ALL STATES</option>
              {availableStates.map(st => <option key={st} value={st}>{st}</option>)}
            </select>
          </div>

          <div style={{ width: '1px', background: '#333' }}></div>

          <button onClick={() => setRemoteOnly(!remoteOnly)} style={{ background: remoteOnly ? 'rgba(0, 255, 157, 0.1)' : 'transparent', border: `1px solid ${remoteOnly ? 'var(--accent)' : 'transparent'}`, color: remoteOnly ? 'var(--accent)' : '#666', padding: '4px 8px', borderRadius: '3px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', cursor: 'pointer', transition: 'all 0.2s' }}>
            <Wifi size={12} /> REMOTE
          </button>
        </div>
      </div>
      
      {loading ? renderSkeletonBoard() : (
          <div style={{ display: 'flex', gap: '15px', overflowX: 'auto', flexGrow: 1, paddingBottom: '10px' }}>
            {columns.map(col => {
              const colJobs = filteredJobs.filter(j => j.status === col.id);
              const displayJobs = colJobs.slice(0, 100);
              return (
                <div key={col.id} style={{ minWidth: '350px', width: '350px', background: '#0a0a0a', border: '1px solid #222', borderRadius: '6px', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ padding: '15px', borderBottom: '1px solid #222', display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 'bold', color: col.color }}>{col.title}</span>
                    <span style={{ background: '#222', padding: '2px 8px', borderRadius: '10px', fontSize: '11px', color: '#aaa' }}>{colJobs.length}</span>
                  </div>
                  <div style={{ padding: '10px', overflowY: 'auto', flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    
                    {displayJobs.length === 0 ? (
                        <div className="empty-state" style={{ padding: '40px 10px' }}>
                            <Inbox size={32} opacity={0.1} color="#fff" />
                            <div style={{ fontSize: '11px', color: '#444' }}>No active intelligence.</div>
                        </div>
                    ) : (
                        displayJobs.map((job, idx) => (
                          <div key={job.id} style={{ animationDelay: `${idx * 0.05}s` }}>
                              <JobCard job={job} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onClick={setSelectedJob} compact={true} />
                          </div>
                        ))
                    )}
                  </div>
                </div>
              )
            })}
          </div>
      )}
    </div>
  );
}