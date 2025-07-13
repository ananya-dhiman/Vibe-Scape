import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

const FeedBack: React.FC = () => {
  const [vibe, setVibe] = useState('');
  const [emoji, setEmoji] = useState('');
  const [feedback, setFeedback] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // No backend call, just go back to dashboard
    navigate('/dashboard');
  };

  return (
    <div style={{ fontFamily: 'Big Shoulders Display, sans-serif', background: '#fff', minHeight: '100vh', padding: '1.5rem 1rem 1rem 1rem', maxWidth: 420, margin: '0 auto', width: '100%', position: 'relative' }}>
      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <button onClick={() => navigate('/dashboard')} style={{ background: 'none', border: 'none', fontSize: 28, cursor: 'pointer', color: '#222', padding: 0, marginRight: 8 }}>&larr;</button>
      
      </div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: 16 , fontFamily: 'Big Shoulders Display, sans-serif'}}>
        <div>
          <label style={{ fontWeight: 700, fontSize: 16, color: '#111', letterSpacing: 1 }}>VIBE OF THE PLACE?</label>
          <input
            type="text"
            value={vibe}
            onChange={e => setVibe(e.target.value)}
            style={{ width: '100%', marginTop: 8, padding: '0.9rem 1.2rem', borderRadius: 24, border: 'none', background: '#fff', boxShadow: '0 2px 8px #eee', fontSize: 16, outline: 'none' }}
          />
        </div>
        <div>
          <label style={{ fontWeight: 700, fontSize: 16, color: '#111', letterSpacing: 1 }}>EMOJI TO DESCRIBE THE PLACE?</label>
          <input
            type="text"
            value={emoji}
            onChange={e => setEmoji(e.target.value)}
            style={{ width: '100%', marginTop: 8, padding: '0.9rem 1.2rem', borderRadius: 24, border: 'none', background: '#fff', boxShadow: '0 2px 8px #eee', fontSize: 16, outline: 'none' }}
          />
        </div>
        <div>
          <label style={{ fontWeight: 700, fontSize: 16, color: '#111', letterSpacing: 1 }}>OVERALL FEEDBACK</label>
          <input
            type="text"
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            style={{ width: '100%', marginTop: 8, padding: '0.9rem 1.2rem', borderRadius: 24, border: 'none', background: '#fff', boxShadow: '0 2px 8px #eee', fontSize: 16, outline: 'none' }}
          />
        </div>
        <button type="submit" style={{ marginTop: 8, padding: '0.7rem 0', borderRadius: 20, background: '#111', color: '#FFC857', fontWeight: 700, fontSize: 18, border: 'none', width: 160, alignSelf: 'center', boxShadow: '0 2px 8px #bbb', letterSpacing: 1 }}>SUBMIT</button>
      </form>
      {/* Floating bot icon */}
      <div
        onClick={() => navigate('/bot')}
        style={{
          position: 'fixed',
          right: 24,
          bottom: 24,
          width: 56,
          height: 56,
          borderRadius: '16px',
          background: '#eee',
          boxShadow: '0 2px 12px #bbb',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          zIndex: 1000
        }}
      >
        <img src={logo} alt="Logo" style={{ width: 100, height: 60,borderRadius: '50%',
    objectFit: 'cover' }} />
      </div>
    </div>
  );
};

export default FeedBack;
