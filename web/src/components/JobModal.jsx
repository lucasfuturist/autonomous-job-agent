import React, { useState, useEffect, useRef } from 'react';
import { ExternalLink, Copy, Check, X, Mic, ArrowRight, RotateCcw, Star, Calendar, MapPin, FileText, BrainCircuit, User } from 'lucide-react';

export default function JobModal({ job, onClose, onUpdateStatus, onToggleStar }) {
  const [copied, setCopied] = useState(false);
  const [resumeContent, setResumeContent] = useState("Loading resume...");
  
  // Resizable Panes State (Percentages)
  const containerRef = useRef(null);
  const [leftWidth, setLeftWidth] = useState(40);
  const [centerWidth, setCenterWidth] = useState(30);

  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  // Fetch Resume Content
  useEffect(() => {
    if (job?.selected_resume) {
        setResumeContent("Loading...");
        fetch(`/api/resume?name=${encodeURIComponent(job.selected_resume)}`)
            .then(res => res.json())
            .then(data => setResumeContent(data.content))
            .catch(err => setResumeContent("Failed to load resume."));
    }
  }, [job]);

  if (!job) return null;

  // --- PARSERS & FORMATTERS ---
  const parts = (job.reason || "").split("### DEPLOYMENT SCRIPT:");
  const reasonText = parts[0].trim();
  const scriptContent = parts.length > 1 ? parts[1].trim() : null;

  // Enforce Max 1 Blank Line (2 consecutive line breaks) for Job Description
  const formatText = (text) => {
    if (!text) return { __html: "" };
    let str = text;
    // 1. Collapse 3+ HTML breaks into exactly 2
    str = str.replace(/(?:<br\s*\/?>\s*){3,}/gi, '<br/><br/>');
    // 2. Collapse 3+ literal newlines into exactly 2
    str = str.replace(/(?:\r?\n\s*){3,}/g, '\n\n');
    // 3. Apply markdown bolding
    str = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 4. If the text is raw string (no block HTML), convert standard newlines to BRs for web render
    if (!str.includes('<p>') && !str.includes('<li>')) {
        str = str.replace(/\n/g, '<br/>');
    }
    return { __html: str };
  };

  // Enforce Max 1 Blank Line for Resume/Markdown
  const formatResume = (text) => {
    if (!text) return "";
    return text.replace(/(?:\r?\n\s*){3,}/g, '\n\n');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(scriptContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // --- RESIZE LOGIC ---
  const handleDragStart = (splitterIndex) => (mouseDownEvent) => {
    mouseDownEvent.preventDefault();
    const container = containerRef.current;
    if (!container) return;

    const bounds = container.getBoundingClientRect();
    document.body.style.userSelect = 'none'; // Prevent text selection while dragging
    document.body.style.cursor = 'col-resize';

    const handleDrag = (mouseMoveEvent) => {
        const percent = ((mouseMoveEvent.clientX - bounds.left) / bounds.width) * 100;
        
        if (splitterIndex === 1) {
            // Adjust Left Pane. Min 15%, Max leaves at least 15% for center + 15% for right
            const newLeft = Math.min(Math.max(percent, 15), 100 - centerWidth - 15);
            setLeftWidth(newLeft);
        } else if (splitterIndex === 2) {
            // Adjust Center Pane. Percent here represents (Left + Center) position.
            const newCenter = Math.min(Math.max(percent - leftWidth, 15), 100 - leftWidth - 15);
            setCenterWidth(newCenter);
        }
    };

    const handleMouseUp = () => {
        document.removeEventListener('mousemove', handleDrag);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
    };

    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const isStarred = job.starred === 1 || job.starred === true;

  // Status Styling
  let statusColor = 'var(--accent)';
  if (job.status === 'APPLIED') statusColor = 'var(--applied)';
  if (job.status === 'INTERVIEW') statusColor = 'var(--interview)';
  if (job.status === 'REJECTED') statusColor = 'var(--danger)';

  // Splitter Component Style
  const splitterStyle = {
      width: '8px',
      margin: '0 -4px',
      cursor: 'col-resize',
      zIndex: 10,
      background: 'transparent',
      transition: 'background 0.2s',
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.95)', backdropFilter: 'blur(5px)',
      zIndex: 1000, display: 'flex', flexDirection: 'column',
      padding: '20px'
    }} onClick={onClose}>
      
      {/* --- TOP BAR --- */}
      <div style={{ 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
          marginBottom: '15px', background: '#0a0a0a', padding: '15px', 
          borderRadius: '8px', border: '1px solid #222' 
      }} onClick={e => e.stopPropagation()}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
             <div style={{ background: statusColor, color: '#000', fontWeight: 'bold', padding: '5px 10px', borderRadius: '4px', fontSize: '12px' }}>
                 {job.status}
             </div>
             <div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff' }}>{job.company}</div>
                <div style={{ fontSize: '14px', color: '#aaa' }}>{job.title}</div>
             </div>
             <div style={{ height: '30px', width: '1px', background: '#333' }}></div>
             <div style={{ display: 'flex', gap: '15px', fontSize: '12px', color: '#666' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><MapPin size={12}/> {job.location}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Calendar size={12}/> {new Date(job.found_at).toLocaleDateString()}</div>
             </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: statusColor }}>{job.score}</div>
            <button 
                onClick={() => onToggleStar(job.id, !isStarred)}
                style={{ background: 'transparent', border: '1px solid #333', padding: '8px', cursor: 'pointer', color: isStarred ? 'gold' : '#666', borderRadius: '4px' }}
            >
                <Star size={18} fill={isStarred ? "gold" : "none"} />
            </button>
            <button onClick={onClose} style={{ background: '#222', border: 'none', color: '#fff', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
                ESC
            </button>
          </div>
      </div>

      {/* --- 3-PANE FLEX CONTAINER --- */}
      <div 
        ref={containerRef}
        style={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }} 
        onClick={e => e.stopPropagation()}
      >
        
        {/* PANE 1: TARGET (Job Description) */}
        <div style={{ width: `calc(${leftWidth}% - 4px)`, background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: '#aaa', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={14} /> TARGET INTEL (DESCRIPTION)
            </div>
            <div style={{ padding: '20px', overflowY: 'auto', color: '#ccc', fontSize: '13px', lineHeight: '1.6' }}>
                <div dangerouslySetInnerHTML={formatText(job.description)} />
            </div>
        </div>

        {/* SPLITTER 1 */}
        <div 
            style={splitterStyle} 
            onMouseDown={handleDragStart(1)}
            onMouseOver={(e) => e.target.style.background = '#333'}
            onMouseOut={(e) => e.target.style.background = 'transparent'}
        />

        {/* PANE 2: STRATEGY (AI Analysis & Script) */}
        <div style={{ width: `calc(${centerWidth}% - 8px)`, background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BrainCircuit size={14} /> TACTICAL ANALYSIS
            </div>
            <div style={{ padding: '20px', overflowY: 'auto', flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
                
                <div style={{ fontSize: '14px', lineHeight: '1.5', color: '#eee', whiteSpace: 'pre-wrap' }}>
                    {formatResume(reasonText)}
                </div>

                {scriptContent && (
                    <div style={{ marginTop: 'auto', background: '#050505', border: '1px solid #333', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: '#151515', borderBottom: '1px solid #333' }}>
                            <span style={{ fontSize: '10px', color: '#666', fontWeight: 'bold' }}>POWERSHELL LOADOUT</span>
                            <button onClick={handleCopy} style={{ background: 'transparent', border: 'none', color: copied ? 'var(--accent)' : '#666', cursor: 'pointer', fontSize: '10px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                {copied ? "COPIED" : "COPY"} <Copy size={10} />
                            </button>
                        </div>
                        <textarea 
                            readOnly 
                            value={scriptContent} 
                            style={{ width: '100%', height: '100px', background: 'transparent', border: 'none', color: '#666', padding: '10px', fontFamily: 'monospace', fontSize: '11px', resize: 'none', boxSizing: 'border-box' }} 
                        />
                    </div>
                )}
            </div>
             {/* FOOTER ACTIONS (Inside Center Pane for focus) */}
            <div style={{ padding: '15px', borderTop: '1px solid #222', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <a href={job.url} target="_blank" style={{ textDecoration: 'none', textAlign: 'center', color: '#fff', border: '1px solid #444', padding: '8px', borderRadius: '4px', fontSize: '12px', background: '#111', display: 'flex', justifyContent: 'center', gap: '8px' }}>
                    OPEN ORIGINAL SOURCE <ExternalLink size={14} />
                </a>

                 {job.status === 'TARGET' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                        <button onClick={() => { onUpdateStatus(job.id, 'REJECTED'); onClose(); }} style={{ background: '#220000', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer' }}>REJECT</button>
                        <button onClick={() => onUpdateStatus(job.id, 'APPLIED')} style={{ background: 'var(--applied)', border: 'none', color: '#fff', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                            MARK APPLIED <Check size={14} />
                        </button>
                    </div>
                )}
                 {job.status === 'APPLIED' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                        <button onClick={() => onUpdateStatus(job.id, 'TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#888', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer' }}>UNDO</button>
                        <button onClick={() => onUpdateStatus(job.id, 'INTERVIEW')} style={{ background: 'var(--interview)', border: 'none', color: '#000', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer' }}>MARK INTERVIEW</button>
                    </div>
                )}
                {job.status === 'REJECTED' && (
                    <button onClick={() => onUpdateStatus(job.id, 'TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        RESTORE TO TARGET <RotateCcw size={14} />
                    </button>
                )}
            </div>
        </div>

        {/* SPLITTER 2 */}
        <div 
            style={splitterStyle} 
            onMouseDown={handleDragStart(2)}
            onMouseOver={(e) => e.target.style.background = '#333'}
            onMouseOut={(e) => e.target.style.background = 'transparent'}
        />

        {/* PANE 3: ASSET (Resume) */}
        <div style={{ flexGrow: 1, background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: '#aaa', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <User size={14} /> ACTIVE ASSET ({job.selected_resume})
            </div>
            <div style={{ padding: '20px', overflowY: 'auto', color: '#888', fontSize: '11px', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {formatResume(resumeContent)}
            </div>
        </div>

      </div>
    </div>
  );
}