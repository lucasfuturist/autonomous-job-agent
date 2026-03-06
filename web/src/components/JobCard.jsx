import React, { useState } from 'react';
import { ExternalLink, Copy, Check, X, Mic, ArrowRight, RotateCcw, Star } from 'lucide-react';

const JobCard = ({ job, onUpdateStatus, onToggleStar, onClick, compact = false }) => {
  const [showScript, setShowScript] = useState(false);
  const [copied, setCopied] = useState(false);

  const parts = (job.reason || "").split("### DEPLOYMENT SCRIPT:");
  const scriptContent = parts.length > 1 ? parts[1].trim() : null;

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
        fontSize: compact ? '11px' : '13px', cursor: 'pointer', transition: 'transform 0.1s'
      }}
      className="job-card-hover"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <div style={{ overflow: 'hidden', flexGrow: 1 }}>
          {/* PRIMARY: JOB TITLE */}
          <div style={{ fontSize: compact ? '13px' : '16px', fontWeight: 'bold', color: '#fff', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }} title={job.title}>
            {job.title}
          </div>
          {/* SUBTITLE: COMPANY */}
          <div style={{ fontSize: compact ? '10px' : '13px', color: '#888', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }} title={job.company}>
            {job.company}
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button onClick={(e) => { stopProp(e); onToggleStar(job.id, !isStarred); }} style={{ background: 'transparent', border: 'none', padding: 0, cursor: 'pointer', color: isStarred ? 'gold' : '#333' }}>
                <Star size={16} fill={isStarred ? "gold" : "none"} />
            </button>
            <div style={{ fontSize: compact ? '14px' : '20px', fontWeight: 'bold', color: 'var(--accent)', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px', height: 'fit-content' }}>
              {job.score}
            </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '5px', marginBottom: '8px', flexWrap: 'wrap' }}>
        {!compact && <span style={{ background: 'var(--accent-dim)', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>{job.selected_resume}</span>}
        <span style={{ border: '1px solid #333', color: '#888', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>{job.location}</span>
        {renderDistanceBadge()}
      </div>

      <div style={{ marginTop: 'auto', display: 'flex', gap: '4px' }} onClick={stopProp}>
        <a href={job.url} target="_blank" style={{ flex: 1, background: '#111', color: '#fff', border: '1px solid #444', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px' }}>
          <ExternalLink size={12} />
        </a>

        {scriptContent && (
          <button onClick={handleCopy} style={{ flex: 1, background: copied ? 'var(--accent)' : '#111', color: copied ? '#000' : 'var(--accent)', border: '1px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px' }}>
            <Copy size={12} />
          </button>
        )}

        {job.status === 'TARGET' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} title="Mark Applied" style={{ background: '#111', border: '1px solid var(--applied)', color: 'var(--applied)', padding: '6px', borderRadius: '3px' }}><Check size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'REJECTED')} title="Reject" style={{ background: '#111', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '6px', borderRadius: '3px' }}><X size={14} /></button>
            </>
        )}
        {job.status === 'APPLIED' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'TARGET')} title="Undo" style={{ background: '#111', border: '1px solid #444', color: '#666', padding: '6px', borderRadius: '3px' }}><RotateCcw size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'INTERVIEW')} title="Mark Interview" style={{ background: '#111', border: '1px solid var(--interview)', color: 'var(--interview)', padding: '6px', borderRadius: '3px' }}><Mic size={14} /></button>
            </>
        )}
        {job.status === 'INTERVIEW' && (
            <>
                <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} title="Undo" style={{ background: '#111', border: '1px solid #444', color: '#666', padding: '6px', borderRadius: '3px' }}><RotateCcw size={14} /></button>
                <button onClick={() => onUpdateStatus(job.id, 'OFFER')} title="Mark Offer" style={{ background: '#111', border: '1px solid #fff', color: '#fff', padding: '6px', borderRadius: '3px' }}><ArrowRight size={14} /></button>
            </>
        )}
        {job.status === 'REJECTED' && (
            <button onClick={() => onUpdateStatus(job.id, 'TARGET')} title="Restore" style={{ flexGrow: 1, background: '#111', border: '1px solid #444', color: '#fff', padding: '6px', borderRadius: '3px', display:'flex', justifyContent:'center', gap:'5px', alignItems:'center' }}>
                <RotateCcw size={14} /> RESTORE
            </button>
        )}
      </div>
    </div>
  );
};

export default React.memo(JobCard, (prev, next) => {
    return prev.job.id === next.job.id && prev.job.status === next.job.status && prev.job.starred === next.job.starred && prev.job.score === next.job.score && prev.job.distance === next.job.distance;
});