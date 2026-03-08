import React, { useState, useEffect } from 'react';
import { Mail, Phone, ExternalLink, Clock, AlertCircle, Search, CheckCircle2, Building2, Briefcase, ChevronDown, ChevronRight, LayoutPanelTop } from 'lucide-react';
import ContactModal from '../components/ContactModal';
import CompanyModal from '../components/CompanyModal';
import JobModal from '../components/JobModal'; 

export default function Network() {
    const [contacts, setContacts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    
    // Modal States
    const [selectedContact, setSelectedContact] = useState(null);
    const [selectedCompany, setSelectedCompany] = useState(null);
    const [selectedJob, setSelectedJob] = useState(null);
    
    // Accordion State
    const [collapsedCompanies, setCollapsedCompanies] = useState({});

    useEffect(() => {
        fetch('/api/network')
            .then(res => res.json())
            .then(data => {
                const cleanedData = data.map(c => {
                    if (!c.contact_dates) c.contact_dates = c.contacted_date ? [c.contacted_date] : [];
                    return c;
                });
                const sorted = cleanedData.sort((a, b) => {
                    const aDate = a.contact_dates?.length > 0 ? new Date([...a.contact_dates].sort().pop()) : new Date(0);
                    const bDate = b.contact_dates?.length > 0 ? new Date([...b.contact_dates].sort().pop()) : new Date(0);
                    return bDate - aDate;
                });
                setContacts(sorted);
                setLoading(false);
            })
            .catch(e => { console.error(e); setLoading(false); });
    }, []);

    const handleUpdateContact = (updatedContact, oldId) => {
        setContacts(prev => prev.map(c => {
            if (c.job_id === updatedContact.job_id && (c.url === oldId || c.email === oldId)) return updatedContact;
            return c;
        }));
    };

    const handleToggleReply = async (contact) => {
        const url_or_email = contact.url || contact.email;
        const newRepliedStatus = !contact.replied;
        
        setContacts(prev => prev.map(c => {
            if ((c.url && c.url === url_or_email) || (c.email && c.email === url_or_email)) return { ...c, replied: newRepliedStatus };
            return c;
        }));

        try {
            await fetch('/api/recruiters/reply', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: contact.job_id, url: url_or_email, replied: newRepliedStatus })
            });
        } catch (e) { console.error(e); }
    };

    // --- NEW: Fetch and open the Job Modal from the Contact Modal ---
    const handleOpenJobFromContact = async (contact) => {
        try {
            const res = await fetch(`/api/company_profile?company=${encodeURIComponent(contact.company)}`);
            if (res.ok) {
                const data = await res.json();
                const targetJob = data.jobs.find(j => j.id === contact.job_id);
                if (targetJob) {
                    setSelectedContact(null); // Close the CRM modal
                    setSelectedJob(targetJob); // Open the Job modal
                } else {
                    alert("Could not locate the original job record. It may have been purged.");
                }
            }
        } catch (e) {
            console.error("Failed to load job profile", e);
        }
    };

    // Job Event Handlers (Passed to Company/Job Modals)
    const handleUpdateJobStatus = async (id, newStatus) => {
        await fetch('/api/update_status', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, status: newStatus })
        });
        if (selectedJob && selectedJob.id === id) setSelectedJob({...selectedJob, status: newStatus});
    };

    const handleToggleJobStar = async (id, starred) => {
        await fetch('/api/star', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, starred })
        });
        if (selectedJob && selectedJob.id === id) setSelectedJob({...selectedJob, starred: starred ? 1 : 0});
    };

    const calculateFollowUp = (contact) => {
        let latestDateStr = contact.contacted_date;
        if (contact.contact_dates && contact.contact_dates.length > 0) {
            const sorted = [...contact.contact_dates].sort((a, b) => new Date(a) - new Date(b));
            latestDateStr = sorted[sorted.length - 1];
        }
        if (!latestDateStr) return { days: 0, text: "Unknown", urgent: false };
        
        const contactDate = new Date(latestDateStr);
        const now = new Date();
        const diffDays = Math.max(0, Math.floor((now - contactDate) / (1000 * 60 * 60 * 24)));
        
        const targetDate = new Date(contactDate);
        targetDate.setDate(targetDate.getDate() + 3);
        const dayOfWeek = targetDate.getDay(); 
        if (dayOfWeek === 6) targetDate.setDate(targetDate.getDate() + 2); 
        else if (dayOfWeek === 0) targetDate.setDate(targetDate.getDate() + 1); 
        
        const isUrgent = now >= targetDate && !contact.replied;
        return { days: diffDays, text: diffDays === 0 ? "Today" : `${diffDays}d ago`, urgent: isUrgent };
    };

    const toggleCompanyCollapse = (companyName) => {
        setCollapsedCompanies(prev => ({ ...prev, [companyName]: !prev[companyName] }));
    };

    const filteredContacts = contacts.filter(c => {
        if (!search) return true;
        const term = search.toLowerCase();
        return (c.name?.toLowerCase().includes(term) || c.company?.toLowerCase().includes(term) || c.title?.toLowerCase().includes(term) || c.job_title?.toLowerCase().includes(term));
    });

    const groupedContacts = filteredContacts.reduce((acc, contact) => {
        const comp = contact.company || 'Unknown';
        if (!acc[comp]) acc[comp] = [];
        acc[comp].push(contact);
        return acc;
    }, {});

    const sortedCompanies = Object.keys(groupedContacts).sort();

    return (
        <div className="fade-in">
            {/* INJECT MODALS */}
            {selectedContact && (
                <ContactModal 
                    contact={selectedContact} 
                    onClose={() => setSelectedContact(null)} 
                    onSave={handleUpdateContact} 
                    onOpenJob={handleOpenJobFromContact} // <-- Pass the new prop here
                />
            )}
            {selectedCompany && <CompanyModal company={selectedCompany} onClose={() => setSelectedCompany(null)} onJobClick={setSelectedJob} onUpdateStatus={handleUpdateJobStatus} onToggleStar={handleToggleJobStar} />}
            {selectedJob && <JobModal job={selectedJob} onClose={() => setSelectedJob(null)} onUpdateStatus={handleUpdateJobStatus} onToggleStar={handleToggleJobStar} />}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1 style={{ fontSize: '24px', margin: 0 }}>NETWORK RECON</h1>
                
                <div style={{ background: '#111', padding: '10px', border: '1px solid #333', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <Search size={14} color="#666" />
                    <input 
                        type="text" placeholder="Search names, roles, or companies..." value={search} onChange={(e) => setSearch(e.target.value)} 
                        style={{ background: 'transparent', border: 'none', color: '#fff', width: '250px', fontSize: '12px', outline: 'none' }} 
                    />
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {loading ? (
                    <div style={{ color: '#666' }}>Loading comms database...</div>
                ) : sortedCompanies.length === 0 ? (
                    <div className="empty-state" style={{ padding: '40px' }}>
                        <Mail size={32} opacity={0.2} color="#fff" />
                        <div style={{ fontSize: '12px', color: '#555' }}>No active contacts found. Add them from the War Room.</div>
                    </div>
                ) : (
                    sortedCompanies.map((companyName) => (
                        <div key={companyName} className="slide-up">
                            
                            {/* Accordion Header */}
                            <div 
                                onClick={() => toggleCompanyCollapse(companyName)}
                                style={{ 
                                    display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
                                    fontSize: '16px', fontWeight: 'bold', color: '#fff', 
                                    marginBottom: collapsedCompanies[companyName] ? '0' : '10px', 
                                    borderBottom: '1px solid #333', paddingBottom: '8px', 
                                    cursor: 'pointer', transition: 'all 0.2s', userSelect: 'none'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Building2 size={16} color="var(--accent)" />
                                    {companyName}
                                    <span style={{ fontSize: '10px', color: '#888', background: '#111', padding: '2px 8px', borderRadius: '10px', border: '1px solid #333', fontWeight: 'normal' }}>
                                        {groupedContacts[companyName].length} TARGET{groupedContacts[companyName].length !== 1 && 'S'}
                                    </span>
                                </div>
                                
                                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                    {/* Company Profile Button */}
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); setSelectedCompany(companyName); }}
                                        style={{ background: 'var(--accent)', border: 'none', color: '#000', padding: '4px 10px', borderRadius: '3px', fontSize: '10px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', transition: 'opacity 0.2s' }}
                                    >
                                        <LayoutPanelTop size={12} /> COMPANY PROFILE
                                    </button>

                                    <div style={{ color: '#666' }}>
                                        {collapsedCompanies[companyName] ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
                                    </div>
                                </div>
                            </div>

                            {/* Contacts Array */}
                            {!collapsedCompanies[companyName] && (
                                <div style={{ display: 'grid', gap: '10px', animation: 'fadeIn 0.2s ease-out' }}>
                                    {groupedContacts[companyName].map((contact, i) => {
                                        const followUp = calculateFollowUp(contact);
                                        return (
                                            <div key={i} onClick={() => setSelectedContact(contact)} style={{ background: '#0a0a0a', border: '1px solid #222', borderLeft: followUp.urgent ? '3px solid var(--warning)' : (contact.replied ? '3px solid var(--accent)' : '3px solid #333'), padding: '15px', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', transition: 'all 0.2s', cursor: 'pointer' }} className="job-card-hover">
                                                <div style={{ flex: 2 }}>
                                                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: contact.replied ? '#aaa' : '#fff', marginBottom: '4px', textDecoration: contact.replied ? 'line-through' : 'none' }}>{contact.name}</div>
                                                    <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px' }}>{contact.title}</div>
                                                    {contact.job_title && (
                                                        <div style={{ fontSize: '10px', color: 'var(--accent)', display: 'inline-flex', alignItems: 'center', gap: '5px', background: 'rgba(0,255,157,0.05)', padding: '2px 6px', borderRadius: '3px', border: '1px solid rgba(0,255,157,0.2)' }}>
                                                            <Briefcase size={10} /> {contact.job_title}
                                                        </div>
                                                    )}
                                                </div>

                                                <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                    {contact.email && <a href={`mailto:${contact.email}`} onClick={e => e.stopPropagation()} style={{ fontSize: '11px', color: '#ccc', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', width: 'fit-content' }}><Mail size={12} color="#666" /> {contact.email}</a>}
                                                    {contact.phone && <div style={{ fontSize: '11px', color: '#ccc', display: 'flex', alignItems: 'center', gap: '6px' }}><Phone size={12} color="#666" /> {contact.phone}</div>}
                                                    {contact.url && <a href={contact.url} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()} style={{ fontSize: '11px', color: '#ccc', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', width: 'fit-content' }}><ExternalLink size={12} color="#666" /> LinkedIn Profile</a>}
                                                    {contact.message_sent && <div style={{ marginTop: '4px', fontSize: '10px', color: '#888', fontStyle: 'italic', borderLeft: '2px solid #333', paddingLeft: '8px', overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis', maxWidth: '200px' }}>"{contact.message_sent}"</div>}
                                                </div>

                                                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                                                    <button onClick={(e) => { e.stopPropagation(); handleToggleReply(contact); }} style={{ background: contact.replied ? 'rgba(0, 255, 157, 0.1)' : '#1a1a1a', border: `1px solid ${contact.replied ? 'var(--accent)' : '#444'}`, color: contact.replied ? 'var(--accent)' : '#aaa', padding: '4px 8px', borderRadius: '3px', fontSize: '9px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                        {contact.replied ? <CheckCircle2 size={12} /> : <Mail size={12} />} {contact.replied ? "REPLIED" : "MARK REPLIED"}
                                                    </button>
                                                    {contact.contacted && !contact.replied && (
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', fontWeight: 'bold', color: followUp.urgent ? 'var(--warning)' : '#666' }}>
                                                            {followUp.urgent ? <AlertCircle size={12} /> : <Clock size={12} />} {followUp.urgent ? `FOLLOW UP (${followUp.text})` : `Sent ${followUp.text}`}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}