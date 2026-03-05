import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, KanbanSquare, UserCircle2, Settings } from 'lucide-react';
import Feed from './pages/Feed';
import Board from './pages/Board';
import Profile from './pages/Profile';

// --- SIDEBAR NAVIGATION LAYOUT ---
function Layout({ children }) {
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

        <div style={{ fontSize: '10px', color: '#444' }}>
          v2.1.0 // CRM SUITE
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