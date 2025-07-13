import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import cafeImg from '../assets/cafe.jpg';
import parkImg from '../assets/park.jpg';
import gymImg from '../assets/gym.jpg';
import restaurantImg from '../assets/restaurant.jpg';
import logo from '../assets/logo.png';


const getFallbackImage = (category: string = '') => {
  const cat = category.toLowerCase();
  if (cat.includes('cafe')) return cafeImg;
  if (cat.includes('restaurant')) return restaurantImg;
  if (cat.includes('park')) return parkImg;
  if (cat.includes('gym')) return gymImg;
  return cafeImg;
};

const Place: React.FC = () => {
  const { place_id } = useParams<{ place_id: string }>();
  const { user, getUserToken } = useAuth();
  const [place, setPlace] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  const [wishlistSuccess, setWishlistSuccess] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!place_id) return;
    setLoading(true);
    fetch(`http://localhost:5000/api/places/${place_id}`)
      .then(res => res.json())
      .then(data => {
        setPlace(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load place');
        setLoading(false);
      });
  }, [place_id]);

  const handleAddToWishlist = async () => {
    if (!user) return;
    setWishlistLoading(true);
    setWishlistSuccess(false);
    const token = await getUserToken();
    const res = await fetch(`http://localhost:5000/api/users/${user.uid}/wishlist/${place_id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (res.ok) {
      setWishlistSuccess(true);
    }
    setWishlistLoading(false);
  };

  if (loading) {
    return <div className="centered">Loading...</div>;
  }
  if (error || !place) {
    return <div className="centered error">{error || 'Place not found'}</div>;
  }

  const imgSrc = place.original?.photo_url && place.original.photo_url.startsWith('http')
    ? place.original.photo_url
    : getFallbackImage(place.original?.category);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@400;700&display=swap');

        body {
          font-family: 'Big Shoulders Display', sans-serif;
          margin: 0;
          background: #faf9fb;
        }

        .centered {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .error {
          color: red;
        }

        .page {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding-bottom: 32px;
        }

        .header {
          width: 100%;
          background: #111;
          border-radius: 0 0;
          padding: 16px 0 32px;
          position: relative;
          margin-bottom: 24px;
        }

        .back-btn {
          position: absolute;
          left: 16px;
          top: 16px;
          background: none;
          border: none;
          color: #fff;
          font-size: 22px;
          cursor: pointer;
        }

        .header-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-top: 16px;
        }

        .img-circle {
          width: 90px;
          height: 90px;
          border-radius: 50%;
          overflow: hidden;
          background: #fff;
          margin-bottom: 12px;
          border: 3px solid #fff;
        }

        .place-title {
          color: #fff;
          font-size: 2rem;
          font-weight: 700;
          letter-spacing: 1px;
        }

        .place-city {
          color: #fff;
          font-size: 1.1rem;
          margin-top: 2px;
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 10px;
        }

        .tag {
          background: #ffb6b6;
          color: #222;
          border-radius: 999px;
          padding: 4px 16px;
          font-weight: 600;
          font-size: 15px;
        }

        .category-tag {
          background: #eee;
        }

        .emoji-row {
          display: flex;
          gap: 8px;
          margin-bottom: 10px;
        }

        .emoji {
          font-size: 22px;
        }

        .summary-box {
          background: #fff;
          border-radius: 18px;
          padding: 18px;
          margin: 10px 0;
          font-size: 16px;
          text-align: center;
          box-shadow: 0 2px 8px #eee;
          max-width: 340px;
          color: #222;
        }

        .btn-dark, .btn-success {
          width: 260px;
          margin: 18px 0 8px;
          padding: 14px 0;
          border-radius: 18px;
          font-weight: 700;
          font-size: 18px;
          border: none;
          box-shadow: 0 2px 8px #eee;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: background 0.2s;
          font-family: 'Big Shoulders Display', sans-serif;
        }

        .btn-dark {
          background: #222;
          color: white;
          cursor: pointer;
        }

        .btn-success {
          background: #b9fbc0;
          color: #222;
          cursor: default;
        }

        .btn-outline {
          width: 180px;
          padding: 12px 0;
          border-radius: 14px;
          background: white;
          color: #222;
          border: 2px solid #222;
          font-weight: 700;
          font-size: 16px;
          box-shadow: 0 2px 8px #eee;
          cursor: pointer;
          font-family: 'Big Shoulders Display', sans-serif;
        }

        .floating-icon {
          position: fixed;
          right: 24px;
          bottom: 24px;
          width: 56px;
          height: 56px;
          border-radius: 50%;
          background: #222;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 12px #bbb;
          z-index: 1000;
        }
      `}</style>

      <div className="page">
        <div className="header">
          <button onClick={() => navigate(-1)} className="back-btn">&larr;</button>
          <div className="header-content">
            <div className="img-circle">
              <img src={imgSrc} alt={place.original?.name || 'Place'} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={e => { (e.target as HTMLImageElement).src = getFallbackImage(place.original?.category); }} />
            </div>
            <div className="place-title">{place.original?.name}</div>
            <div className="place-city">{place.original?.city}</div>
          </div>
        </div>

        <div className="tags">
          {(place.processed?.vibe_tags || []).map((tag: string) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
          {place.original?.category && (
            <span className="tag category-tag">{place.original.category}</span>
          )}
        </div>

        <div className="emoji-row">
          {(place.processed?.emojis || []).map((emoji: string, i: number) => (
            <span key={i} className="emoji">{emoji}</span>
          ))}
        </div>

        <div className="summary-box">
          {place.processed?.summary || 'No description available.'}
        </div>

        <button
          onClick={handleAddToWishlist}
          disabled={wishlistLoading || wishlistSuccess}
          className={wishlistSuccess ? 'btn-success' : 'btn-dark'}
        >
          {wishlistSuccess ? 'Added to Wishlist!' : 'ADD TO WISHLIST'}
          {!wishlistSuccess && <span style={{ fontSize: 22, marginLeft: 6 }}>+</span>}
        </button>

        <button
          className="btn-outline"
          onClick={() => navigate(`/feedback/${place_id}`)}
        >
          FEEDBACK
        </button>

        <div className="floating-icon"  onClick={() => navigate('/bot')}>
            
        
          {/* Replace with your actual icon */}
          <img src={logo} alt="Logo" style={{ width: 100, height: 60,borderRadius: '50%',
    objectFit: 'cover' }} />


        </div>
      </div>
    </>
  );
};

export default Place;
