import React, { useState, useEffect } from 'react';
import { ExternalLink, Copy, Check, X, Mic, ArrowRight, RotateCcw, Star, Calendar, MapPin, FileText, BrainCircuit } from 'lucide-react';

export default function JobModal({ job, onClose, onUpdateStatus, onToggleStar }) {
  const [copied, setCopied] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!job) return null;

  // Parse AI Reason vs Script
  const parts = (job.reason || "").split("### DEPLOYMENT SCRIPT:");
  const reasonText = parts[0].trim();
  const scriptContent = parts.length > 1 ? parts[1].trim() : null;

  const handleCopy = () => {
    navigator.clipboard.writeText(scriptContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isStarred = job.starred === 1 || job.starred === true;

  // Status Styling
  let statusColor = 'var(--accent)';
  if (job.status === 'APPLIED') statusColor = 'var(--applied)';
  if (job.status === 'INTERVIEW') statusColor = 'var(--interview)';
  if (job.status === 'REJECTED') statusColor = 'var(--danger)';

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(5px)',
      zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center',
      padding: '20px'
    }} onClick={onClose}>
      
      <div style={{
        backgroundColor: '#0a0a0a', border: '1px solid #333',
        width: '100%', maxWidth: '900px', height: '90vh',
        display: 'flex', flexDirection: 'column', borderRadius: '8px',
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)', overflow: 'hidden'
      }} onClick={e => e.stopPropagation()}>

        {/* --- HEADER --- */}
        <div style={{ padding: '20px', borderBottom: '1px solid #222', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', background: '#111' }}>
          <div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff', marginBottom: '5px' }}>{job.company}</div>
            <div style={{ fontSize: '16px', color: '#aaa' }}>{job.title}</div>
            
            <div style={{ display: 'flex', gap: '15px', marginTop: '10px', fontSize: '12px', color: '#666' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><MapPin size={12}/> {job.location}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Calendar size={12}/> Found: {new Date(job.found_at).toLocaleDateString()}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><FileText size={12}/> Resume: {job.selected_resume}</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: statusColor, lineHeight: 1 }}>{job.score}</div>
            <button 
                onClick={() => onToggleStar(job.id, !isStarred)}
                style={{ background: 'transparent', border: '1px solid #333', padding: '5px 10px', cursor: 'pointer', color: isStarred ? 'gold' : '#666', borderRadius: '4px', display: 'flex', gap: '5px', alignItems: 'center', fontSize: '12px' }}
            >
                <Star size={14} fill={isStarred ? "gold" : "none"} /> {isStarred ? "STARRED" : "STAR"}
            </button>
          </div>
        </div>

        {/* --- SCROLLABLE BODY --- */}
        <div style={{ flexGrow: 1, overflowY: 'auto', padding: '25px', display: 'flex', flexDirection: 'column', gap: '25px' }}>
            
            {/* AI ANALYSIS */}
            <div style={{ background: '#111', border: '1px solid #222', borderRadius: '6px', padding: '15px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px', color: statusColor, fontWeight: 'bold', fontSize: '12px' }}>
                    <BrainCircuit size={16} />
                    AI STRATEGY ANALYSIS
                </div>
                <div style={{ color: '#ddd', fontSize: '14px', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                    {reasonText}
                </div>
            </div>

            {/* SCRIPT (IF EXISTS) */}
            {scriptContent && (
                 <div style={{ background: '#080808', border: '1px solid #333', borderRadius: '6px', overflow: 'hidden' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 15px', background: '#151515', borderBottom: '1px solid #333' }}>
                        <span style={{ fontSize: '11px', color: '#666', fontWeight: 'bold' }}>POWERSHELL DEPLOYMENT</span>
                        <button onClick={handleCopy} style={{ background: 'transparent', border: 'none', color: copied ? 'var(--accent)' : '#666', cursor: 'pointer', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                            {copied ? "COPIED" : "COPY SCRIPT"} <Copy size={12} />
                        </button>
                    </div>
                    <textarea 
                        readOnly 
                        value={scriptContent} 
                        style={{ width: '100%', height: '80px', background: 'transparent', border: 'none', color: '#888', padding: '15px', fontFamily: 'monospace', fontSize: '12px', resize: 'none' }} 
                    />
                 </div>
            )}

            {/* JOB DESCRIPTION */}
            <div>
                <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff', marginBottom: '15px', borderBottom: '1px solid #222', paddingBottom: '10px' }}>JOB DESCRIPTION</div>
                <div 
                    style={{ color: '#aaa', fontSize: '13px', lineHeight: '1.6' }}
                    dangerouslySetInnerHTML={{ __html: job.description }} 
                />
            </div>
        </div>

        {/* --- FOOTER ACTIONS --- */}
        <div style={{ padding: '20px', borderTop: '1px solid #222', background: '#111', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <a href={job.url} target="_blank" style={{ textDecoration: 'none', color: '#fff', border: '1px solid #444', padding: '10px 20px', borderRadius: '4px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', background: '#000' }}>
                OPEN ORIGINAL <ExternalLink size={14} />
            </a>

            <div style={{ display: 'flex', gap: '10px' }}>
                 {/* Workflow Buttons - TARGET */}
                {job.status === 'TARGET' && (
                    <>
                        <button onClick={() => { onUpdateStatus(job.id, 'REJECTED'); onClose(); }} style={{ background: '#220000', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '10px 20px', borderRadius: '4px', fontWeight: 'bold' }}>REJECT</button>
                        <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} style={{ background: 'var(--applied)', border: 'none', color: '#fff', padding: '10px 30px', borderRadius: '4px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            MARK APPLIED <Check size={16} />
                        </button>
                    </>
                )}
                
                {/* Workflow Buttons - APPLIED */}
                {job.status === 'APPLIED' && (
                    <>
                        <button onClick={() => onUpdateStatus(job.id, 'TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#888', padding: '10px 20px', borderRadius: '4px' }}>UNDO</button>
                        <button onClick={() => onUpdateStatus(job.id, 'INTERVIEW')} style={{ background: 'var(--interview)', border: 'none', color: '#000', padding: '10px 30px', borderRadius: '4px', fontWeight: 'bold' }}>INTERVIEW</button>
                    </>
                )}

                 {/* Workflow Buttons - REJECTED */}
                 {job.status === 'REJECTED' && (
                    <button onClick={() => onUpdateStatus(job.id, 'TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '10px 20px', borderRadius: '4px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <RotateCcw size={14} /> RESTORE TO TARGET
                    </button>
                )}
            </div>
        </div>

      </div>
    </div>
  );
}