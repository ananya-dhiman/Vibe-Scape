import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import cafeImg from '../assets/cafe.jpg';
import parkImg from '../assets/park.jpg';
import gymImg from '../assets/gym.jpg';
import restaurantImg from '../assets/restaurant.jpg';

const getFallbackImage = (category: string = '') => {
  const cat = category.toLowerCase();
  if (cat.includes('cafe')) return cafeImg;
  if (cat.includes('restaurant')) return restaurantImg;
  if (cat.includes('park')) return parkImg;
  if (cat.includes('gym')) return gymImg;
  return cafeImg;
};

const WishList: React.FC = () => {
  const { user, getUserToken } = useAuth();
  const [places, setPlaces] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWishlist = async () => {
      if (!user) return;
      setLoading(true);
      setError('');
      const token = await getUserToken();
      try {
        const res = await fetch(`http://localhost:5000/api/users/${user.uid}/wishlist`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setPlaces(data.wishlist || []);
      } catch (err) {
        setError('Failed to load wishlist');
      } finally {
        setLoading(false);
      }
    };
    fetchWishlist();
  }, [user, getUserToken]);

  if (!user) return null;

  return (
    <div style={{ fontFamily: 'Big Shoulders Display, sans-serif', background: '#fafafa', minHeight: '100vh', padding: '1rem', maxWidth: 420, margin: '0 auto', width: '100%', position: 'relative' }}>
      {/* Header with user photo and back button */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem', justifyContent: 'space-between' }}>
        <button onClick={() => navigate('/dashboard')} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer', color: '#222' }}>&larr;</button>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
          <div
            style={{ 
              width: 56, 
              height: 56, 
              borderRadius: '50%', 
              overflow: 'hidden', 
              border: '3px solid #ff8686', 
              cursor: 'pointer', 
              background: '#ff8686',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#222',
              fontWeight: 'bold',
              fontSize: '20px',
              transition: 'transform 0.2s'
            }}
            onClick={() => navigate('/wishlist')}
            title={user.displayName || user.email || 'User'}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {user.photoURL ? (
              <img
                src={user.photoURL}
                alt="User"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement;
                  if (parent) {
                    parent.textContent = user.displayName?.charAt(0) || user.email?.charAt(0) || 'U';
                  }
                }}
              />
            ) : (
              user.displayName?.charAt(0) || user.email?.charAt(0) || 'U'
            )}
          </div>
        </div>
        <div style={{ width: 40 }}></div> {/* Spacer for symmetry */}
      </div>
      <h2 style={{ textAlign: 'center', fontWeight: 700, fontSize: 28, marginBottom: 18 }}>My Wishlist</h2>
      {loading && <div style={{ textAlign: 'center', color: '#888' }}>Loading...</div>}
      {error && <div style={{ color: 'red', textAlign: 'center', marginBottom: 12 }}>{error}</div>}
      <div id="results" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {places.length === 0 && !loading && !error && (
          <div style={{ color: '#aaa', textAlign: 'center' }}>No places in your wishlist yet.</div>
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
    </div>
  );
};

export default WishList;
