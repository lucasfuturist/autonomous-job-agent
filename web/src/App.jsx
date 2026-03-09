import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, KanbanSquare, UserCircle2, Power, Terminal, Users, Building2 } from 'lucide-react';
import Feed from './pages/feed';
import Board from './pages/board';
import Profile from './pages/profile';
import Network from './pages/network'; 
import Companies from './pages/companies'; // <-- New Import

function Layout({ children }) {
  const [isActive, setIsActive] = useState(false);
  const [activityLog, setActivityLog] = useState({ source: "SYSTEM", message: "Connecting..." });

  useEffect(() => {
    let isMounted = true;
    const fetchState = () => {
        fetch('/api/agent_state')
            .then(res => res.json())
            .then(data => {
                if (!isMounted) return;
                setIsActive(data.active);
                if (data.activity) setActivityLog(data.activity);
                else setActivityLog({ source: "SYSTEM", message: "Waiting for signal..." });
            })
            .catch((e) => {
                if (!isMounted) return;
                setActivityLog({ source: "ERROR", message: "Backend Disconnected" });
            });
    };

    fetchState();
    const interval = setInterval(fetchState, 2000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  const toggleAgent = async () => {
    const newState = !isActive;
    setIsActive(newState); 
    try {
        await fetch('/api/agent_state', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: newState })
        });
    } catch (e) { setIsActive(!newState); }
  };

  const navStyle = ({ isActive }) => ({
    display: 'flex', alignItems: 'center', gap: '10px',
    padding: '12px 15px', color: isActive ? '#000' : '#888',
    background: isActive ? 'var(--accent)' : 'transparent',
    textDecoration: 'none', fontWeight: 'bold', borderRadius: '4px',
    marginBottom: '5px', transition: 'all 0.2s'
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <div style={{ width: '250px', background: '#080808', borderRight: '1px solid #222', padding: '20px', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ color: '#fff', fontSize: '14px', borderBottom: '1px solid #333', paddingBottom: '15px', marginTop: 0 }}>
          <span style={{ color: 'var(--accent)', marginRight: '8px' }}>●</span>
          SYSTEM CNS
        </h2>
        
        <nav style={{ flexGrow: 1 }}>
          <NavLink to="/" style={navStyle}><LayoutDashboard size={18} /> LIVE FEED</NavLink>
          <NavLink to="/board" style={navStyle}><KanbanSquare size={18} /> WAR ROOM</NavLink>
          <NavLink to="/companies" style={navStyle}><Building2 size={18} /> STRATEGY</NavLink> {/* <-- New Link */}
          <NavLink to="/network" style={navStyle}><Users size={18} /> NETWORK</NavLink> 
          <NavLink to="/profile" style={navStyle}><UserCircle2 size={18} /> PROFILE</NavLink>

          <div style={{ marginTop: '20px', background: '#000', border: '1px solid #222', padding: '10px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>
             <div style={{ color: '#666', marginBottom: '5px', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 'bold' }}><Terminal size={10} /> ACTIVITY LOG</div>
             <div style={{ color: 'var(--accent)', marginBottom: '2px', fontWeight: 'bold' }}>{">"} {activityLog.source}</div>
             <div style={{ color: '#ccc', lineHeight: '1.4' }}>{activityLog.message}<span className="blink-cursor">_</span></div>
          </div>
        </nav>

        <div onClick={toggleAgent}
            style={{ 
                marginTop: 'auto', marginBottom: '15px', padding: '15px', 
                background: isActive ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255, 0, 85, 0.1)', 
                border: `1px solid ${isActive ? 'var(--accent)' : 'var(--danger)'}`, 
                borderRadius: '4px', cursor: 'pointer', display: 'flex', alignItems: 'center', 
                justifyContent: 'center', gap: '8px', color: isActive ? 'var(--accent)' : 'var(--danger)', 
                fontWeight: 'bold', fontSize: '12px', transition: 'all 0.2s'
            }}>
            <Power size={14} /> {isActive ? 'AGENT: ACTIVE' : 'AGENT: OFFLINE'}
        </div>
      </div>
      <div style={{ flexGrow: 1, padding: '20px', overflowY: 'auto', maxHeight: '100vh' }}>
        {children}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/board" element={<Board />} />
          <Route path="/companies" element={<Companies />} /> {/* <-- New Route */}
          <Route path="/network" element={<Network />} /> 
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;