import React, { useState, useEffect } from 'react';
import logo from '../assets/logo.png';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import cafeImg from '../assets/cafe.jpg';
import parkImg from '../assets/park.jpg';
import gymImg from '../assets/gym.jpg';
import restaurantImg from '../assets/restaurant.jpg';

// Import Google Fonts (Big Shoulders Display)
const fontLink = document.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700&display=swap';
fontLink.rel = 'stylesheet';
document.head.appendChild(fontLink);

const Dashboard: React.FC = () => {
  const [city, setCity] = useState(''); 
  const [category, setCategory] = useState('');
  const [vibeTags, setVibeTags] = useState<string[]>([]);
  const [vibeInput, setVibeInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [places, setPlaces] = useState<any[]>([]);
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };

  useEffect(() => {
    // Fetch all places on mount
    setLoading(true);
    fetch('http://localhost:5000/api/places/')
      .then(res => res.json())
      .then(data => {
        setPlaces(data.places || []);
        setLoading(false);
      })
      .catch(err => {
        console.log(err); 
        setError('Failed to load places');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    // Only run if city is not already set
    if (city) return;

    if (!navigator.geolocation) {
      console.log('Geolocation not supported');
      return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`
        );
        if (response.ok) {
          const data = await response.json();
          if (data.address) {
            const cityName =
              data.address.city ||
              data.address.town ||
              data.address.village ||
              data.address.county ||
              data.address.state;
            if (cityName) setCity(cityName);
          }
        }
      } catch (error) {
        console.log('City detection error:', error);
      }
    }, (error) => {
      console.log('Geolocation error:', error);
    });
  }, [city]);

  const handleAddVibe = (e: React.KeyboardEvent | React.MouseEvent) => {
    if (
      (e as React.KeyboardEvent).key === 'Enter' ||
      (e as React.MouseEvent).type === 'click'
    ) {
      e.preventDefault();
      const tag = vibeInput.trim();
      if (tag && !vibeTags.includes(tag)) {
        setVibeTags([...vibeTags, tag]);
      }
      setVibeInput('');
    }
  };

  const handleRemoveVibe = (tag: string) => {
    setVibeTags(vibeTags.filter(v => v !== tag));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setPlaces([]);
    try {
      const res = await fetch('http://localhost:5000/api/fallback/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, category, vibe_tags: vibeTags, min_results: 5 })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Unknown error');
      setPlaces(data.places || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch');
    } finally {
      setLoading(false);
    }
  };

  const getFallbackImage = (category: string = '') => {
    const cat = category.toLowerCase();
    if (cat.includes('cafe')) return cafeImg;
    if (cat.includes('restaurant')) return restaurantImg;
    if (cat.includes('park')) return parkImg;
    if (cat.includes('gym')) return gymImg;
    return cafeImg; // default fallback
  };

  return (
    <div style={{ fontFamily: 'Big Shoulders Display, sans-serif', background: '#fafafa', minHeight: '100vh', padding: '1rem', maxWidth: 420, margin: '0 auto', width: '100%', position: 'relative' }}>
      {/* Header with user info and logout */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <img src={logo} alt="Logo" style={{ height: 32 }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {user && (
            <>
              <div 
                onClick={() => navigate('/wishlist')}
                style={{ 
                  cursor: 'pointer',
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  overflow: 'hidden',
                  border: '2px solid #ff8686',
                  transition: 'transform 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <img
                  src={user.photoURL || 'https://via.placeholder.com/40x40/ff8686/222?text=' + (user.displayName?.charAt(0) || user.email?.charAt(0) || 'U')}
                  alt="User"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = 'https://via.placeholder.com/40x40/ff8686/222?text=' + (user.displayName?.charAt(0) || user.email?.charAt(0) || 'U');
                  }}
                />
              </div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>
                {user.displayName || user.email}
              </div>
            </>
          )}
          <button
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '1rem',
              background: '#ff8686',
              color: '#222',
              border: 'none',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <input
          type="text"
          placeholder="City (e.g. Delhi)"
          value={city}
          onChange={e => setCity(e.target.value)}
          style={{ padding: '0.75rem', borderRadius: '1.5rem', border: '1px solid #eee', fontSize: '1rem' }}
          required
        />
        <input
          type="text"
          placeholder="Category (e.g. cafes)"
          value={category}
          onChange={e => setCategory(e.target.value)}
          style={{ padding: '0.75rem', borderRadius: '1.5rem', border: '1px solid #eee', fontSize: '1rem' }}
          required
        />
        <div style={{ background: '#fff', borderRadius: '1.2rem', padding: '0.7rem 1rem', boxShadow: '0 2px 8px #eee', marginBottom: 0 }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 6, color: '#222' }}>Vibes</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: 8 }}>
            {vibeTags.map(tag => (
              <span key={tag} style={{ background: '#ff8686', color: '#222', borderRadius: '2rem', padding: '0.5rem 1.2rem', fontWeight: 700, fontSize: '1.1rem', display: 'flex', alignItems: 'center' }}>
                {tag}
                <span
                  style={{ marginLeft: 8, cursor: 'pointer', fontWeight: 700 }}
                  onClick={() => handleRemoveVibe(tag)}
                >
                  ×
                </span>
              </span>
            ))}
            <input
              type="text"
              value={vibeInput}
              onChange={e => setVibeInput(e.target.value)}
              onKeyDown={handleAddVibe}
              placeholder="Add vibe..."
              style={{
                border: 'none',
                outline: 'none',
                fontSize: '1.1rem',
                fontFamily: 'Big Shoulders Display, sans-serif',
                minWidth: 80,
                background: 'transparent',
                marginLeft: 4
              }}
            />
       
          </div>
        </div>
        <button type="submit" style={{ padding: '0.75rem', borderRadius: '1.5rem', background: '#222', color: '#fff', fontWeight: 700, fontSize: '1rem', border: 'none' }} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
      <div id="results" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {places.length === 0 && !loading && !error && (
          <div style={{ color: '#aaa', textAlign: 'center' }}>No results yet. Try searching!</div>
        )}
        {places.map((place, idx) => (
          <div
            key={place._id || place.original?.fsq_id || idx}
            style={{
              background: '#ddd',
              borderRadius: '2rem',
              padding: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1.5rem',
              boxShadow: '0 2px 8px #eee',
              minHeight: 160,
              cursor: 'pointer',
              transition: 'box-shadow 0.15s',
            }}
            onClick={() => navigate(`/place/${place._id}`)}
          >
            {/* Left: Info */}
            <div style={{ flex: 2, minWidth: 0 }}>
              <div style={{ color: '#222', fontSize: '1.1rem', marginBottom: 4 }}>{place.original?.locality} {place.original?.city}</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: 1, lineHeight: 1 }}>{place.original?.name}</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, margin: '0.5rem 0', display: 'inline-block' }}>75%</div>
              <div style={{ display: 'flex', gap: '1rem', margin: '1rem 0 0.5rem 0' }}>
                {(place.processed?.vibe_tags || []).slice(0, 2).map((tag: string) => (
                  <span key={tag} style={{ background: '#ff8686', color: '#222', borderRadius: '2rem', padding: '0.5rem 1.2rem', fontWeight: 700, fontSize: '1.1rem', marginRight: 8 }}>{tag}</span>
                ))}
              </div>
            </div>
            {/* Center: Circle (photo placeholder or image) */}
            <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
              <div style={{ width: 100, height: 100, borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                <img
                  src={
                    place.original?.photo_url && place.original.photo_url.startsWith('http')
                      ? place.original.photo_url
                      : getFallbackImage(place.original?.category)
                  }
                  alt={place.original?.name || 'Place'}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={e => {
                    const target = e.target as HTMLImageElement;
                    target.onerror = null;
                    target.src = getFallbackImage(place.original?.category);
                  }}
                />
              </div>
            </div>
            {/* Right: Emojis and category */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, height: '100%' }}>
              {Array.isArray(place.processed?.emojis) && place.processed.emojis.length > 0 && (
                <div style={{ background: '#fff', borderRadius: '1.2rem', padding: '0.5rem 0.7rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                  {place.processed.emojis.map((emoji: string, i: number) => (
                    <span key={i} style={{ fontSize: '1.5rem' }}>{emoji}</span>
                  ))}
                </div>
              )}
              <div style={{ background: '#fff', borderRadius: '1.2rem', padding: '0.3rem 1.2rem', fontWeight: 600, fontSize: '1.1rem', marginTop: 12 }}>{place.original?.category}</div>
            </div>
          </div>
        ))}
      </div>
      <div
        onClick={() => navigate('/bot')}
        style={{
          position: 'fixed',
          right: 24,
          bottom: 24,
          width: 60,
          height: 60,
          borderRadius: '50%',
          background: 'black',
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

export default Dashboard;
