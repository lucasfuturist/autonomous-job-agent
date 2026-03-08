import React, { useState, useEffect } from 'react';
import { X, Building2, Briefcase, Inbox } from 'lucide-react';
import JobCard from './JobCard';

export default function CompanyModal({ company, onClose, onJobClick, onUpdateStatus, onToggleStar }) {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!company) return;
        fetch(`/api/company_profile?company=${encodeURIComponent(company)}`)
            .then(res => res.json())
            .then(data => {
                setJobs(data.jobs || []);
                setLoading(false);
            })
            .catch(e => {
                console.error(e);
                setLoading(false);
            });
    }, [company]);

    if (!company) return null;

    return (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(5px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }} className="fade-in" onClick={onClose}>
            <div style={{ background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', overflow: 'hidden', maxHeight: '90vh' }} onClick={e => e.stopPropagation()} className="slide-up">
                
                {/* HEADER */}
                <div style={{ padding: '20px', borderBottom: '1px solid #222', background: '#111', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <div style={{ background: '#000', padding: '10px', borderRadius: '8px', border: '1px solid #333' }}>
                            <Building2 size={24} color="var(--accent)" />
                        </div>
                        <div>
                            <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '20px' }}>{company}</div>
                            <div style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>COMPANY PROFILE & ACTIVE PIPELINE</div>
                        </div>
                    </div>
                    <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', transition: 'color 0.2s' }} onMouseOver={e=>e.target.style.color='#fff'} onMouseOut={e=>e.target.style.color='#888'}>
                        <X size={24} />
                    </button>
                </div>

                {/* BODY / JOB LIST */}
                <div style={{ padding: '20px', overflowY: 'auto', background: '#050505', flexGrow: 1 }}>
                    <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#666', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Briefcase size={14} /> IDENTIFIED TARGET ROLES ({jobs.length})
                    </div>

                    {loading ? (
                        <div style={{ color: '#666', fontSize: '12px' }}>Loading intelligence...</div>
                    ) : jobs.length === 0 ? (
                        <div className="empty-state" style={{ padding: '30px' }}>
                            <Inbox size={24} opacity={0.2} color="#fff" />
                            <div style={{ fontSize: '12px', color: '#555' }}>No jobs tracked for this company.</div>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '15px' }}>
                            {jobs.map((job) => (
                                <JobCard 
                                    key={job.id} 
                                    job={job} 
                                    onUpdateStatus={onUpdateStatus} 
                                    onToggleStar={onToggleStar} 
                                    onClick={() => {
                                        // Close the company modal and open the detailed job modal
                                        onClose();
                                        onJobClick(job);
                                    }}
                                    compact={true}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}