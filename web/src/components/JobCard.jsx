import React, { useState } from 'react';
import { ExternalLink, Copy, Check, X, Mic, FileText, ArrowRight } from 'lucide-react';

export default function JobCard({ job, onUpdateStatus, compact = false }) {
  const [showScript, setShowScript] = useState(false);
  const [copied, setCopied] = useState(false);

  const parts = (job.reason || "").split("### DEPLOYMENT SCRIPT:");
  const reasonText = parts[0].trim();
  const scriptContent = parts.length > 1 ? parts[1].trim() : null;

  const handleCopy = () => {
    navigator.clipboard.writeText(scriptContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Status Styling
  let borderStyle = '3px solid var(--accent)';
  let bgStyle = 'var(--card-bg)';
  if (job.status === 'APPLIED') { borderStyle = '3px solid var(--applied)'; }
  else if (job.status === 'INTERVIEW') { borderStyle = '3px solid var(--interview)'; bgStyle = '#050a10'; }
  else if (job.status === 'OFFER') { borderStyle = '3px solid #fff'; }

  return (
    <div style={{ 
      background: bgStyle, border: '1px solid #222', borderLeft: borderStyle, 
      padding: '10px', display: 'flex', flexDirection: 'column', position: 'relative',
      fontSize: compact ? '11px' : '13px'
    }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <div style={{ overflow: 'hidden' }}>
          <div style={{ fontSize: compact ? '13px' : '16px', fontWeight: 'bold', color: '#fff', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{job.company}</div>
          <div style={{ fontSize: compact ? '10px' : '13px', color: '#888', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{job.title}</div>
        </div>
        <div style={{ 
          fontSize: compact ? '14px' : '20px', fontWeight: 'bold', color: 'var(--accent)', 
          background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px', height: 'fit-content' 
        }}>
          {job.score}
        </div>
      </div>

      {/* Meta */}
      <div style={{ display: 'flex', gap: '5px', marginBottom: '8px', flexWrap: 'wrap' }}>
        {!compact && <span style={{ background: 'var(--accent-dim)', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>{job.selected_resume}</span>}
        <span style={{ border: '1px solid #333', color: '#888', padding: '2px 4px', borderRadius: '3px', fontSize: '9px' }}>{job.location}</span>
      </div>

      {/* Script Box (Hidden in Compact unless toggled) */}
      {showScript && scriptContent && (
        <textarea readOnly value={scriptContent} onClick={(e) => e.target.select()} style={{ width: '100%', height: '60px', background: '#080808', color: '#777', border: '1px solid #333', marginBottom: '10px' }} />
      )}

      {/* Actions */}
      <div style={{ marginTop: 'auto', display: 'flex', gap: '4px' }}>
        <a href={job.url} target="_blank" style={{ flex: 1, background: '#111', color: '#fff', border: '1px solid #444', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px' }}>
          <ExternalLink size={12} />
        </a>

        {scriptContent && (
          <button onClick={handleCopy} style={{ flex: 1, background: copied ? 'var(--accent)' : '#111', color: copied ? '#000' : 'var(--accent)', border: '1px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '6px', borderRadius: '3px' }}>
            <Copy size={12} />
          </button>
        )}

        {/* Workflow Buttons */}
        {job.status === 'TARGET' && <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} title="Applied" style={{ background: '#111', border: '1px solid var(--applied)', color: 'var(--applied)', padding: '6px', borderRadius: '3px' }}><Check size={14} /></button>}
        
        {job.status === 'APPLIED' && <button onClick={() => onUpdateStatus(job.id, 'INTERVIEW')} title="Interview" style={{ background: '#111', border: '1px solid var(--interview)', color: 'var(--interview)', padding: '6px', borderRadius: '3px' }}><Mic size={14} /></button>}
        
        {job.status === 'INTERVIEW' && <button onClick={() => onUpdateStatus(job.id, 'OFFER')} title="Offer" style={{ background: '#111', border: '1px solid #fff', color: '#fff', padding: '6px', borderRadius: '3px' }}><ArrowRight size={14} /></button>}

        <button onClick={() => onUpdateStatus(job.id, 'REJECTED')} title="Reject" style={{ background: '#111', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '6px', borderRadius: '3px' }}><X size={14} /></button>
      </div>
    </div>
  );
}