import React, { useState, useEffect, useRef, useMemo } from 'react';
import { ExternalLink, Check, X, Mic, ArrowRight, RotateCcw, Star, Calendar, MapPin, FileText, BrainCircuit, User, Link, FileDown, ChevronLeft, ChevronRight, Navigation, FileCheck, Edit, Save, XCircle, RefreshCw, AlertTriangle, Cpu, PenTool, DollarSign, Lock, FilePlus, Users, ScanSearch, CheckCircle2, Mail, Plus, Copy, Zap, Eye, PenLine } from 'lucide-react';

export default function JobModal({ job, onClose, onUpdateStatus, onToggleStar, onNext, onPrev }) {
  const [localJob, setLocalJob] = useState(job);
  
  const [urlCopied, setUrlCopied] = useState(false);
  const [msgCopied, setMsgCopied] = useState(false);
  const [descCopied, setDescCopied] = useState(false);
  const [resumeCopied, setResumeCopied] = useState(false);
  const [resumeContent, setResumeContent] = useState("Loading...");
  
  const [deploying, setDeploying] = useState(false);
  const [deployed, setDeployed] = useState(false);
  
  const [regenerating, setRegenerating] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  
  // EDIT MODES
  const [isEditingResume, setIsEditingResume] = useState(false);
  const [resumeEditContent, setResumeEditContent] = useState("");
  
  const [isEditingDesc, setIsEditingDesc] = useState(false);
  const [descEditContent, setDescEditContent] = useState("");
  
  // RECRUITER STATE - Updated to match CRM Schema
  const [recruiters, setRecruiters] = useState([]);
  const [newContact, setNewContact] = useState({ 
      name: '', title: '', url: '', email: '', phone: '', message_sent: '', history: '', contact_dates: [], replied: false 
  });
  
  // OUTREACH MSG STATE
  const [outreachMsg, setOutreachMsg] = useState("");
  const [generatingMsg, setGeneratingMsg] = useState(false);
  
  const containerRef = useRef(null);
  const [leftWidth, setLeftWidth] = useState(40);
  const [centerWidth, setCenterWidth] = useState(30);

  // MAPPING RATIONALE STATE
  const [mappingRationale, setMappingRationale] = useState("");

  // Sync prop job to local state
  useEffect(() => {
    setLocalJob(job);
  }, [job]);

  const isStarred = localJob?.starred === 1 || localJob?.starred === true;
  const hasResume = localJob?.selected_resume && localJob.selected_resume !== "" && localJob.selected_resume !== "None";

  // --- ENRICHED DATA PARSING ---
  const techStack = useMemo(() => {
    try { return localJob?.tech_stack_core ? JSON.parse(localJob.tech_stack_core) :[]; } catch { return []; }
  }, [localJob?.tech_stack_core]);

  const hardwareStack = useMemo(() => {
    try { return localJob?.hardware_physical_tools ? JSON.parse(localJob.hardware_physical_tools) : []; } catch { return []; }
  },[localJob?.hardware_physical_tools]);

  const redFlags = useMemo(() => {
    try { return localJob?.red_flags ? JSON.parse(localJob.red_flags) : []; } catch { return []; }
  },[localJob?.red_flags]);

  const salaryString = useMemo(() => {
    if (!localJob?.salary_base_min && !localJob?.salary_base_max) return null;
    const fmt = (n) => n >= 1000 ? `$${Math.round(n/1000)}k` : `$${n}`;
    if (localJob.salary_base_min && localJob.salary_base_max) return `${fmt(localJob.salary_base_min)} - ${fmt(localJob.salary_base_max)}`;
    return fmt(localJob.salary_base_min || localJob.salary_base_max) + "+";
  },[localJob?.salary_base_min, localJob?.salary_base_max]);


  // --- ACTION HANDLERS ---
  const handleTriageAction = React.useCallback((status) => {
      if (onNext) onNext(); else onClose(); 
      if (localJob?.id) onUpdateStatus(localJob.id, status);        
  },[localJob?.id, onNext, onClose, onUpdateStatus]);

  const handleCorrection = (status) => {
      if (localJob?.id) onUpdateStatus(localJob.id, status);
  };

  // --- KEYBOARD SHORTCUTS ---
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!localJob) return;
      if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
      
      const key = e.key.toLowerCase();
      
      if (key === 'escape') onClose();
      if (key === 'arrowright' && onNext) onNext();
      if (key === 'arrowleft' && onPrev) onPrev();
      
      if (key === 'x' && localJob.status === 'TARGET') handleTriageAction('REJECTED');
      if (key === 'a' && localJob.status === 'TARGET') handleTriageAction('APPLIED');
      if (key === 's') onToggleStar(localJob.id, !isStarred);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  },[localJob, onClose, onNext, onPrev, onToggleStar, isStarred, handleTriageAction]);

  // --- 1. RESUME EFFECT (Separated to prevent re-fetching on recruiter updates) ---
  useEffect(() => {
    if (!localJob) return;

    if (hasResume) {
        setResumeContent("Loading...");
        setIsEditingResume(false); 
        fetch(`/api/resume?name=${encodeURIComponent(localJob.selected_resume)}`)
            .then(res => res.json())
            .then(data => setResumeContent(data.content))
            .catch(err => setResumeContent("Failed to load resume."));
    } else {
        setResumeContent(null);
    }
    setIsEditingDesc(false);
  }, [localJob?.id, localJob?.selected_resume, hasResume]);

  // --- 2. INTEL & RECRUITERS EFFECT (Syncs on polling update) ---
  useEffect(() => {
    if (!localJob) return;
    
    // Sync local state with DB
    setOutreachMsg(localJob?.outreach_message || "");
    setMappingRationale(localJob?.resume_rationale || ""); 
    
    if (localJob?.recruiters) {
        try { setRecruiters(JSON.parse(localJob.recruiters)); } catch(e) { setRecruiters([]); }
    } else if (localJob?.company) {
        setRecruiters([]);
        fetch(`/api/recruiters?company=${encodeURIComponent(localJob.company)}`)
            .then(res => res.json())
            .then(data => { if(data.recruiters) setRecruiters(data.recruiters); })
            .catch(e => console.error(e));
    }
  }, [localJob?.id, localJob?.recruiters, localJob?.outreach_message, localJob?.resume_rationale]); 


  // --- COPY HANDLERS ---
  const handleCopyDesc = () => {
      if (!localJob?.description) return;
      navigator.clipboard.writeText(localJob.description);
      setDescCopied(true);
      setTimeout(() => setDescCopied(false), 2000);
  };

  const handleCopyResume = () => {
      if (!resumeContent || resumeContent === "Loading...") return;
      navigator.clipboard.writeText(resumeContent);
      setResumeCopied(true);
      setTimeout(() => setResumeCopied(false), 2000);
  };

  const copyOutreachMessage = () => {
      navigator.clipboard.writeText(outreachMsg);
      setMsgCopied(true);
      setTimeout(() => setMsgCopied(false), 2000);
  };

  // --- ROBUST MSG GEN ---
  const handleGenerateOutreach = async () => {
    if (generatingMsg) return;
    setGeneratingMsg(true);
    try {
        const res = await fetch('/api/outreach/generate', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: localJob.id })
        });
        if (!res.ok) throw new Error("Server error");
        const data = await res.json();
        if (data.success) {
            setOutreachMsg(data.message);
            localJob.outreach_message = data.message; 
        }
    } catch (e) {
        console.error("Outreach gen failed:", e);
    } finally {
        setGeneratingMsg(false);
    }
  };

  // --- RESUME LOGIC ---
  const handleRegenerateSummary = async () => {
      if (regenerating) return;
      setRegenerating(true);
      try {
          const res = await fetch('/api/regenerate_summary', {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name: localJob.selected_resume })
          });
          if (res.ok) {
              const data = await res.json();
              setResumeContent(data.content);
          }
      } catch (e) { console.error(e); } finally { setRegenerating(false); }
  };

  const handleRebuildResume = async () => {
    if (rebuilding) return;
    if (!confirm("Fully rebuild this resume? This will overwrite manual edits.")) return;
    setRebuilding(true);
    try {
        const res = await fetch('/api/regenerate_resume', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: localJob.id })
        });
        if (res.ok) {
            const data = await res.json();
            setResumeContent(data.content);
        }
    } catch (e) { console.error(e); } finally { setRebuilding(false); }
  };

  const handleSaveResumeEdit = async () => {
      try {
          const res = await fetch('/api/save_resume', {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name: localJob.selected_resume, content: resumeEditContent })
          });
          if (res.ok) {
              setResumeContent(resumeEditContent);
              setIsEditingResume(false);
          }
      } catch (e) { alert("Error saving resume."); }
  };

  const handleStartDescEdit = () => {
      setDescEditContent(localJob.description || "");
      setIsEditingDesc(true);
  };
  
  const handleSaveDescEdit = async () => {
      setAnalyzing(true);
      try {
          const res = await fetch('/api/intel/update', {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ id: localJob.id, description: descEditContent })
          });
          if (res.ok) {
              const data = await res.json();
              if (data.success && data.job) {
                  setLocalJob(data.job);
                  setIsEditingDesc(false);
              }
          } else { alert("Failed to update description."); }
      } catch (e) { alert("Error saving description."); } finally { setAnalyzing(false); }
  };

  const handleSaveRationale = async () => {
      try {
          await fetch('/api/intel/rationale', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ id: localJob.id, rationale: mappingRationale })
          });
      } catch (e) {
          console.error("Failed to save rationale", e);
      }
  };

  const handleRecruiterRecon = (e) => {
    if (e) e.stopPropagation();
    const query = `site:linkedin.com/in "${localJob.company}" talent OR recruiter OR hiring`;
    const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    window.open(url, '_blank');
  };

  // --- FIXED DUPLICATE GUARD ADD RECRUITER ---
  const handleAddRecruiter = async () => {
      const url = newContact.url?.trim() || "";
      const email = newContact.email?.trim() || "";
      const phone = newContact.phone?.trim() || "";

      if (!url && !email && !phone) return;
      
      const contactToSave = { 
          ...newContact,
          name: newContact.name?.trim() || "Unknown Contact",
          title: newContact.title?.trim() || "Staff",
          url, email, phone, 
          message_sent: newContact.message_sent?.trim() || "",
          contacted: true 
      };
      
      // FRONTEND DUPLICATE CHECK: Prevent optimistic rendering spam
      setRecruiters(prev => {
          const isDup = prev.some(r => (url && r.url === url) || (email && r.email === email));
          if (isDup) return prev;
          return [...prev, contactToSave];
      });
      
      setNewContact({ name: '', title: '', url: '', email: '', phone: '', message_sent: '', history: '', contact_dates: [], replied: false });

      try {
          await fetch('/api/recruiters/add', {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ job_id: localJob.id, contact: contactToSave })
          });
      } catch (e) { console.error("Failed to add contact", e); }
  };

  const handleToggleContact = async (url) => {
    const newRecruiters = recruiters.map(r => {
        if (r.url === url || r.email === url) return { ...r, contacted: !r.contacted };
        return r;
    });
    setRecruiters(newRecruiters);

    try {
        const target = newRecruiters.find(r => r.url === url || r.email === url);
        await fetch('/api/recruiters/status', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: localJob.id, url: url, contacted: target.contacted })
        });
    } catch(e) { console.error("Failed to toggle contact status", e); }
  };

  if (!localJob) return null;

  const reasonText = (localJob.reason || "").trim();

  const formatText = (text) => {
    if (!text) return { __html: "" };
    let str = text;
    str = str.replace(/(?:<br\s*\/?>\s*){3,}/gi, '<br/><br/>');
    str = str.replace(/(?:\r?\n\s*){3,}/g, '\n\n');
    str = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    if (!str.includes('<p>') && !str.includes('<li>')) {
        str = str.replace(/\n/g, '<br/>');
    }
    return { __html: str };
  };

  const formatResume = (text) => {
    if (!text) return "";
    return text.replace(/(?:\r?\n\s*){3,}/g, '\n\n');
  };

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(localJob.url);
    setUrlCopied(true);
    setTimeout(() => setUrlCopied(false), 2000);
  };

  const handleDeploy = async () => {
    if (!localJob.selected_resume) return;
    setDeploying(true);
    try {
        const res = await fetch('/api/deploy', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume: localJob.selected_resume, target_role: localJob.title })
        });
        const data = await res.json();
        
        if (data.success && data.url) {
            setDeployed(true);
            window.open(data.url, '_blank');
        }
        setTimeout(() => setDeployed(false), 5000);
    } catch (e) { console.error("Deploy failed:", e); } finally { setDeploying(false); }
  };

  // --- PRO-GRADE RESIZE LOGIC (REFINED) ---
  const handleDragStart = (splitterIndex) => (mouseDownEvent) => {
    mouseDownEvent.preventDefault();
    const container = containerRef.current;
    if (!container) return;

    const bounds = container.getBoundingClientRect();
    
    // Anchor current positions
    const startX = mouseDownEvent.clientX;
    const startLeft = leftWidth;
    const startCenter = centerWidth;

    document.body.style.userSelect = 'none'; 
    document.body.style.cursor = 'col-resize';

    const handleDrag = (mouseMoveEvent) => {
        const deltaX = mouseMoveEvent.clientX - startX;
        const deltaPercent = (deltaX / bounds.width) * 100;

        if (splitterIndex === 1) {
            // TRADE SPACE: PANE 1 <-> PANE 2
            let newLeft = startLeft + deltaPercent;
            let newCenter = startCenter - deltaPercent;
            
            // Hard limits (2% min width for high-density viewing)
            if (newLeft < 2) {
                newLeft = 2;
                newCenter = startLeft + startCenter - 2;
            } else if (newCenter < 2) {
                newCenter = 2;
                newLeft = startLeft + startCenter - 2;
            }

            setLeftWidth(newLeft);
            setCenterWidth(newCenter);
            
        } else if (splitterIndex === 2) {
            // TRADE SPACE: PANE 2 <-> PANE 3
            let newCenter = startCenter + deltaPercent;
            const rightPaneWidth = 100 - startLeft - newCenter;

            // Constrain Pane 2 and Pane 3 (The Resume Pane)
            if (newCenter < 2) {
                newCenter = 2;
            } else if (rightPaneWidth < 2) {
                // This prevents the Resume pane from getting stuck
                newCenter = 100 - startLeft - 2;
            }

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

  let statusColor = 'var(--accent)';
  if (localJob.status === 'APPLIED') statusColor = 'var(--applied)';
  if (localJob.status === 'INTERVIEW') statusColor = 'var(--interview)';
  if (localJob.status === 'REJECTED') statusColor = 'var(--danger)';

  const splitterStyle = { width: '8px', margin: '0 -4px', cursor: 'col-resize', zIndex: 10, background: 'transparent', transition: 'background 0.2s' };

  const renderModalDistance = () => {
    if (localJob.distance === undefined || localJob.distance === null) return null;
    if (localJob.distance === -1 || localJob.distance === -1.0) return <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Navigation size={12}/> Remote</div>;
    return <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: localJob.distance <= 30 ? 'var(--accent)' : 'inherit' }}><Navigation size={12}/> {Math.round(localJob.distance)} mi from Boston</div>;
  };

  const renderSkeletonResume = () => (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }} className="fade-in">
       <div className="skeleton" style={{ height: '28px', width: '50%', marginBottom: '10px' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '30%', marginBottom: '25px' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '100%' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '95%' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '90%' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '80%', marginBottom: '30px' }}></div>
       <div className="skeleton" style={{ height: '18px', width: '40%', marginBottom: '10px' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '100%' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '85%' }}></div>
       <div className="skeleton" style={{ height: '12px', width: '90%' }}></div>
    </div>
  );

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.95)', backdropFilter: 'blur(5px)',
      zIndex: 1000, display: 'flex', flexDirection: 'column', padding: '20px'
    }} onClick={onClose} className="fade-in">
      
      <div style={{ 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
          marginBottom: '15px', background: '#0a0a0a', padding: '15px', 
          borderRadius: '8px', border: '1px solid #222' 
      }} onClick={e => e.stopPropagation()}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
             <div style={{ background: statusColor, color: '#000', fontWeight: 'bold', padding: '5px 10px', borderRadius: '4px', fontSize: '12px' }}>
                 {localJob.status}
             </div>
             <div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff' }}>{localJob.company}</div>
                <div style={{ fontSize: '14px', color: '#aaa' }}>{localJob.title}</div>
             </div>
             <div style={{ height: '30px', width: '1px', background: '#333' }}></div>
             <div style={{ display: 'flex', gap: '15px', fontSize: '12px', color: '#666' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><MapPin size={12}/> {localJob.location}</div>
                {renderModalDistance()}
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Calendar size={12}/> {new Date(localJob.found_at).toLocaleDateString()}</div>
             </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: statusColor, marginRight: '10px' }}>{localJob.score}</div>
            
            <button onClick={() => onToggleStar(localJob.id, !isStarred)} style={{ background: 'transparent', border: '1px solid #333', padding: '8px', cursor: 'pointer', color: isStarred ? 'gold' : '#666', borderRadius: '4px', transition: 'color 0.2s' }} title="Star (S)">
                <Star size={18} fill={isStarred ? "gold" : "none"} />
            </button>
            
            <div style={{ display: 'flex', background: '#111', border: '1px solid #333', borderRadius: '4px', overflow: 'hidden', marginLeft: '10px' }}>
                <button onClick={onPrev} disabled={!onPrev} style={{ background: 'transparent', border: 'none', color: '#fff', padding: '8px', cursor: onPrev ? 'pointer' : 'not-allowed', opacity: onPrev ? 1 : 0.3, transition: 'opacity 0.2s' }} title="Previous (Left Arrow)">
                    <ChevronLeft size={18} />
                </button>
                <div style={{ width: '1px', background: '#333' }}></div>
                <button onClick={onNext} disabled={!onNext} style={{ background: 'transparent', border: 'none', color: '#fff', padding: '8px', cursor: onNext ? 'pointer' : 'not-allowed', opacity: onNext ? 1 : 0.3, transition: 'opacity 0.2s' }} title="Next (Right Arrow)">
                    <ChevronRight size={18} />
                </button>
            </div>

            <button onClick={onClose} style={{ background: '#222', border: 'none', color: '#fff', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', marginLeft: '10px', transition: 'background 0.2s' }} title="Close (ESC)">
                ESC
            </button>
          </div>
      </div>

      <div ref={containerRef} style={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }} onClick={e => e.stopPropagation()}>
        
        {/* PANE 1: TARGET */}
        <div style={{ width: `calc(${leftWidth}% - 4px)`, flex: 'none', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: '#aaa', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FileText size={14} /> TARGET INTEL (DESCRIPTION)</div>
                {!isEditingDesc ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={handleCopyDesc} style={{ background: 'transparent', border: 'none', color: descCopied ? 'var(--accent)' : '#666', cursor: 'pointer', transition: 'color 0.2s' }} title="Copy Description">
                            {descCopied ? <Check size={14} /> : <Copy size={14} />}
                        </button>
                        <button onClick={handleStartDescEdit} style={{ background: 'transparent', border: 'none', color: '#666', cursor: 'pointer', transition: 'color 0.2s' }} title="Edit Description">
                            <PenLine size={14} />
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={handleSaveDescEdit} disabled={analyzing} style={{ background: 'var(--accent)', border: 'none', color: '#000', borderRadius: '3px', padding: '2px 8px', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px', cursor: analyzing ? 'wait' : 'pointer' }}>
                             {analyzing ? "ANALYZING..." : "SAVE & RE-ANALYZE"}
                        </button>
                        <button onClick={() => setIsEditingDesc(false)} disabled={analyzing} style={{ background: '#333', border: 'none', color: '#fff', borderRadius: '3px', padding: '2px 8px', fontSize: '10px', cursor: 'pointer' }}>CANCEL</button>
                    </div>
                )}
            </div>
            
            <div style={{ flexGrow: 1, overflowY: 'auto', position: 'relative' }}>
                {isEditingDesc ? (
                     <textarea 
                        value={descEditContent} 
                        onChange={(e) => setDescEditContent(e.target.value)}
                        placeholder="Paste full job description here..."
                        style={{ width: '100%', height: '100%', background: '#050505', color: '#ddd', border: 'none', padding: '20px', fontFamily: 'monospace', fontSize: '12px', resize: 'none', outline: 'none', boxSizing: 'border-box' }} 
                    />
                ) : (
                    <div style={{ padding: '20px', color: '#ccc', fontSize: '13px', lineHeight: '1.6' }}>
                        {localJob.description ? (
                             <div dangerouslySetInnerHTML={formatText(localJob.description)} />
                        ) : (
                             <div style={{ color: '#555', fontStyle: 'italic' }}>No description available. Click edit to paste one.</div>
                        )}
                    </div>
                )}
            </div>
        </div>

        <div style={splitterStyle} onMouseDown={handleDragStart(1)} onMouseOver={(e) => e.target.style.background = '#333'} onMouseOut={(e) => e.target.style.background = 'transparent'} />

        {/* PANE 2: STRATEGY */}
        <div style={{ width: `calc(${centerWidth}% - 8px)`, flex: 'none', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BrainCircuit size={14} /> TACTICAL ANALYSIS
            </div>
            
            <div style={{ padding: '20px', overflowY: 'auto', flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                     <div style={{ background: '#111', border: '1px solid #222', padding: '10px', borderRadius: '4px' }}>
                         <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px', display:'flex', alignItems:'center', gap:'4px' }}><DollarSign size={10} /> COMP RANGE</div>
                         <div style={{ color: salaryString ? 'var(--accent)' : '#444', fontWeight: 'bold' }}>{salaryString || "N/A"}</div>
                     </div>
                     <div style={{ background: '#111', border: '1px solid #222', padding: '10px', borderRadius: '4px' }}>
                         <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px', display:'flex', alignItems:'center', gap:'4px' }}><Lock size={10} /> SECURITY CLEARANCE</div>
                         <div style={{ color: (localJob.clearance_required && localJob.clearance_required !== 'None') ? 'var(--danger)' : '#444', fontWeight: 'bold' }}>{localJob.clearance_required || "None"}</div>
                     </div>
                </div>

                {redFlags.length > 0 && (
                    <div style={{ background: 'rgba(255,0,0,0.1)', border: '1px solid var(--danger)', padding: '10px', borderRadius: '4px' }}>
                        <div style={{ fontSize: '11px', color: 'var(--danger)', fontWeight: 'bold', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}><AlertTriangle size={12} /> RISK ASSESSMENT (RED FLAGS)</div>
                        <ul style={{ margin: 0, paddingLeft: '15px', color: '#faa', fontSize: '12px' }}>{redFlags.map((flag, i) => <li key={i}>{flag}</li>)}</ul>
                    </div>
                )}

                {techStack.length > 0 && (
                    <div style={{ background: '#111', border: '1px solid #222', padding: '10px', borderRadius: '4px' }}>
                        <div style={{ fontSize: '10px', color: '#888', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}><Cpu size={12} /> DETECTED TECH STACK</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {techStack.map((tech, i) => (<span key={i} style={{ background: '#222', color: '#ccc', border: '1px solid #333', padding: '2px 6px', borderRadius: '4px', fontSize: '11px' }}>{tech}</span>))}
                        </div>
                    </div>
                )}

                {hardwareStack.length > 0 && (
                    <div style={{ background: '#111', border: '1px solid #222', padding: '10px', borderRadius: '4px' }}>
                         <div style={{ fontSize: '10px', color: '#888', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}><PenTool size={12} /> PHYSICAL TOOLS</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {hardwareStack.map((tool, i) => (<span key={i} style={{ background: '#222', color: '#ccc', border: '1px solid #333', padding: '2px 6px', borderRadius: '4px', fontSize: '11px' }}>{tool}</span>))}
                        </div>
                    </div>
                )}

                {/* RECRUITER RECON */}
                <div style={{ background: '#111', border: '1px solid #222', padding: '10px', borderRadius: '4px' }}>
                    <div style={{ fontSize: '10px', color: '#888', marginBottom: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Users size={12} /> RECRUITER RECON & OUTREACH</div>
                        <button onClick={handleRecruiterRecon} style={{ background: 'transparent', border: 'none', color: 'var(--accent)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '9px', fontWeight: 'bold' }}><ScanSearch size={10} /> GOOGLE X-RAY</button>
                    </div>
                    
                    <div style={{ background: '#050505', border: '1px solid #333', padding: '10px', borderRadius: '4px', marginBottom: '10px', position: 'relative' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                            <div style={{ fontSize: '9px', color: '#666', fontWeight: 'bold' }}>STANDARDIZED DM TEMPLATE</div>
                            {outreachMsg && (<div style={{ fontSize: '9px', fontWeight: 'bold', color: outreachMsg.length > 280 ? 'var(--danger)' : outreachMsg.length > 200 ? 'orange' : '#666' }}>{outreachMsg.length} / 300 CHARS</div>)}
                        </div>
                        
                        {outreachMsg ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <textarea
                                    value={outreachMsg}
                                    onChange={(e) => { setOutreachMsg(e.target.value); localJob.outreach_message = e.target.value; }}
                                    style={{ width: '100%', minHeight: '80px', background: '#111', color: '#ccc', border: '1px solid #222', padding: '8px', fontFamily: 'monospace', fontSize: '11px', lineHeight: '1.4', resize: 'vertical', outline: 'none', borderRadius: '3px' }} 
                                />
                                <div style={{ display: 'flex', gap: '5px' }}>
                                    <button onClick={copyOutreachMessage} style={{ flexGrow: 1, background: msgCopied ? 'var(--accent)' : '#222', border: '1px solid #444', color: msgCopied ? '#000' : '#fff', padding: '6px', borderRadius: '3px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', fontSize: '10px', fontWeight: 'bold', transition: 'all 0.2s' }}>
                                        {msgCopied ? "COPIED" : "COPY PAYLOAD"} {msgCopied ? <Check size={12} /> : <Copy size={12} />}
                                    </button>
                                    <button onClick={handleGenerateOutreach} disabled={generatingMsg} style={{ background: 'transparent', border: '1px solid #444', color: '#aaa', padding: '6px 10px', borderRadius: '3px', cursor: generatingMsg ? 'wait' : 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', transition: 'all 0.2s' }} title="Retry Generation">
                                        <RefreshCw size={12} className={generatingMsg ? "live-dot" : ""} />
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: '10px 0' }}>
                                <button onClick={handleGenerateOutreach} disabled={generatingMsg} style={{ background: '#222', border: '1px solid #444', color: '#fff', padding: '8px 15px', borderRadius: '4px', cursor: generatingMsg ? 'wait' : 'pointer', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s' }}>
                                    <BrainCircuit size={12} className={generatingMsg ? "live-dot" : ""} /> {generatingMsg ? "DRAFTING PITCH (32B)..." : "GENERATE DM TEMPLATE"}
                                </button>
                            </div>
                        )}
                    </div>

                    <div style={{ background: '#050505', border: '1px solid #333', padding: '10px', borderRadius: '4px', marginBottom: '10px' }}>
                        <div style={{ fontSize: '9px', color: '#666', fontWeight: 'bold', marginBottom: '8px' }}>ADD NEW CONTACT</div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px', marginBottom: '5px' }}>
                            <input type="text" placeholder="Name" value={newContact.name} onChange={e => setNewContact({...newContact, name: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none' }} />
                            <input type="text" placeholder="Title (e.g. Hiring Manager)" value={newContact.title} onChange={e => setNewContact({...newContact, title: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none' }} />
                            <input type="text" placeholder="Email" value={newContact.email} onChange={e => setNewContact({...newContact, email: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none' }} />
                            <input type="text" placeholder="Phone" value={newContact.phone} onChange={e => setNewContact({...newContact, phone: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none' }} />
                        </div>
                        <textarea placeholder="Message sent (Optional)" value={newContact.message_sent} onChange={e => setNewContact({...newContact, message_sent: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none', width: '100%', minHeight: '40px', resize: 'vertical', boxSizing: 'border-box', marginBottom: '5px', fontFamily: 'monospace' }} />
                        <div style={{ display: 'flex', gap: '5px' }}>
                            <input type="text" placeholder="LinkedIn URL" value={newContact.url} onChange={e => setNewContact({...newContact, url: e.target.value})} style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '6px', fontSize: '11px', borderRadius: '3px', outline: 'none', flexGrow: 1 }} />
                            <button onClick={handleAddRecruiter} disabled={!newContact.url && !newContact.email && !newContact.phone} style={{ background: (newContact.url || newContact.email || newContact.phone) ? 'var(--accent)' : '#222', color: (newContact.url || newContact.email || newContact.phone) ? '#000' : '#555', border: 'none', padding: '0 15px', borderRadius: '3px', fontWeight: 'bold', fontSize: '11px', cursor: (newContact.url || newContact.email || newContact.phone) ? 'pointer' : 'not-allowed', display: 'flex', alignItems: 'center', gap: '4px', transition: 'all 0.2s' }}>
                                <Plus size={12} /> ADD
                            </button>
                        </div>
                    </div>

                    {recruiters.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                            {recruiters.map((rec, i) => (
                                <div key={i} style={{ display: 'flex', background: '#222', borderRadius: '3px', border: rec.contacted ? '1px solid var(--accent)' : '1px solid #333', overflow: 'hidden' }}>
                                    <a href={rec.url || (rec.email ? `mailto:${rec.email}` : '#')} target="_blank" rel="noreferrer" style={{ flexGrow: 1, textDecoration: 'none', padding: '8px', display: 'block' }}>
                                        <div style={{ fontSize: '11px', fontWeight: 'bold', color: rec.contacted ? 'var(--accent)' : '#fff', marginBottom: '4px' }}>
                                            {rec.name} <span style={{ color: '#888', fontWeight: 'normal' }}>- {rec.title}</span>
                                        </div>
                                        <div style={{ fontSize: '10px', color: '#aaa', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                            {rec.email && <span>📧 {rec.email}</span>}
                                            {rec.phone && <span>📱 {rec.phone}</span>}
                                            {rec.url && <span>🔗 {rec.url.replace('https://www.', '').replace('linkedin.com/in/', '@/')}</span>}
                                        </div>
                                        {rec.message_sent && <div style={{ fontSize: '10px', color: '#888', marginTop: '6px', fontStyle: 'italic', borderLeft: '2px solid #444', paddingLeft: '6px' }}>"{rec.message_sent}"</div>}
                                    </a>
                                    <button onClick={() => handleToggleContact(rec.url || rec.email)} title={rec.contacted ? "Mark as Not Contacted" : "Mark as Contacted"} style={{ width: '30px', background: rec.contacted ? 'rgba(0,255,157,0.1)' : '#1a1a1a', borderLeft: '1px solid #333', borderTop: 'none', borderRight: 'none', borderBottom: 'none', color: rec.contacted ? 'var(--accent)' : '#444', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }}>
                                        {rec.contacted ? <CheckCircle2 size={14} /> : <Mail size={14} />}
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{ fontSize: '11px', color: '#444', textAlign: 'center', padding: '10px 0' }}>No profiles tracked yet.</div>
                    )}
                </div>

                <div style={{ fontSize: '14px', lineHeight: '1.5', color: '#eee', whiteSpace: 'pre-wrap', borderTop: '1px solid #222', paddingTop: '10px' }}>
                    <div style={{ fontSize: '10px', color: '#666', marginBottom: '5px' }}>SCORING RATIONALE</div>
                    {formatResume(reasonText)}
                </div>

                {/* --- NEW MAPPING RATIONALE BLOCK --- */}
                <div style={{ borderTop: '1px solid #222', paddingTop: '10px', marginTop: '10px' }}>
                    <div style={{ fontSize: '10px', color: '#888', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <FileCheck size={12} /> JD-TO-RESUME MAPPING (PROOF OF AUDIT)
                    </div>
                    <textarea
                        value={mappingRationale}
                        onChange={(e) => {
                            setMappingRationale(e.target.value);
                            localJob.resume_rationale = e.target.value; // Optimistic update
                        }}
                        onBlur={handleSaveRationale} // Auto-saves when you click away
                        placeholder="Paste your Gemini 'Proof of Audit' mapping here for interview prep..."
                        style={{ 
                            width: '100%', minHeight: '120px', background: '#050505', color: '#ccc', 
                            border: '1px solid #333', padding: '10px', fontFamily: 'monospace', 
                            fontSize: '11px', lineHeight: '1.4', resize: 'vertical', outline: 'none', 
                            borderRadius: '4px' 
                        }}
                    />
                </div>
                {/* ----------------------------------- */}

                <div style={{ marginTop: 'auto', background: '#050505', border: '1px solid #333', borderRadius: '4px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ padding: '10px', background: '#111' }}>
                        <button onClick={handleDeploy} disabled={deploying || !hasResume || isEditingResume} style={{ width: '100%', background: deployed ? 'var(--accent)' : '#222', color: deployed ? '#000' : 'var(--accent)', border: `1px solid ${deployed ? 'var(--accent)' : '#444'}`, padding: '10px', borderRadius: '4px', cursor: (deploying || !hasResume || isEditingResume) ? 'not-allowed' : 'pointer', fontWeight: 'bold', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', transition: 'all 0.3s', opacity: (!hasResume || isEditingResume) ? 0.5 : 1 }}>
                            {deploying ? "CONVERTING PDF..." : deployed ? "DEPLOYMENT SUCCESSFUL" : "DEPLOY PDF"}
                            {deploying && <RefreshCw size={14} className="live-dot" style={{marginRight: 0}} />}
                            {!deploying && !deployed && <FileDown size={14} />}
                            {deployed && <FileCheck size={14} />}
                        </button>
                    </div>
                </div>
            </div>
            
            <div style={{ padding: '15px', borderTop: '1px solid #222', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <a href={localJob.url} target="_blank" rel="noreferrer" style={{ flexGrow: 1, textDecoration: 'none', textAlign: 'center', color: '#fff', border: '1px solid #444', padding: '8px', borderRadius: '4px', fontSize: '12px', background: '#111', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', transition: 'background 0.2s' }}>
                        OPEN ORIGINAL SOURCE <ExternalLink size={14} />
                    </a>
                    <button onClick={handleCopyUrl} style={{ background: urlCopied ? 'var(--accent)' : '#111', border: '1px solid #444', color: urlCopied ? '#000' : '#aaa', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', fontWeight: 'bold', transition: 'all 0.2s' }}>
                        {urlCopied ? "COPIED!" : "COPY URL"} {urlCopied ? <Check size={14} /> : <Link size={14} />}
                    </button>
                </div>

                 {localJob.status === 'TARGET' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '5px' }}>
                        <button onClick={() => handleTriageAction('REJECTED')} style={{ background: '#220000', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'opacity 0.2s' }}>REJECT (X)</button>
                        <button onClick={() => handleTriageAction('APPLIED')} style={{ background: 'var(--applied)', border: 'none', color: '#fff', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', cursor: 'pointer', transition: 'opacity 0.2s' }}>MARK APPLIED (A) <Check size={14} /></button>
                    </div>
                )}
                 {localJob.status === 'APPLIED' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '5px' }}>
                        <button onClick={() => handleCorrection('TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#888', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'opacity 0.2s' }}>UNDO (TO TARGET)</button>
                        <button onClick={() => handleTriageAction('INTERVIEW')} style={{ background: 'var(--interview)', border: 'none', color: '#000', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'opacity 0.2s' }}>MARK INTERVIEW</button>
                    </div>
                )}
                {localJob.status === 'INTERVIEW' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '5px' }}>
                        <button onClick={() => handleCorrection('APPLIED')} style={{ background: '#000', border: '1px solid #444', color: '#888', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'opacity 0.2s' }}>UNDO (TO APPLIED)</button>
                        <button onClick={() => handleTriageAction('OFFER')} style={{ background: '#fff', border: 'none', color: '#000', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', transition: 'opacity 0.2s' }}>MARK OFFER</button>
                    </div>
                )}
                {localJob.status === 'REJECTED' && (
                    <button onClick={() => handleCorrection('TARGET')} style={{ background: '#000', border: '1px solid #444', color: '#fff', padding: '10px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', cursor: 'pointer', marginTop: '5px', transition: 'opacity 0.2s' }}>
                        RESTORE TO TARGET <RotateCcw size={14} />
                    </button>
                )}
            </div>
        </div>

        <div style={splitterStyle} onMouseDown={handleDragStart(2)} onMouseOver={(e) => e.target.style.background = '#333'} onMouseOut={(e) => e.target.style.background = 'transparent'} />

        {/* PANE 3: ASSET */}
        <div style={{ flexGrow: 1, flex: 'none', width: `${100 - leftWidth - centerWidth}%`, background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '10px 15px', borderBottom: '1px solid #222', background: '#111', fontWeight: 'bold', fontSize: '12px', color: '#aaa', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <User size={14} /> ACTIVE ASSET ({localJob.selected_resume || "None"})
                </div>
                {!isEditingResume ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={handleCopyResume} disabled={!hasResume || resumeContent === "Loading..."} style={{ background: 'transparent', border: 'none', color: resumeCopied ? 'var(--accent)' : '#aaa', cursor: (!hasResume || resumeContent === "Loading...") ? 'not-allowed' : 'pointer', padding: '4px', transition: 'color 0.2s' }} title="Copy Resume Content">
                            {resumeCopied ? <Check size={16} /> : <Copy size={16} />}
                        </button>
                        <button onClick={handleRebuildResume} disabled={!hasResume || rebuilding || isEditingResume} style={{ background: 'transparent', border: 'none', color: rebuilding ? 'var(--accent)' : '#aaa', cursor: (!hasResume || rebuilding) ? 'not-allowed' : 'pointer', padding: '4px', transition: 'color 0.2s' }} title="Full Asset Rebuild (Regenerate from Source)"><Zap size={16} className={rebuilding ? "live-dot" : ""} /></button>
                        <button onClick={handleRegenerateSummary} disabled={!hasResume || regenerating || resumeContent === "Loading..."} style={{ background: 'transparent', border: 'none', color: regenerating ? 'var(--accent)' : '#aaa', cursor: (!hasResume || regenerating || resumeContent === "Loading...") ? 'not-allowed' : 'pointer', padding: '4px', transition: 'color 0.2s' }} title="Regenerate Summary Only"><RefreshCw size={16} className={regenerating ? "live-dot" : ""} /></button>
                        <button onClick={() => { setResumeEditContent(resumeContent); setIsEditingResume(true); }} disabled={!hasResume || resumeContent === "Loading..."} style={{ background: 'transparent', border: 'none', color: resumeContent === "Loading..." ? '#444' : '#aaa', cursor: resumeContent === "Loading..." ? 'not-allowed' : 'pointer', padding: '4px', transition: 'color 0.2s' }} title="Edit Resume"><Edit size={16} /></button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={handleSaveResumeEdit} style={{ background: 'var(--accent)', border: 'none', color: '#000', borderRadius: '3px', padding: '4px 8px', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}><Save size={12} /> SAVE</button>
                        <button onClick={() => setIsEditingResume(false)} style={{ background: '#333', border: 'none', color: '#fff', borderRadius: '3px', padding: '4px 8px', fontSize: '10px', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}><XCircle size={12} /> CANCEL</button>
                    </div>
                )}
            </div>
            
            <div style={{ flexGrow: 1, overflow: 'hidden', position: 'relative' }}>
                {isEditingResume ? (
                    <textarea 
                        value={resumeEditContent} 
                        onChange={(e) => setResumeEditContent(e.target.value)}
                        style={{ width: '100%', height: '100%', background: '#050505', color: '#ddd', border: 'none', padding: '20px', fontFamily: 'monospace', fontSize: '12px', resize: 'none', outline: 'none', boxSizing: 'border-box' }} 
                    />
                ) : (
                    <div style={{ height: '100%', overflowY: 'auto', color: '#888', fontSize: '11px', fontFamily: 'monospace', whiteSpace: 'pre-wrap', boxSizing: 'border-box' }}>
                        {!hasResume ? (
                             <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '15px' }} className="fade-in">
                                 <FilePlus size={32} color="#333" />
                                 <div style={{ fontSize: '12px', color: '#666' }}>NO RESUME GENERATED</div>
                                 <button onClick={handleRegenerateSummary} style={{ background: '#222', border: '1px solid #444', color: '#fff', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s' }} onMouseOver={e => e.target.style.borderColor = 'var(--accent)'} onMouseOut={e => e.target.style.borderColor = '#444'}><BrainCircuit size={14} /> GENERATE ASSET</button>
                             </div>
                        ) : resumeContent === "Loading..." ? (
                            renderSkeletonResume()
                        ) : (
                            <div style={{ padding: '20px' }} className="fade-in">
                                {formatResume(resumeContent)}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>

      </div>
    </div>
  );
}