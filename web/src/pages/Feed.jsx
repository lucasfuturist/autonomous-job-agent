import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Target, Search, Wifi, MapPin, ShieldAlert, RefreshCw, Star, FileText, Terminal, Ghost } from 'lucide-react';
import JobCard from '../components/JobCard';
import JobModal from '../components/JobModal';

export default function Feed() {
  const [jobs, setJobs] = useState([]);
  const [queueSize, setQueueSize] = useState(0);
  const [displayLimit, setDisplayLimit] = useState(100);
  const [selectedJob, setSelectedJob] = useState(null); 
  
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  const [showRules, setShowRules] = useState(false);
  const [rules, setRules] = useState("");
  const [rescoreLoading, setRescoreLoading] = useState(false);

  // Commander State
  const [command, setCommand] = useState("");
  const [commandLoading, setCommandLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(parseFloat(localStorage.getItem('cns_score') || 5));
  const [remoteOnly, setRemoteOnly] = useState(localStorage.getItem('cns_remote') === 'true');
  const [stateFilter, setStateFilter] = useState(localStorage.getItem('cns_state') || 'ALL');
  const [resumeFilter, setResumeFilter] = useState(localStorage.getItem('cns_resume') || 'ALL');
  const [starsOnly, setStarsOnly] = useState(false);

  const lastJobsRaw = useRef("");
  const lastStatusRaw = useRef("");
  const isTriaging = useRef(false);

  useEffect(() => { localStorage.setItem('cns_score', minScore) }, [minScore]);
  useEffect(() => { localStorage.setItem('cns_remote', remoteOnly) }, [remoteOnly]);
  useEffect(() => { localStorage.setItem('cns_state', stateFilter) }, [stateFilter]);
  useEffect(() => { localStorage.setItem('cns_resume', resumeFilter) }, [resumeFilter]);

  useEffect(() => { setDisplayLimit(100); }, [search, minScore, remoteOnly, stateFilter, resumeFilter, starsOnly]);

  useEffect(() => {
      isTriaging.current = !!selectedJob;
  }, [selectedJob]);

  const fetchData = async () => {
    try {
      const [jobsRes, statusRes] = await Promise.all([fetch('/api/jobs'), fetch('/data/status.json')]);
      
      if (jobsRes.ok) {
        const text = await jobsRes.text();
        if (text !== lastJobsRaw.current && !isTriaging.current) {
            lastJobsRaw.current = text;
            setJobs(JSON.parse(text));
            setIsInitialLoad(false);
        }
      }
      if (statusRes.ok) {
        const text = await statusRes.text();
        if (text !== lastStatusRaw.current) {
            lastStatusRaw.current = text;
            setQueueSize(JSON.parse(text).queue_size);
        }
      }
    } catch (e) { 
        console.error(e); 
        setIsInitialLoad(false);
    }
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

  // --- COMMANDER HANDLER ---
  const handleSendCommand = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;
    setCommandLoading(true);
    try {
        await fetch('/api/agenda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });
        setCommand("");
        alert("Command received. Scout deployed.");
    } catch (e) {
        alert("Failed to send command.");
    } finally {
        setCommandLoading(false);
    }
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

  const availableResumes = useMemo(() => {
    const r = new Set();
    jobs.forEach(j => { if (j.selected_resume) r.add(j.selected_resume); });
    return Array.from(r).sort();
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
    
    if (resumeFilter !== 'ALL' && j.selected_resume !== resumeFilter) return false;

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

  const renderSkeletonCards = () => {
    return Array.from({ length: 8 }).map((_, i) => (
      <div key={i} style={{ background: '#0a0a0a', border: '1px solid #222', borderLeft: '3px solid #333', padding: '10px', height: '120px', display: 'flex', flexDirection: 'column' }} className="fade-in">
         <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <div style={{ width: '60%' }}>
                <div className="skeleton" style={{ height: '16px', width: '100%', marginBottom: '6px' }}></div>
                <div className="skeleton" style={{ height: '12px', width: '50%' }}></div>
            </div>
            <div className="skeleton" style={{ height: '24px', width: '40px', borderRadius: '4px' }}></div>
         </div>
         <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
             <div className="skeleton" style={{ height: '14px', width: '60px' }}></div>
             <div className="skeleton" style={{ height: '14px', width: '40px' }}></div>
         </div>
         <div style={{ display: 'flex', gap: '5px', marginTop: 'auto' }}>
            <div className="skeleton" style={{ height: '24px', flexGrow: 1 }}></div>
            <div className="skeleton" style={{ height: '24px', flexGrow: 1 }}></div>
         </div>
      </div>
    ));
  };

  return (
    <div className="fade-in">
      <JobModal job={selectedJob} onClose={() => setSelectedJob(null)} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onNext={handleNext} onPrev={handlePrev} />
      
      {/* COMMANDER MODULE */}
      <div style={{ marginBottom: '15px' }}>
          <form onSubmit={handleSendCommand} style={{ display: 'flex', gap: '10px' }}>
              <div style={{ flexGrow: 1, position: 'relative' }}>
                  <Terminal size={14} className={commandLoading ? "live-dot" : ""} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent)' }} />
                  <input 
                    type="text" 
                    placeholder="Enter mission command (e.g. 'Hunt for mid-level embedded systems roles in Boston or Remote')..." 
                    value={command} 
                    onChange={(e) => setCommand(e.target.value)} 
                    disabled={commandLoading}
                    style={{ width: '100%', background: '#0a0a0a', border: `1px solid ${commandLoading ? '#333' : 'var(--accent)'}`, color: 'var(--accent)', padding: '10px 10px 10px 35px', borderRadius: '4px', outline: 'none', fontFamily: 'monospace', boxSizing: 'border-box', transition: 'border 0.3s' }} 
                  />
              </div>
              <button type="submit" disabled={commandLoading} style={{ background: commandLoading ? '#222' : 'var(--accent)', color: commandLoading ? '#888' : '#000', border: 'none', padding: '0 20px', borderRadius: '4px', fontWeight: 'bold', cursor: commandLoading ? 'wait' : 'pointer', transition: 'all 0.3s' }}>
                  {commandLoading ? "PARSING..." : "EXECUTE"}
              </button>
          </form>
      </div>

      {/* TACTICAL CONTROLS */}
      <div style={{ marginBottom: '15px' }}>
         <button onClick={() => setShowRules(!showRules)} style={{ background: '#222', border: '1px solid #444', color: '#fff', padding: '8px 15px', borderRadius: '4px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', transition: 'background 0.2s' }}>
            <ShieldAlert size={14} color={rules.length > 5 ? "var(--accent)" : "#666"} />
            TACTICAL RULES {rules.length > 5 && "(ACTIVE)"}
         </button>
         {showRules && (
            <div className="slide-up" style={{ background: '#111', border: '1px solid #333', padding: '15px', marginTop: '10px', borderRadius: '4px' }}>
                <textarea value={rules} onChange={(e) => setRules(e.target.value)} style={{ width: '100%', height: '100px', background: '#000', border: '1px solid #333', color: '#fff', fontFamily: 'monospace', padding: '10px', boxSizing: 'border-box' }} />
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                    <button onClick={handleSaveRules} style={{ background: 'var(--accent)', color: '#000', border: 'none', padding: '8px 15px', fontWeight: 'bold', borderRadius: '2px', cursor: 'pointer' }}>SAVE RULES</button>
                    <button onClick={handleAssimilation} disabled={rescoreLoading} style={{ background: '#222', color: '#fff', border: '1px solid #444', padding: '8px 15px', borderRadius: '2px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        <RefreshCw size={14} className={rescoreLoading ? "live-dot" : ""} />
                        ASSIMILATION (RESCORE)
                    </button>
                </div>
            </div>
         )}
      </div>

      {/* FULL HEADER CONTROLS */}
      <div style={{ background: '#111', padding: '15px', border: '1px solid #333', borderRadius: '4px', display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
        
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexGrow: 1 }}>
          <Search size={16} color="#666" />
          <input type="text" placeholder="Search targets..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '8px', width: '100%', minWidth: '150px', outline: 'none' }} />
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <MapPin size={16} color="#666" />
          <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} style={{ background: '#000', color: '#fff', border: '1px solid #444', padding: '7px', outline: 'none', cursor: 'pointer' }}>
            <option value="ALL">ALL STATES</option>
            {availableStates.map(st => <option key={st} value={st}>{st}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={16} color="#666" />
          <select value={resumeFilter} onChange={(e) => setResumeFilter(e.target.value)} style={{ background: '#000', color: '#fff', border: '1px solid #444', padding: '7px', outline: 'none', maxWidth: '200px', cursor: 'pointer' }}>
            <option value="ALL">ALL RESUMES</option>
            {availableResumes.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Target size={16} color="#666" />
          <input type="range" min="1" max="10" step="0.5" value={minScore} onChange={(e) => setMinScore(parseFloat(e.target.value))} style={{ accentColor: 'var(--accent)', cursor: 'pointer' }} />
          <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{minScore}</span>
        </div>

        {/* Toggles */}
        <button onClick={() => setRemoteOnly(!remoteOnly)} style={{ background: remoteOnly ? 'rgba(0,255,157,0.1)' : '#000', border: `1px solid ${remoteOnly ? 'var(--accent)' : '#444'}`, color: remoteOnly ? 'var(--accent)' : '#666', padding: '7px 12px', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', borderRadius: '3px', transition: 'all 0.2s' }}>
          <Wifi size={14} /> REMOTE
        </button>

        <button onClick={() => setStarsOnly(!starsOnly)} style={{ background: starsOnly ? 'rgba(255,215,0,0.1)' : '#000', border: `1px solid ${starsOnly ? 'gold' : '#444'}`, color: starsOnly ? 'gold' : '#666', padding: '7px 12px', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', borderRadius: '3px', transition: 'all 0.2s' }}>
          <Star size={14} fill={starsOnly ? "gold" : "none"} /> STARRED
        </button>
        
        {/* Telemetry */}
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
        {isInitialLoad ? (
            renderSkeletonCards()
        ) : filteredJobs.length === 0 ? (
            <div style={{ gridColumn: '1 / -1' }} className="empty-state">
                <Ghost size={48} opacity={0.2} color="#fff" />
                <div style={{ fontSize: '16px', color: '#888' }}>NO TARGETS FOUND</div>
                <div style={{ fontSize: '12px', color: '#555' }}>Adjust radar parameters or deploy a new scout command.</div>
            </div>
        ) : (
            visibleJobs.map((job, idx) => (
                <div key={job.id} style={{ animationDelay: `${idx * 0.05}s` }}>
                    <JobCard job={job} onUpdateStatus={handleUpdateStatus} onToggleStar={handleToggleStar} onClick={setSelectedJob} />
                </div>
            ))
        )}
      </div>

      {/* LOAD MORE */}
      {!isInitialLoad && filteredJobs.length > displayLimit && (
        <div style={{ textAlign: 'center', marginTop: '30px', paddingBottom: '30px' }} className="fade-in">
            <button 
                onClick={() => setDisplayLimit(prev => prev + 100)}
                style={{ background: '#111', border: '1px solid var(--accent)', color: 'var(--accent)', padding: '10px 30px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'background 0.2s' }}
                onMouseOver={(e) => e.target.style.background = 'rgba(0, 255, 157, 0.1)'}
                onMouseOut={(e) => e.target.style.background = '#111'}
            >
                LOAD MORE TARGETS ({filteredJobs.length - displayLimit} REMAINING)
            </button>
        </div>
      )}
    </div>
  )
}