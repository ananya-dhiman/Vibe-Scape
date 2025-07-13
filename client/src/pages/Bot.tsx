import React, { useState, useRef, useEffect } from 'react';
import logo from '../assets/logo.png';

// Import Google Fonts (Big Shoulders Display)
const fontLink = document.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700&display=swap';
fontLink.rel = 'stylesheet';
document.head.appendChild(fontLink);

const BOT_FIRST_MESSAGE = 'Hii I am Viber';

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: BOT_FIRST_MESSAGE }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [places, setPlaces] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Set body background color
  useEffect(() => {
    const prev = document.body.style.background;
    document.body.style.background = '#ede5f3';
    return () => { document.body.style.background = prev; };
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages(msgs => [...msgs, { sender: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);
    setPlaces([]); // Clear previous places
    try {
      const res = await fetch('http://localhost:5000/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      });
      const data = await res.json();
      setMessages(msgs => [
        ...msgs,
        { sender: 'bot', text: data.response || 'Sorry, I did not understand that.' }
      ]);
      // Handle places data if present
      if (data.places && Array.isArray(data.places)) {
        setPlaces(data.places);
      }
    } catch (err) {
      setMessages(msgs => [
        ...msgs,
        { sender: 'bot', text: 'Sorry, there was an error. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'Big Shoulders Display, sans-serif', minHeight: '100vh', position: 'relative', maxWidth: 420, margin: '0 auto', width: '100%' }}>
      {/* Top bar with title */}
      <div style={{ width: '100%', padding: '1.2rem 0 0.5rem 0', textAlign: 'center' }}>
        <span style={{ fontSize: '2rem', fontWeight: 700, color: '#111', letterSpacing: 0.5 }}>Viber</span>
      </div>
      {/* Chat messages */}
      <div style={{ padding: '0.5rem 0.5rem 6.5rem 0.5rem', minHeight: '80vh', boxSizing: 'border-box' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: 18,
            alignItems: 'flex-end'
          }}>
            {msg.sender === 'bot' ? (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                boxShadow: '2px 4px 8px #d1c9d6',
                background: '#fff',
                borderRadius: '2rem',
                padding: '0.2rem 1.2rem 0.2rem 0.5rem',
                minHeight: 38,
                maxWidth: 260
              }}>
                <img src={logo} alt="bot" style={{ width: 55, height: 40, marginRight: 2, background: 'transparent', display: 'inline-block' }} />
                <span style={{ color: '#111', fontWeight: 700, fontSize: '1.1rem', letterSpacing: 0.2 }}>{msg.text}</span>
              </div>
            ) : (
              <div style={{
                background: '#fff',
                color: '#111',
                borderRadius: '2rem',
                padding: '0.2rem 1.2rem',
                minHeight: 38,
                maxWidth: 180,
                fontWeight: 700,
                fontSize: '1.1rem',
                boxShadow: '2px 4px 8px #d1c9d6',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'flex-end'
              }}>{msg.text}</div>
            )}
          </div>
        ))}
        
        {/* Place Cards Section */}
        {places.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <div style={{ 
              textAlign: 'center', 
              marginBottom: '1rem',
              fontSize: '1.2rem',
              fontWeight: 700,
              color: '#111'
            }}>
              Found {places.length} places for you:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {places.map((place, idx) => {
                // Support both nested (place.original) and flat structures
                const original = place.original || place;
                const processed = place.processed || place;
                const name = original?.name || place.name || 'Unknown Place';
                const city = original?.city || place.city || '';
                const locality = original?.locality || place.locality || '';
                const category = original?.category || place.category || '';
                const photo_url = original?.photo_url || place.photo_url || '/default_place.png';
                const vibe_tags = processed?.vibe_tags || [];
                const emojis = processed?.emojis || [];
                return (
                  <div key={place._id || original?.fsq_id || idx} style={{ 
                    background: '#ddd', 
                    borderRadius: '2rem', 
                    padding: '1.5rem', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '1.5rem', 
                    boxShadow: '0 2px 8px #eee', 
                    minHeight: 160 
                  }}>
                    {/* Left: Info */}
                    <div style={{ flex: 2, minWidth: 0 }}>
                      <div style={{ color: '#222', fontSize: '1.1rem', marginBottom: 4 }}>
                        {locality} {city}
                      </div>
                      <div style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: 1, lineHeight: 1 }}>
                        {name}
                      </div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0', display: 'inline-block' }}>
                        75%
                      </div>
                      <div style={{ display: 'flex', gap: '1rem', margin: '1rem 0 0.5rem 0' }}>
                        {(vibe_tags || []).slice(0, 2).map((tag: string) => (
                          <span key={tag} style={{ 
                            background: '#ff8686', 
                            color: '#222', 
                            borderRadius: '2rem', 
                            padding: '0.5rem 1.2rem', 
                            fontWeight: 700, 
                            fontSize: '1.1rem', 
                            marginRight: 8 
                          }}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    {/* Center: Circle (photo placeholder or image) */}
                    <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
                      <div style={{ 
                        width: 100, 
                        height: 100, 
                        borderRadius: '50%', 
                        background: '#fff', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        overflow: 'hidden' 
                      }}>
                        <img
                          src={photo_url}
                          alt={name}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      </div>
                    </div>
                    {/* Right: Emojis and category */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, height: '100%' }}>
                      {Array.isArray(emojis) && emojis.length > 0 && (
                        <div style={{ 
                          background: '#fff', 
                          borderRadius: '1.2rem', 
                          padding: '0.5rem 0.7rem', 
                          display: 'flex', 
                          flexDirection: 'column', 
                          alignItems: 'center', 
                          gap: 8 
                        }}>
                          {emojis.map((emoji: string, i: number) => (
                            <span key={i} style={{ fontSize: '1.5rem' }}>{emoji}</span>
                          ))}
                        </div>
                      )}
                      <div style={{ 
                        background: '#fff', 
                        borderRadius: '1.2rem', 
                        padding: '0.3rem 1.2rem', 
                        fontWeight: 600, 
                        fontSize: '1.1rem', 
                        marginTop: 12 
                      }}>
                        {category}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      {/* Chat input bar */}
      <form onSubmit={handleSend} style={{
        position: 'fixed',
        left: 0,
        right: 0,
        bottom: 0,
        background: 'transparent',
        zIndex: 10,
        maxWidth: 420,
        margin: '0 auto',
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        padding: '0 0 1.2rem 0'
      }}>
        <div style={{
          background: '#fff',
          borderRadius: '2rem',
          boxShadow: '2px 4px 8px #d1c9d6',
          display: 'flex',
          alignItems: 'center',
          width: '90%',
          maxWidth: 340,
          padding: '0.2rem 0.2rem 0.2rem 1rem',
          justifyContent: 'space-between'
        }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your query..."
            style={{
              border: 'none',
              outline: 'none',
              background: 'transparent',
              fontSize: '1.1rem',
              flex: 1,
              padding: '0.7rem 0',
              fontFamily: 'Big Shoulders Display, sans-serif',
              color: '#111',
              fontWeight: 700
            }}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()} style={{
            background: '#111',
            border: 'none',
            borderRadius: '50%',
            width: 36,
            height: 36,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginLeft: 8,
            cursor: loading ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 6px #bbb',
            color: '#fff',
            fontWeight: 700
          }}>
            <span style={{ color: '#fff', fontSize: 22, fontWeight: 700 }}>&#9654;</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chatbot; 