import React, { useState, useMemo } from 'react';
import { ExternalLink, Copy, Check, X, Mic, ArrowRight, RotateCcw, Star, DollarSign, ShieldAlert, Cpu, Globe, Briefcase, Clock } from 'lucide-react';

const JobCard = ({ job, onUpdateStatus, onToggleStar, onClick, compact = false }) => {
  const [showScript, setShowScript] = useState(false);
  const [copied, setCopied] = useState(false);

  const parts = (job.reason || "").split("### DEPLOYMENT SCRIPT:");
  const scriptContent = parts.length > 1 ? parts[1].trim() : null;

  // --- PARSE ENRICHED DATA ---
  const techStack = useMemo(() => {
    try { return job.tech_stack_core ? JSON.parse(job.tech_stack_core) : []; } catch { return []; }
  }, [job.tech_stack_core]);

  const salaryString = useMemo(() => {
    if (!job.salary_base_min && !job.salary_base_max) return null;
    const fmt = (n) => n >= 1000 ? `$${Math.round(n/1000)}k` : `$${n}`;
    if (job.salary_base_min && job.salary_base_max) return `${fmt(job.salary_base_min)} - ${fmt(job.salary_base_max)}`;
    return fmt(job.salary_base_min || job.salary_base_max) + "+";
  }, [job.salary_base_min, job.salary_base_max]);

  const timeAgo = useMemo(() => {
    if (!job.found_at) return "";
    
    // Parse timestamp defensively. 
    // SQLite default CURRENT_TIMESTAMP is UTC 'YYYY-MM-DD HH:MM:SS'. 
    // Appending 'Z' ensures JS treats it as UTC, preventing timezone drift.
    let dateStr = job.found_at;
    if (!dateStr.endsWith('Z') && !dateStr.includes('+')) {
        dateStr += 'Z';
    }
    
    const now = new Date();
    const found = new Date(dateStr);
    
    // Fallback if date parsing fails
    if (isNaN(found.getTime())) return "";

    const seconds = Math.floor((now - found) / 1000);
    
    // Handle future dates (clock skew)
    if (seconds < 0) return "just now";

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + "y ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + "mo ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + "d ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + "h ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + "m ago";
    
    return Math.floor(seconds) + "s ago";
  }, [job.found_at]);

  const hasClearance = job.clearance_required && job.clearance_required !== "None";

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(scriptContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const stopProp = (e) => e.stopPropagation();

  let borderStyle = '3px solid var(--accent)';
  let bgStyle = 'var(--card-bg)';
  if (job.status === 'APPLIED') { borderStyle = '3px solid var(--applied)'; }
  else if (job.status === 'INTERVIEW') { borderStyle = '3px solid var(--interview)'; bgStyle = '#050a10'; }
  else if (job.status === 'OFFER') { borderStyle = '3px solid #fff'; }
  else if (job.status === 'REJECTED') { borderStyle = '3px solid var(--danger)'; bgStyle = '#1a0505'; }

  const isStarred = job.starred === 1 || job.starred === true;

  // Render Distance Badge Helper
  const renderDistanceBadge = () => {
    if (job.distance === undefined || job.distance === null) return null;
    if (job.distance === -1 || job.distance === -1.0) {
        return <span style={{ border: '1px solid #333', color: '#888', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>🌐 Remote</span>;
    }
    const isClose = job.distance <= 30;
    return (
        <span style={{ border: `1px solid ${isClose ? 'var(--accent)' : '#333'}`, color: isClose ? 'var(--accent)' : '#888', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>
            🚗 {Math.round(job.distance)} mi
        </span>
    );
  };

  return (
    <div 
      onClick={() => onClick && onClick(job)}
      style={{ 
        background: bgStyle, border: '1px solid #222', borderLeft: borderStyle, 
        padding: '10px', display: 'flex', flexDirection: 'column', position: 'relative',
        fontSize: compact ? '11px' : '13px', cursor: 'pointer', transition: 'transform 0.1s, border-color 0.2s, background 0.2s'
      }}
      className="job-card-hover slide-up fade-in"
    >
      {/* HEADER ROW */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <div style={{ overflow: 'hidden', flexGrow: 1 }}>
          <div style={{ fontSize: compact ? '13px' : '16px', fontWeight: 'bold', color: '#fff', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }} title={job.title}>
            {job.title}
          </div>
          <div style={{ fontSize: compact ? '10px' : '13px', color: '#888', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }} title={job.company}>
            {job.company}
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button onClick={(e) => { stopProp(e); onToggleStar(job.id, !isStarred); }} style={{ background: 'transparent', border: 'none', padding: 0, cursor: 'pointer', color: isStarred ? 'gold' : '#333', transition: 'color 0.2s' }}>
                <Star size={16} fill={isStarred ? "gold" : "none"} />
            </button>
            <div style={{ fontSize: compact ? '14px' : '20px', fontWeight: 'bold', color: 'var(--accent)', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px', height: 'fit-content' }}>
              {job.score}
            </div>
        </div>
      </div>

      {/* METADATA BADGES */}
      <div style={{ display: 'flex', gap: '5px', marginBottom: '8px', flexWrap: 'wrap' }}>
        {salaryString && (
           <span style={{ background: 'rgba(0, 255, 157, 0.1)', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '2px 5px', borderRadius: '3px', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '3px' }}>
              <DollarSign size={10} /> {salaryString}
           </span>
        )}
        
        {hasClearance && (
           <span style={{ background: 'rgba(255, 0, 85, 0.1)', color: 'var(--danger)', border: '1px solid var(--danger)', padding: '2px 5px', borderRadius: '3px', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '3px' }}>
              <ShieldAlert size={10} /> {job.clearance_required.toUpperCase()}
           </span>
        )}
        
        {renderDistanceBadge()}
        
        {!compact && <span style={{ background: '#222', color: '#aaa', border: '1px solid #444', padding: '2px 4px', borderRadius: '3px', fontSize: '9px', display:'flex', alignItems:'center', gap:'3px' }}><Clock size={9}/> {timeAgo}</span>}
      </div>

      {/* TECH STACK PILLS */}
      {!compact && techStack.length > 0 && (
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginBottom: '8px' }}>
              {techStack.slice(0, 4).map((tech, i) => (
                  <span key={i} style={{ fontSize: '9px', background: '#111', color: '#888', border: '1px solid #333', padding: '1px 4px', borderRadius: '2px' }}>
                      {tech}
                  </span>
              ))}
              {techStack.length > 4 && <span style={{ fontSize: '9px', color: '#666' }}>+{techStack.length - 4}</span>}
          </div>
      )}

      {/* ACTION BAR */}
      <div style={{ marginTop: 'auto', display: 'flex', gap: '4px' }} onClick={stopProp}>
        <a href={job.url} target="_blank" style={{ flex: 1, background: '#111', color: '#fff', border: '1px solid #444', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}>
          <ExternalLink size={12} />
        </a>

        {scriptContent && (
          <button onClick={handleCopy} style={{ flex: 1, background: copied ? 'var(--accent)' : '#111', color: copied ? '#000' : 'var(--accent)', border: '1px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px', transition: 'all 0.2s' }}>
            <Copy size={12} />
          </button>
        )}

        {job.status === 'TARGET' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} title="Mark Applied" style={{ background: '#111', border: '1px solid var(--applied)', color: 'var(--applied)', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><Check size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'REJECTED')} title="Reject" style={{ background: '#111', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><X size={14} /></button>
            </>
        )}
        {job.status === 'APPLIED' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'TARGET')} title="Undo" style={{ background: '#111', border: '1px solid #444', color: '#666', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><RotateCcw size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'INTERVIEW')} title="Mark Interview" style={{ background: '#111', border: '1px solid var(--interview)', color: 'var(--interview)', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><Mic size={14} /></button>
            </>
        )}
        {job.status === 'INTERVIEW' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} title="Undo" style={{ background: '#111', border: '1px solid #444', color: '#666', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><RotateCcw size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'OFFER')} title="Mark Offer" style={{ background: '#111', border: '1px solid #fff', color: '#fff', padding: '6px', borderRadius: '3px', transition: 'background 0.2s' }}><ArrowRight size={14} /></button>
            </>
        )}
        {job.status === 'REJECTED' && (
            <button onClick={() => onUpdateStatus(job.id, 'TARGET')} title="Restore" style={{ flexGrow: 1, background: '#111', border: '1px solid #444', color: '#fff', padding: '6px', borderRadius: '3px', display:'flex', justifyContent:'center', gap:'5px', alignItems:'center', transition: 'background 0.2s' }}>
                <RotateCcw size={14} /> RESTORE
            </button>
        )}
      </div>
    </div>
  );
};

export default React.memo(JobCard, (prev, next) => {
    return prev.job.id === next.job.id && 
           prev.job.status === next.job.status && 
           prev.job.starred === next.job.starred && 
           prev.job.score === next.job.score && 
           prev.job.salary_base_min === next.job.salary_base_min &&
           prev.job.found_at === next.job.found_at;
});