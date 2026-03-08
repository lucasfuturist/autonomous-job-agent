import React, { useState, useEffect } from 'react';
import { X, Save, User, Mail, Phone, Link, MessageSquare, Clock, FileText, Plus, Briefcase } from 'lucide-react';

export default function ContactModal({ contact, onClose, onSave, onOpenJob }) {
    const [formData, setFormData] = useState({ ...contact });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (contact) {
            const data = { ...contact };
            if (!data.contact_dates) {
                data.contact_dates = data.contacted_date ? [data.contacted_date] : [];
            }
            setFormData(data);
        }
    }, [contact]);

    if (!contact) return null;

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSave = async () => {
        setSaving(true);
        const old_id = contact.url || contact.email;
        
        try {
            await fetch('/api/recruiters/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: contact.job_id, old_id: old_id, contact: formData })
            });
            onSave(formData, old_id);
            onClose();
        } catch (e) {
            console.error("Failed to save contact", e);
            alert("Failed to save contact.");
        } finally {
            setSaving(false);
        }
    };

    const getLocalYMD = (isoStr) => {
        if (!isoStr) return '';
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return '';
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    };

    const updateDateFromYMD = (oldIso, newYmd) => {
        if (!newYmd) return oldIso;
        const [y, m, d] = newYmd.split('-');
        const dateObj = oldIso ? new Date(oldIso) : new Date();
        dateObj.setFullYear(y, m - 1, d);
        return dateObj.toISOString();
    };

    const handleDateChange = (index, newYmd) => {
        const newDates = [...formData.contact_dates];
        newDates[index] = updateDateFromYMD(newDates[index], newYmd);
        setFormData(prev => ({ ...prev, contact_dates: newDates }));
    };

    const handleAddDate = () => {
        const newDates = [...(formData.contact_dates || []), new Date().toISOString()];
        setFormData(prev => ({ ...prev, contact_dates: newDates }));
    };

    const handleRemoveDate = (index) => {
        const newDates = formData.contact_dates.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, contact_dates: newDates }));
    };

    const handleToggleContacted = () => {
        const isNowContacted = !formData.contacted;
        if (isNowContacted) {
            const newDates = formData.contact_dates?.length > 0 ? formData.contact_dates : [new Date().toISOString()];
            setFormData(prev => ({ ...prev, contacted: true, contact_dates: newDates }));
        } else {
            setFormData(prev => ({ ...prev, contacted: false, contact_dates: [] }));
        }
    };

    const getContactedText = (dateString) => {
        if (!dateString) return "Never";
        const d = new Date(dateString);
        if (isNaN(d.getTime())) return "Unknown";
        
        const now = new Date();
        const diffTime = now - d;
        const diffDays = Math.max(0, Math.floor(diffTime / (1000 * 60 * 60 * 24)));
        
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        const formattedDate = d.toLocaleDateString(undefined, options);
        
        if (diffDays === 0) return `${formattedDate} (Today)`;
        if (diffDays === 1) return `${formattedDate} (Yesterday)`;
        return `${formattedDate} (${diffDays} days ago)`;
    };

    const inputStyle = { background: '#050505', border: '1px solid #333', color: '#fff', padding: '8px', fontSize: '12px', borderRadius: '4px', outline: 'none', width: '100%', boxSizing: 'border-box' };
    const labelStyle = { fontSize: '10px', color: '#888', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 'bold' };

    const latestDate = formData.contact_dates?.length > 0 
        ? [...formData.contact_dates].sort((a,b) => new Date(a) - new Date(b)).pop() 
        : null;

    return (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(5px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }} className="fade-in" onClick={onClose}>
            
            <div style={{ background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', width: '100%', maxWidth: '500px', display: 'flex', flexDirection: 'column', overflow: 'hidden', maxHeight: '90vh' }} onClick={e => e.stopPropagation()} className="slide-up">
                
                {/* HEADER W/ INTERNAL JOB MODAL LINK */}
                <div style={{ padding: '15px 20px', borderBottom: '1px solid #222', background: '#111', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}>CONFIGURE TARGET PROFILE</div>
                        <div style={{ fontSize: '11px', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginTop: '2px' }}>
                            <span>Target: {contact.company || 'Unknown'}</span>
                            {contact.job_title && (
                                <>
                                    <span style={{ color: '#444' }}>|</span>
                                    <div 
                                        onClick={() => onOpenJob && onOpenJob(contact)} 
                                        style={{ color: '#aaa', display: 'flex', alignItems: 'center', gap: '4px', transition: 'color 0.2s', cursor: 'pointer' }} 
                                        onMouseOver={e => e.target.style.color = '#fff'} 
                                        onMouseOut={e => e.target.style.color = '#aaa'}
                                        title="Open Job Command Profile"
                                    >
                                        Role: {contact.job_title} <Briefcase size={10} />
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                    <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#888', cursor: 'pointer' }}><X size={18} /></button>
                </div>

                {/* BODY */}
                <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px', overflowY: 'auto' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div><div style={labelStyle}><User size={12} /> NAME</div><input type="text" value={formData.name || ''} onChange={e => handleChange('name', e.target.value)} style={inputStyle} /></div>
                        <div><div style={labelStyle}>TITLE</div><input type="text" value={formData.title || ''} onChange={e => handleChange('title', e.target.value)} style={inputStyle} /></div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div><div style={labelStyle}><Mail size={12} /> EMAIL</div><input type="text" value={formData.email || ''} onChange={e => handleChange('email', e.target.value)} style={inputStyle} /></div>
                        <div><div style={labelStyle}><Phone size={12} /> PHONE</div><input type="text" value={formData.phone || ''} onChange={e => handleChange('phone', e.target.value)} style={inputStyle} /></div>
                    </div>
                    <div><div style={labelStyle}><Link size={12} /> LINKEDIN URL</div><input type="text" value={formData.url || ''} onChange={e => handleChange('url', e.target.value)} style={inputStyle} /></div>
                    <div><div style={labelStyle}><MessageSquare size={12} /> OUTREACH PAYLOAD (MESSAGE SENT)</div><textarea value={formData.message_sent || ''} onChange={e => handleChange('message_sent', e.target.value)} style={{ ...inputStyle, minHeight: '60px', resize: 'vertical', fontFamily: 'monospace' }} /></div>
                    <div><div style={labelStyle}><FileText size={12} /> HISTORY & NOTES</div><textarea value={formData.history || ''} onChange={e => handleChange('history', e.target.value)} placeholder="Log call notes, background context, or follow-up details here..." style={{ ...inputStyle, minHeight: '100px', resize: 'vertical', fontFamily: 'monospace' }} /></div>

                    {/* STATUS & TIMESTAMPS */}
                    <div style={{ marginTop: '5px', borderTop: '1px solid #222', paddingTop: '15px' }}>
                        <div style={{ marginBottom: '15px' }}>
                            <div style={{...labelStyle, justifyContent: 'space-between'}}>
                                <span><Clock size={12} style={{marginRight: '4px', verticalAlign: 'middle'}}/> CONTACT HISTORY (DATES)</span>
                                <span style={{ color: latestDate ? '#ccc' : '#666' }}>{latestDate ? getContactedText(latestDate) : 'Never'}</span>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', background: '#111', padding: '10px', borderRadius: '4px', border: '1px solid #222' }}>
                                {(formData.contact_dates || []).map((isoDate, idx) => (
                                    <div key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                                        <input type="date" value={getLocalYMD(isoDate)} onChange={(e) => handleDateChange(idx, e.target.value)} style={{ ...inputStyle, width: 'auto', flexGrow: 1, cursor: 'pointer' }} />
                                        <button onClick={() => handleRemoveDate(idx)} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', display: 'flex', alignItems: 'center' }} title="Remove Date"><X size={14}/></button>
                                    </div>
                                ))}
                                <button onClick={handleAddDate} style={{ background: '#222', color: '#aaa', border: '1px dashed #444', padding: '6px', borderRadius: '4px', fontSize: '10px', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px', transition: 'all 0.2s' }}><Plus size={12} /> ADD DATE</button>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button onClick={handleToggleContacted} style={{ flex: 1, background: formData.contact_dates?.length > 0 ? 'rgba(0, 255, 157, 0.1)' : '#111', border: `1px solid ${formData.contact_dates?.length > 0 ? 'var(--accent)' : '#333'}`, color: formData.contact_dates?.length > 0 ? 'var(--accent)' : '#888', padding: '10px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' }}>
                                {formData.contact_dates?.length > 0 ? "STATUS: CONTACTED" : "STATUS: PENDING"}
                            </button>
                            <button onClick={() => handleChange('replied', !formData.replied)} disabled={!formData.contact_dates || formData.contact_dates.length === 0} style={{ flex: 1, background: formData.replied ? '#111' : '#111', border: `1px solid ${formData.replied ? '#fff' : '#333'}`, color: formData.replied ? '#fff' : '#555', opacity: formData.contact_dates?.length > 0 ? 1 : 0.3, padding: '10px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold', cursor: formData.contact_dates?.length > 0 ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}>
                                {formData.replied ? "STATUS: REPLIED" : "MARK AS REPLIED"}
                            </button>
                        </div>
                    </div>
                </div>

                {/* FOOTER */}
                <div style={{ padding: '15px 20px', borderTop: '1px solid #222', background: '#0d0d0d', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button onClick={onClose} style={{ background: 'transparent', border: '1px solid #333', color: '#fff', padding: '8px 15px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>CANCEL</button>
                    <button onClick={handleSave} disabled={saving} style={{ background: 'var(--accent)', border: 'none', color: '#000', padding: '8px 20px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', cursor: saving ? 'wait' : 'pointer' }}>
                        <Save size={14} /> {saving ? "SAVING..." : "SAVE PROFILE"}
                    </button>
                </div>
            </div>
        </div>
    );
}