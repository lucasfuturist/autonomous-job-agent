import React, { useState, useEffect } from 'react';
import { Building2, Star, Search, PenLine, Save, X, CheckSquare } from 'lucide-react';
import JobModal from '../components/JobModal'; 

export default function Companies() {
  const [companies, setCompanies] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyJobs, setCompanyJobs] = useState([]);
  
  // Job-level filtering & sorting state
  const [jobSearchTerm, setJobSearchTerm] = useState("");
  const [jobStatusFilter, setJobStatusFilter] = useState("ALL");
  const [jobSortOption, setJobSortOption] = useState("SCORE_DESC"); // Default sort
  
  // Editing state
  const [isEditingCompany, setIsEditingCompany] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState("");

  // Modal State
  const [selectedJob, setSelectedJob] = useState(null);

  const fetchCompanies = () => {
    fetch('/api/companies')
      .then(res => {
          if (!res.ok) throw new Error("Backend endpoint not found.");
          return res.json();
      })
      .then(data => setCompanies(data || []))
      .catch(err => console.error("Failed to load companies:", err));
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const loadCompanyProfile = (companyName) => {
    setSelectedCompany(companyName);
    setIsEditingCompany(false);
    setJobSearchTerm("");
    setJobStatusFilter("ALL");
    setJobSortOption("SCORE_DESC");
    
    fetch(`/api/company_profile?company=${encodeURIComponent(companyName)}`)
      .then(res => res.json())
      .then(data => setCompanyJobs(data.jobs || []))
      .catch(err => console.error(err));
  };

  const handleRenameCompany = async () => {
    if (!newCompanyName.trim() || newCompanyName === selectedCompany) {
        setIsEditingCompany(false);
        return;
    }
    
    try {
        const res = await fetch('/api/company/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_name: selectedCompany, new_name: newCompanyName })
        });
        
        if (res.ok) {
            setIsEditingCompany(false);
            fetchCompanies(); // Refresh left pane
            loadCompanyProfile(newCompanyName); // Reload right pane with new name
        }
    } catch (e) {
        console.error("Failed to rename company:", e);
    }
  };

  // FAST-ACTION: Restore a Rejected Job to Target
  const handleRestoreJob = async (e, jobId) => {
    e.stopPropagation(); // Prevent the modal from opening
    try {
        const res = await fetch('/api/update_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: jobId, status: 'TARGET' })
        });
        
        if (res.ok) {
            // Instantly update the local job list
            setCompanyJobs(prev => prev.map(j => j.id === jobId ? {...j, status: 'TARGET'} : j));
            // Refresh the left pane so the "Targets:" counter increments correctly
            fetchCompanies(); 
        }
    } catch (e) {
        console.error("Failed to restore job:", e);
    }
  };

  // Filter Left Pane
  const filteredCompanies = companies.filter(c => {
      if (!c || !c.company) return false;
      return c.company.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Filter & Sort Right Pane
  const filteredAndSortedJobs = companyJobs
    .filter(job => {
        const matchesSearch = job.title.toLowerCase().includes(jobSearchTerm.toLowerCase()) || 
                              (job.location && job.location.toLowerCase().includes(jobSearchTerm.toLowerCase()));
        const matchesStatus = jobStatusFilter === "ALL" || job.status === jobStatusFilter;
        return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
        if (jobSortOption === "SCORE_DESC") return b.score - a.score;
        if (jobSortOption === "SCORE_ASC") return a.score - b.score;
        if (jobSortOption === "ALPHA_ASC") return a.title.localeCompare(b.title);
        if (jobSortOption === "ALPHA_DESC") return b.title.localeCompare(a.title);
        if (jobSortOption === "DATE_DESC") return new Date(b.found_at) - new Date(a.found_at);
        return 0;
    });

  return (
    <div style={{ display: 'flex', height: '100%', gap: '20px' }} className="fade-in">
      
      {/* LEFT PANE: Company Roster */}
      <div style={{ width: '35%', display: 'flex', flexDirection: 'column', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #222', background: '#111' }}>
          <h2 style={{ margin: '0 0 15px 0', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: '#fff' }}>
            <Building2 size={18} color="var(--accent)" /> STRATEGIC ROSTER
          </h2>
          <div style={{ display: 'flex', background: '#000', border: '1px solid #333', borderRadius: '4px', padding: '8px 12px', alignItems: 'center', gap: '8px' }}>
            <Search size={14} color="#666" />
            <input 
              type="text" 
              placeholder="Filter companies..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#fff', width: '100%', outline: 'none', fontSize: '12px' }}
            />
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          {filteredCompanies.length === 0 ? (
              <div style={{ padding: '30px 20px', textAlign: 'center', color: '#666', fontSize: '12px' }}>
                  {searchTerm ? `No targets found for "${searchTerm}"` : "Awaiting Hunter Agent data..."}
              </div>
          ) : (
              filteredCompanies.map((c, i) => (
                <div 
                  key={i} 
                  onClick={() => loadCompanyProfile(c.company)}
                  style={{ 
                    padding: '15px 20px', borderBottom: '1px solid #222', cursor: 'pointer', 
                    background: selectedCompany === c.company ? '#1a1a1a' : 'transparent',
                    borderLeft: selectedCompany === c.company ? '3px solid var(--accent)' : '3px solid transparent',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                    <span style={{ fontWeight: 'bold', color: selectedCompany === c.company ? 'var(--accent)' : '#fff', fontSize: '14px' }}>{c.company}</span>
                    <span style={{ fontSize: '11px', background: '#222', padding: '2px 8px', borderRadius: '12px', color: '#aaa' }}>{c.total_jobs} Reqs</span>
                  </div>
                  <div style={{ display: 'flex', gap: '15px', fontSize: '11px', color: '#666' }}>
                    <span>🎯 Targets: <strong style={{color: '#fff'}}>{c.target_jobs}</strong></span>
                    <span>🔥 Peak Score: <strong style={{color: 'var(--accent)'}}>{c.max_score}</strong></span>
                  </div>
                </div>
              ))
          )}
        </div>
      </div>

      {/* RIGHT PANE: Selected Company Detail */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', overflow: 'hidden' }}>
        {!selectedCompany ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#444' }}>
            <Building2 size={48} style={{ marginBottom: '15px', opacity: 0.5 }} />
            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>SELECT A COMPANY</div>
            <div style={{ fontSize: '12px', marginTop: '5px' }}>Review all open requisitions to identify the highest probability target.</div>
          </div>
        ) : (
          <>
            <div style={{ padding: '20px', borderBottom: '1px solid #222', background: '#111', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {isEditingCompany ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input 
                            type="text" 
                            value={newCompanyName} 
                            onChange={e => setNewCompanyName(e.target.value)}
                            style={{ background: '#000', border: '1px solid var(--accent)', color: '#fff', padding: '6px 10px', borderRadius: '4px', fontSize: '16px', fontWeight: 'bold', outline: 'none' }}
                            autoFocus
                        />
                        <button onClick={handleRenameCompany} style={{ background: 'var(--accent)', border: 'none', color: '#000', padding: '6px', borderRadius: '4px', cursor: 'pointer' }}><Save size={16}/></button>
                        <button onClick={() => setIsEditingCompany(false)} style={{ background: '#333', border: 'none', color: '#fff', padding: '6px', borderRadius: '4px', cursor: 'pointer' }}><X size={16}/></button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <h2 style={{ margin: 0, fontSize: '20px', color: '#fff' }}>{selectedCompany}</h2>
                        <button 
                            onClick={() => { setNewCompanyName(selectedCompany); setIsEditingCompany(true); }}
                            style={{ background: 'transparent', border: 'none', color: '#666', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px' }}
                            title="Edit Company Name"
                        >
                            <PenLine size={16} />
                        </button>
                    </div>
                )}
                <div style={{ fontSize: '12px', color: '#888' }}>{companyJobs.length} Processed Requisitions</div>
              </div>

              {/* Job Filters & Sort */}
              <div style={{ display: 'flex', gap: '10px' }}>
                <div style={{ flex: 1, display: 'flex', background: '#000', border: '1px solid #333', borderRadius: '4px', padding: '8px 12px', alignItems: 'center', gap: '8px' }}>
                  <Search size={14} color="#666" />
                  <input 
                    type="text" 
                    placeholder="Search titles or locations..." 
                    value={jobSearchTerm}
                    onChange={(e) => setJobSearchTerm(e.target.value)}
                    style={{ background: 'transparent', border: 'none', color: '#fff', width: '100%', outline: 'none', fontSize: '12px' }}
                  />
                </div>
                
                {/* SORT DROPDOWN */}
                <select 
                    value={jobSortOption} 
                    onChange={e => setJobSortOption(e.target.value)}
                    style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '8px 12px', borderRadius: '4px', outline: 'none', fontSize: '12px', cursor: 'pointer' }}
                >
                    <option value="SCORE_DESC">Sort: Score (High-Low)</option>
                    <option value="SCORE_ASC">Sort: Score (Low-High)</option>
                    <option value="ALPHA_ASC">Sort: Title (A-Z)</option>
                    <option value="ALPHA_DESC">Sort: Title (Z-A)</option>
                    <option value="DATE_DESC">Sort: Newest First</option>
                </select>

                {/* STATUS FILTER */}
                <select 
                    value={jobStatusFilter} 
                    onChange={e => setJobStatusFilter(e.target.value)}
                    style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '8px 12px', borderRadius: '4px', outline: 'none', fontSize: '12px', cursor: 'pointer' }}
                >
                    <option value="ALL">All Statuses</option>
                    <option value="TARGET">Target</option>
                    <option value="PENDING">Pending</option>
                    <option value="APPLIED">Applied</option>
                    <option value="INTERVIEW">Interview</option>
                    <option value="REJECTED">Rejected</option>
                </select>
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {filteredAndSortedJobs.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#666', fontSize: '13px' }}>
                      No requisitions match your current filters.
                  </div>
              ) : (
                  filteredAndSortedJobs.map((job, idx) => {
                    let statusColor = '#444';
                    if (job.status === 'TARGET') statusColor = 'var(--accent)';
                    if (job.status === 'APPLIED') statusColor = 'var(--applied)';
                    if (job.status === 'INTERVIEW') statusColor = 'var(--interview)';
                    
                    return (
                      <div 
                        key={idx} 
                        onClick={() => setSelectedJob(job)}
                        style={{ background: '#111', border: `1px solid ${statusColor}`, borderRadius: '6px', padding: '15px', cursor: 'pointer', transition: 'transform 0.1s', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                        onMouseOver={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                        onMouseOut={e => e.currentTarget.style.transform = 'translateY(0)'}
                      >
                        <div>
                          <div style={{ fontSize: '15px', fontWeight: 'bold', color: '#fff', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            {job.title}
                            {job.starred === 1 && <Star size={12} color="gold" fill="gold" />}
                          </div>
                          <div style={{ fontSize: '12px', color: '#888', display: 'flex', gap: '15px' }}>
                            <span>Score: <strong style={{color: statusColor}}>{job.score}</strong></span>
                            <span>{job.location}</span>
                            <span>{new Date(job.found_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          {job.status === 'REJECTED' && (
                              <button 
                                  onClick={(e) => handleRestoreJob(e, job.id)}
                                  style={{ 
                                      background: 'rgba(0, 255, 157, 0.1)', color: 'var(--accent)', border: '1px solid var(--accent)', 
                                      padding: '4px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '10px', fontWeight: 'bold', 
                                      display: 'flex', alignItems: 'center', gap: '4px', transition: 'all 0.2s' 
                                  }}
                                  title="Mark as Target"
                                  onMouseOver={e => { e.currentTarget.style.background = 'var(--accent)'; e.currentTarget.style.color = '#000'; }}
                                  onMouseOut={e => { e.currentTarget.style.background = 'rgba(0, 255, 157, 0.1)'; e.currentTarget.style.color = 'var(--accent)'; }}
                              >
                                  <CheckSquare size={12} /> RESTORE
                              </button>
                          )}
                          <div style={{ fontSize: '10px', fontWeight: 'bold', background: statusColor, color: '#000', padding: '4px 10px', borderRadius: '3px' }}>
                            {job.status}
                          </div>
                        </div>
                      </div>
                    )
                  })
              )}
            </div>
          </>
        )}
      </div>

      {selectedJob && (
        <JobModal 
          job={selectedJob} 
          onClose={() => setSelectedJob(null)}
          onUpdateStatus={(id, status) => {
              setCompanyJobs(prev => prev.map(j => j.id === id ? {...j, status} : j));
              fetchCompanies(); // Refresh left pane counters if status changes in modal
          }}
          onToggleStar={() => {}}
        />
      )}
    </div>
  );
}