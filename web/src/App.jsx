import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, KanbanSquare, UserCircle2, Power } from 'lucide-react';
import Feed from './pages/feed';
import Board from './pages/board';
import Profile from './pages/profile';

function Layout({ children }) {
  const [isActive, setIsActive] = useState(false);

  // Poll Agent State
  useEffect(() => {
    fetch('/api/agent_state')
        .then(res => res.json())
        .then(data => setIsActive(data.active))
        .catch(() => {});
        
    const interval = setInterval(() => {
      fetch('/api/agent_state')
        .then(res => res.json())
        .then(data => setIsActive(data.active))
        .catch(() => {});
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Toggle Agent State
  const toggleAgent = async () => {
    const newState = !isActive;
    setIsActive(newState); // Optimistic UI update
    
    try {
        await fetch('/api/agent_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: newState })
        });
    } catch (e) {
        console.error("Failed to toggle agent state:", e);
        setIsActive(!newState); // Revert on failure
    }
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
      {/* Sidebar */}
      <div style={{ width: '220px', background: '#080808', borderRight: '1px solid #222', padding: '20px', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ color: '#fff', fontSize: '14px', borderBottom: '1px solid #333', paddingBottom: '15px', marginTop: 0 }}>
          <span style={{ color: 'var(--accent)', marginRight: '8px' }}>●</span>
          SYSTEM CNS
        </h2>
        
        <nav style={{ flexGrow: 1 }}>
          <NavLink to="/" style={navStyle}>
            <LayoutDashboard size={18} /> LIVE FEED
          </NavLink>
          <NavLink to="/board" style={navStyle}>
            <KanbanSquare size={18} /> WAR ROOM
          </NavLink>
          <NavLink to="/profile" style={navStyle}>
            <UserCircle2 size={18} /> PROFILE
          </NavLink>
        </nav>

        {/* --- SYSTEM POWER TOGGLE --- */}
        <div 
            onClick={toggleAgent}
            style={{ 
                marginTop: 'auto', 
                marginBottom: '15px',
                padding: '15px', 
                background: isActive ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255, 0, 85, 0.1)', 
                border: `1px solid ${isActive ? 'var(--accent)' : 'var(--danger)'}`, 
                borderRadius: '4px', 
                cursor: 'pointer', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '8px', 
                color: isActive ? 'var(--accent)' : 'var(--danger)', 
                fontWeight: 'bold', 
                fontSize: '12px',
                transition: 'all 0.2s'
            }} 
            title={isActive ? "Click to Pause Scraping" : "Click to Start Scraping"}
        >
            <Power size={14} /> 
            {isActive ? 'AGENT: ACTIVE' : 'AGENT: OFFLINE'}
        </div>

        <div style={{ fontSize: '10px', color: '#444' }}>
          v2.2.0 // DECOUPLED UI
        </div>
      </div>

      {/* Main Content */}
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
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;