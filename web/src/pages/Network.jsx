import React, { useState, useEffect } from 'react';
import { Users, Search, Building2, Clock, Mail, CheckCircle2, MessageSquare, ExternalLink, XCircle, PenLine, Save, X, Phone, FileText } from 'lucide-react';

// --- SUB-COMPONENT: Individual Contact Card ---
const ContactCard = ({ rec, onRefresh, toggleReply, getDaysAgoText }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...rec });

  // Sync local form state if the parent data changes
  useEffect(() => {
    setFormData({ ...rec });
  }, [rec]);

  const handleSave = async () => {
    try {
      const res = await fetch('/api/recruiters/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          job_id: rec.job_id, 
          old_id: rec.url || rec.email, // Backend uses this to find the right object in the array
          contact: formData 
        })
      });
      if (res.ok) {
        setIsEditing(false);
        onRefresh();
      }
    } catch (e) {
      console.error("Failed to update contact:", e);
    }
  };

  if (isEditing) {
    return (
      <div style={{ background: '#111', border: '1px solid var(--accent)', borderRadius: '6px', overflow: 'hidden', padding: '15px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
          <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <PenLine size={14} /> EDITING PROFILE
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button onClick={handleSave} style={{ background: 'var(--accent)', color: '#000', border: 'none', padding: '4px 10px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}><Save size={12} /> SAVE</button>
            <button onClick={() => { setIsEditing(false); setFormData({ ...rec }); }} style={{ background: '#333', color: '#fff', border: 'none', padding: '4px 10px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}><X size={12} /> CANCEL</button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
          <div>
            <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>FULL NAME</div>
            <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none' }} />
          </div>
          <div>
            <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>JOB TITLE</div>
            <input type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none' }} />
          </div>
          <div>
            <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>EMAIL</div>
            <input type="text" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none' }} />
          </div>
          <div>
            <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>PHONE</div>
            <input type="text" value={formData.phone || ''} onChange={e => setFormData({...formData, phone: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none' }} />
          </div>
        </div>

        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>LINKEDIN URL</div>
          <input type="text" value={formData.url} onChange={e => setFormData({...formData, url: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none' }} />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>OUTREACH PAYLOAD (MESSAGE SENT)</div>
          <textarea value={formData.message_sent} onChange={e => setFormData({...formData, message_sent: e.target.value})} style={{ width: '100%', background: '#000', border: '1px solid #333', color: '#ccc', padding: '8px', borderRadius: '4px', fontSize: '11px', outline: 'none', minHeight: '60px', resize: 'vertical', fontFamily: 'monospace' }} />
        </div>

        <div>
          <div style={{ fontSize: '9px', color: '#666', marginBottom: '4px' }}>INTERNAL NOTES & HISTORY</div>
          <textarea value={formData.history || ''} onChange={e => setFormData({...formData, history: e.target.value})} placeholder="Log call details, next steps, or specific friction points here..." style={{ width: '100%', background: 'rgba(0, 255, 157, 0.02)', border: '1px solid #333', color: '#fff', padding: '8px', borderRadius: '4px', fontSize: '12px', outline: 'none', minHeight: '80px', resize: 'vertical' }} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: '#111', border: rec.replied ? '1px solid var(--accent)' : '1px solid #333', borderRadius: '6px', overflow: 'hidden' }}>
      {/* Contact Info Header */}
      <div style={{ padding: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', background: rec.replied ? 'rgba(0, 255, 157, 0.05)' : 'transparent' }}>
        <div>
          <div style={{ fontSize: '15px', fontWeight: 'bold', color: '#fff', marginBottom: '4px' }}>
            {rec.name} <span style={{ color: '#888', fontWeight: 'normal', fontSize: '13px' }}>- {rec.title}</span>
          </div>
          <div style={{ display: 'flex', gap: '15px', fontSize: '11px', color: '#aaa', marginTop: '8px', flexWrap: 'wrap' }}>
            {rec.email && <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Mail size={12} /> {rec.email}</span>}
            {rec.phone && <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Phone size={12} /> {rec.phone}</span>}
            {rec.url && (
              <a href={rec.url} target="_blank" rel="noreferrer" style={{color: 'var(--accent)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px'}}>
                <ExternalLink size={12} /> LinkedIn Profile
              </a>
            )}
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            onClick={() => setIsEditing(true)}
            style={{ background: 'transparent', color: '#666', border: '1px solid #333', padding: '6px', borderRadius: '4px', cursor: 'pointer', transition: 'all 0.2s' }}
            title="Edit Profile"
          >
            <PenLine size={14} />
          </button>
          <button 
            onClick={() => toggleReply(rec)}
            style={{ 
              background: rec.replied ? 'var(--accent)' : '#222', color: rec.replied ? '#000' : '#888', 
              border: `1px solid ${rec.replied ? 'var(--accent)' : '#444'}`, padding: '6px 12px', borderRadius: '4px', 
              cursor: 'pointer', fontSize: '10px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px',
              transition: 'all 0.2s'
            }}
          >
            {rec.replied ? <CheckCircle2 size={14} /> : <MessageSquare size={14} />} 
            {rec.replied ? "REPLIED" : "MARK REPLIED"}
          </button>
        </div>
      </div>

      {/* Associated Job Context */}
      <div style={{ padding: '8px 15px', background: '#0a0a0a', borderTop: '1px solid #222', borderBottom: '1px solid #222', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#666' }}>Target Role:</span>
        <a href={rec.job_url} target="_blank" rel="noreferrer" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold', borderBottom: '1px dotted #555' }}>
          {rec.job_title}
        </a>
      </div>

      {/* Payload & Notes Split */}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '15px', fontSize: '11px', color: '#ccc' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: '#666', fontWeight: 'bold' }}>OUTREACH PAYLOAD</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: rec.contacted_date ? 'var(--accent)' : '#666' }}>
              <Clock size={12} /> {rec.contacted_date ? `Sent ${getDaysAgoText(rec.contacted_date)}` : "Not Sent"}
            </span>
          </div>
          {rec.message_sent ? (
            <div style={{ background: '#000', padding: '12px', borderRadius: '4px', borderLeft: '3px solid #333', fontStyle: 'italic', lineHeight: '1.5' }}>
              "{rec.message_sent}"
            </div>
          ) : (
            <div style={{ fontStyle: 'italic', color: '#666' }}>No message payload recorded.</div>
          )}
        </div>

        {rec.history && (
          <div style={{ padding: '15px', borderTop: '1px dotted #222', background: '#0d0d0d' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#888', fontWeight: 'bold', fontSize: '10px', marginBottom: '8px' }}>
              <FileText size={12} /> INTERNAL NOTES
            </div>
            <div style={{ color: '#eee', fontSize: '12px', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
              {rec.history}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};


// --- MAIN COMPONENT ---
export default function Network() {
  const [contacts, setContacts] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCompany, setSelectedCompany] = useState(null);
  
  // Sort State
  const [sortOption, setSortOption] = useState("CONNECTIONS_DESC");

  const fetchNetwork = () => {
    fetch('/api/network')
      .then(res => res.json())
      .then(data => setContacts(data || []))
      .catch(err => console.error("Failed to load network:", err));
  };

  useEffect(() => {
    fetchNetwork();
  }, []);

  const toggleReply = async (rec) => {
    try {
        const res = await fetch('/api/recruiters/reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: rec.job_id, url: rec.url || rec.email, replied: !rec.replied })
        });
        if (res.ok) {
            fetchNetwork();
        }
    } catch (e) {
        console.error("Failed to update reply status:", e);
    }
  };

  // --- 1. GROUP DATA BY COMPANY ---
  const companiesMap = {};
  contacts.forEach(c => {
      if (!companiesMap[c.company]) {
          companiesMap[c.company] = { 
              company: c.company, 
              recruiters: [], 
              lastOutreach: null 
          };
      }
      companiesMap[c.company].recruiters.push(c);
      
      if (c.contacted_date) {
          const d = new Date(c.contacted_date);
          if (!companiesMap[c.company].lastOutreach || d > companiesMap[c.company].lastOutreach) {
              companiesMap[c.company].lastOutreach = d;
          }
      }
  });

  let groupedCompanies = Object.values(companiesMap);

  // --- 2. FILTER DATA ---
  if (searchTerm) {
      groupedCompanies = groupedCompanies.filter(c => 
          c.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
          c.recruiters.some(r => r.name.toLowerCase().includes(searchTerm.toLowerCase()))
      );
  }

  // --- 3. SORT DATA ---
  groupedCompanies.sort((a, b) => {
      if (sortOption === "CONNECTIONS_DESC") {
          return b.recruiters.length - a.recruiters.length;
      }
      if (sortOption === "OUTREACH_RECENT") {
          return (b.lastOutreach || 0) - (a.lastOutreach || 0);
      }
      if (sortOption === "OUTREACH_OLDEST") {
          if (!a.lastOutreach) return 1; // Push nulls to the bottom
          if (!b.lastOutreach) return -1;
          return a.lastOutreach - b.lastOutreach;
      }
      return 0;
  });

  const getDaysAgoText = (dateStr) => {
      if (!dateStr) return "Never";
      const date = new Date(dateStr);
      const diffTime = Math.abs(new Date() - date);
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays === 0) return "Today";
      if (diffDays === 1) return "1d ago";
      return `${diffDays}d ago`;
  };

  const activeCompanyData = groupedCompanies.find(c => c.company === selectedCompany);

  return (
    <div style={{ display: 'flex', height: '100%', gap: '20px' }} className="fade-in">
      
      {/* LEFT PANE: Network Roster */}
      <div style={{ width: '35%', display: 'flex', flexDirection: 'column', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', overflow: 'hidden' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #222', background: '#111' }}>
          <h2 style={{ margin: '0 0 15px 0', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: '#fff' }}>
            <Users size={18} color="var(--accent)" /> CRM ROSTER
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', background: '#000', border: '1px solid #333', borderRadius: '4px', padding: '8px 12px', alignItems: 'center', gap: '8px' }}>
                <Search size={14} color="#666" />
                <input 
                  type="text" 
                  placeholder="Search companies or names..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#fff', width: '100%', outline: 'none', fontSize: '12px' }}
                />
              </div>

              <select 
                  value={sortOption} 
                  onChange={e => setSortOption(e.target.value)}
                  style={{ background: '#000', border: '1px solid #333', color: '#fff', padding: '8px 12px', borderRadius: '4px', outline: 'none', fontSize: '12px', cursor: 'pointer' }}
              >
                  <option value="CONNECTIONS_DESC">Sort: Volume (High-Low)</option>
                  <option value="OUTREACH_RECENT">Sort: Recent Outreach</option>
                  <option value="OUTREACH_OLDEST">Sort: Oldest Outreach</option>
              </select>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          {groupedCompanies.length === 0 ? (
              <div style={{ padding: '30px 20px', textAlign: 'center', color: '#666', fontSize: '12px' }}>
                  No contacts found in your network.
              </div>
          ) : (
              groupedCompanies.map((c, i) => (
                <div 
                  key={i} 
                  onClick={() => setSelectedCompany(c.company)}
                  style={{ 
                    padding: '15px 20px', borderBottom: '1px solid #222', cursor: 'pointer', 
                    background: selectedCompany === c.company ? '#1a1a1a' : 'transparent',
                    borderLeft: selectedCompany === c.company ? '3px solid var(--accent)' : '3px solid transparent',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold', color: selectedCompany === c.company ? 'var(--accent)' : '#fff', fontSize: '14px' }}>{c.company}</span>
                    <span style={{ fontSize: '11px', background: '#222', padding: '2px 8px', borderRadius: '12px', color: '#aaa' }}>{c.recruiters.length} Targets</span>
                  </div>
                  <div style={{ display: 'flex', gap: '15px', fontSize: '11px', color: '#666', alignItems: 'center' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={12} color={c.lastOutreach ? 'var(--accent)' : '#666'} /> 
                        {c.lastOutreach ? getDaysAgoText(c.lastOutreach) : "Pending"}
                    </span>
                  </div>
                </div>
              ))
          )}
        </div>
      </div>

      {/* RIGHT PANE: Selected Company Detail */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#0a0a0a', border: '1px solid #222', borderRadius: '8px', overflow: 'hidden' }}>
        {!activeCompanyData ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#444' }}>
            <Users size={48} style={{ marginBottom: '15px', opacity: 0.5 }} />
            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>SELECT A NETWORK NODE</div>
            <div style={{ fontSize: '12px', marginTop: '5px' }}>Review active outreach threads for specific companies.</div>
          </div>
        ) : (
          <>
            <div style={{ padding: '20px', borderBottom: '1px solid #222', background: '#111', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: '0 0 5px 0', fontSize: '20px', color: '#fff', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Building2 size={20} /> {activeCompanyData.company}
                </h2>
                <div style={{ fontSize: '12px', color: '#888' }}>{activeCompanyData.recruiters.length} Tracked Connections</div>
              </div>
              <button 
                  onClick={() => setSelectedCompany(null)}
                  style={{ background: '#222', border: '1px solid #444', color: '#fff', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s' }}
                  title="Clear Selection"
              >
                  <XCircle size={14} /> CLEAR
              </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {activeCompanyData.recruiters.map((rec, idx) => (
                  <ContactCard 
                    key={idx} 
                    rec={rec} 
                    onRefresh={fetchNetwork} 
                    toggleReply={toggleReply} 
                    getDaysAgoText={getDaysAgoText} 
                  />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}