import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Target, Search, Wifi, MapPin, ShieldAlert, RefreshCw, Star } from 'lucide-react';
import JobCard from '../components/JobCard';
import JobModal from '../components/JobModal';

export default function Feed() {
  const [jobs, setJobs] = useState([]);
  const [queueSize, setQueueSize] = useState(0);
  const [displayLimit, setDisplayLimit] = useState(100);
  const [selectedJob, setSelectedJob] = useState(null); 
  
  const [showRules, setShowRules] = useState(false);
  const [rules, setRules] = useState("");
  const [rescoreLoading, setRescoreLoading] = useState(false);

  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(parseFloat(localStorage.getItem('cns_score') || 5));
  const [remoteOnly, setRemoteOnly] = useState(localStorage.getItem('cns_remote') === 'true');
  const [stateFilter, setStateFilter] = useState(localStorage.getItem('cns_state') || 'ALL');
  const [starsOnly, setStarsOnly] = useState(false);

  // Polling optimization refs
  const lastJobsRaw = useRef("");
  const lastStatusRaw = useRef("");

  useEffect(() => { localStorage.setItem('cns_score', minScore) }, [minScore]);
  useEffect(() => { localStorage.setItem('cns_remote', remoteOnly) }, [remoteOnly]);
  useEffect(() => { localStorage.setItem('cns_state', stateFilter) }, [stateFilter]);

  useEffect(() => { setDisplayLimit(100); }, [search, minScore, remoteOnly, stateFilter, starsOnly]);

  const fetchData = async () => {
    try {
      const [jobsRes, statusRes] = await Promise.all([fetch('/api/jobs'), fetch('/data/status.json')]);
      
      if (jobsRes.ok) {
        const text = await jobsRes.text();
        // Only trigger React state update if the JSON payload actually changed
        if (text !== lastJobsRaw.current) {
            lastJobsRaw.current = text;
            setJobs(JSON.parse(text));
        }
      }
      if (statusRes.ok) {
        const text = await statusRes.text();
        if (text !== lastStatusRaw.current) {
            lastStatusRaw.current = text;
            setQueueSize(JSON.parse(text).queue_size);
        }
      }
    } catch (e) { console.error(e); }
  };

  const fetchRules = async () => {
    try {
      const res = await fetch('/api/rules');
      if (res.ok) setRules((await res.json()).rules);
    } catch(e) {}
  }

  useEffect(() => {
    fetchData();
    fetchRules();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedJob) {
        const updated = jobs.find(j => j.id === selectedJob.id);
        if (updated && updated !== selectedJob && updated.status === selectedJob.status) {
            setSelectedJob(updated);
        }
    }
  }, [jobs]);

  const handleUpdateStatus = async (id, newStatus) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, status: newStatus } : j));
    // Force cache bust on the ref so the next poll doesn't revert our optimistic update
    lastJobsRaw.current = ""; 
    await fetch('/api/update_status', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status: newStatus })
    });
  };

  const handleToggleStar = async (id, starred) => {
    setJobs(prev => prev.map(j => j.id === id ? { ...j, starred: starred } : j));
    lastJobsRaw.current = "";
    await fetch('/api/star', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, starred })
    });
  };

  // ... (Rest of Feed remains identical: handleSaveRules, handleAssimilation, filteredJobs mapping) ...
  const handleSaveRules = async () => {
    await fetch('/api/rules', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rules }) });
    alert("Rules Saved.");
  };

  const handleAssimilation = async () => {
    if(!confirm("Start Assimilation?")) return;
    setRescoreLoading(true);
    await fetch('/api/rescore', { method: 'POST' });
    setTimeout(() => { alert("Assimilation Initiated."); setRescoreLoading(false); }, 1000);
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
    if (j.status !== 'TARGET') return false; 
    if (starsOnly) { if (!j.starred) return false; } else { if (parseFloat(j.score) < minScore) return false; }
    if (remoteOnly) { if (!((j.location+j.title).toLowerCase().includes('remote'))) return false; }
    if (stateFilter !== 'ALL') {
      const loc = (j.location || "").toUpperCase();
      const stateRegex = new RegExp(`\\b${stateFilter}\\b`);
      if (!stateRegex.test(loc)) return false;
    }
    if (search) {
      const query = search.toLowerCase();
      const content = (j.company + " " + j.title + " " + (j.location || "") + " " + (j.search_term || "")).toLowerCase();
      if (!content.includes(query)) return false;
    }
    return true;
  });

  const visibleJobs = filteredJobs.slice(0, displayLimit);

  const handleNext = () => {
      if (!selectedJob) return;
      const idx = visibleJobs.findIndex(j => j.id === selectedJob.id);
      if (idx >= 0 && idx < visibleJobs.length - 1) setSelectedJob(visibleJobs[idx + 1]);
      else setSelectedJob(null);
  };

  const handlePrev = () => {
      if (!selectedJob) return;
      const idx = visibleJobs.findIndex(j => j.id === selectedJob.id);
      if (idx > 0) setSelectedJob(visibleJobs[idx - 1]);
  };

  return (
    <div>
      <JobModal job={selectedJob} onClose={() => setSelectedJob(null)} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onNext={handleNext} onPrev={handlePrev} />
      {/* ... (TACTICAL CONTROLS & HEADER HTML Identical to previous) ... */}
      <div style={{ marginBottom: '15px' }}>
         <button onClick={() => setShowRules(!showRules)} style={{ background: '#222', border: '1px solid #444', color: '#fff', padding: '8px 15px', borderRadius: '4px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={14} color={rules.length > 5 ? "var(--accent)" : "#666"} />
            TACTICAL RULES {rules.length > 5 && "(ACTIVE)"}
         </button>
         {showRules && (
            <div style={{ background: '#111', border: '1px solid #333', padding: '15px', marginTop: '10px', borderRadius: '4px' }}>
                <textarea value={rules} onChange={(e) => setRules(e.target.value)} style={{ width: '100%', height: '100px', background: '#000', border: '1px solid #333', color: '#fff', fontFamily: 'monospace', padding: '10px', boxSizing: 'border-box' }} />
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                    <button onClick={handleSaveRules} style={{ background: 'var(--accent)', color: '#000', border: 'none', padding: '8px 15px', fontWeight: 'bold', borderRadius: '2px' }}>SAVE RULES</button>
                </div>
            </div>
         )}
      </div>

      <div style={{ background: '#111', padding: '15px', border: '1px solid #333', borderRadius: '4px', display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexGrow: 1 }}>
          <Search size={16} color="#666" />
          <input type="text" placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '8px', width: '100%', minWidth: '200px' }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Target size={16} color="#666" />
          <input type="range" min="1" max="10" step="0.5" value={minScore} onChange={(e) => setMinScore(parseFloat(e.target.value))} style={{ accentColor: 'var(--accent)' }} />
          <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{minScore}</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))', gap: '15px' }}>
        {visibleJobs.map(job => (
          <JobCard key={job.id} job={job} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onClick={setSelectedJob} />
        ))}
      </div>
    </div>
  )
}