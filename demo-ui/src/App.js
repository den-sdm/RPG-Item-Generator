import React, { useState, useEffect } from 'react';

const RARITY_COLORS = {
  COMMON: { border: '#9d9d9d', bg: '#1a1a1a', glow: 'rgba(157, 157, 157, 0.3)' },
  UNCOMMON: { border: '#1eff00', bg: '#0a2d0a', glow: 'rgba(30, 255, 0, 0.3)' },
  RARE: { border: '#0070dd', bg: '#0a1a2d', glow: 'rgba(0, 112, 221, 0.3)' },
  EPIC: { border: '#a335ee', bg: '#1f0a2d', glow: 'rgba(163, 53, 238, 0.3)' },
  LEGENDARY: { border: '#ff8000', bg: '#2d1a0a', glow: 'rgba(255, 128, 0, 0.3)' }
};

function ItemCard({ item }) {
  const colors = RARITY_COLORS[item.rarity] || RARITY_COLORS.COMMON;
  
  const getTypeIcon = (type) => {
    if (type.includes('weapon')) return '⚔️';
    if (type.includes('armor')) return '🛡️';
    if (type.includes('accessory')) return '💍';
    return '❓';
  };
  
  return (
    <div style={{
      background: colors.bg,
      border: `2px solid ${colors.border}`,
      borderRadius: '8px',
      padding: '16px',
      boxShadow: `0 4px 20px ${colors.glow}, 0 0 40px ${colors.glow}`,
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'pointer',
      position: 'relative',
      overflow: 'hidden',
      animation: 'fadeIn 0.3s ease-in'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = `0 8px 30px ${colors.glow}, 0 0 60px ${colors.glow}`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = `0 4px 20px ${colors.glow}, 0 0 40px ${colors.glow}`;
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
        background: colors.border,
        color: '#000',
        padding: '4px 12px',
        fontSize: '11px',
        fontWeight: 'bold',
        borderBottomLeftRadius: '8px',
        letterSpacing: '0.5px'
      }}>
        {item.rarity}
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', marginTop: '8px' }}>
        <span style={{ fontSize: '24px' }}>{getTypeIcon(item.type)}</span>
        <h3 style={{ 
          margin: 0, 
          color: colors.border, 
          fontSize: '18px',
          fontWeight: 'bold',
          textShadow: `0 0 10px ${colors.glow}`
        }}>
          {item.name}
        </h3>
      </div>
      
      <div style={{ 
        color: '#999', 
        fontSize: '12px', 
        marginBottom: '12px',
        textTransform: 'uppercase',
        letterSpacing: '1px'
      }}>
        {item.type.replace('-', ' · ')}
      </div>
      
      <div style={{ marginBottom: '12px' }}>
        {item.stats && item.stats.map((stat, idx) => (
          <div key={idx} style={{
            color: '#ccc',
            fontSize: '13px',
            padding: '3px 0',
            borderBottom: idx < item.stats.length - 1 ? '1px solid #333' : 'none'
          }}>
            {stat}
          </div>
        ))}
      </div>
      
      {item.flavor && (
        <div style={{
          color: '#ff8c00',
          fontSize: '12px',
          fontStyle: 'italic',
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #444',
          lineHeight: '1.4'
        }}>
          "{item.flavor}"
        </div>
      )}
    </div>
  );
}

export default function RPGItemGeneratorDemo() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filterRarity, setFilterRarity] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');
  const [numItems, setNumItems] = useState(10);
  const [temperature, setTemperature] = useState(0.8);
  const [apiStatus, setApiStatus] = useState('checking');
  
  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);
  
  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health');
      const data = await response.json();
      setApiStatus(data.status === 'ok' ? 'connected' : 'error');
    } catch (err) {
      setApiStatus('disconnected');
    }
  };
  
  const generateItems = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const rarityParam = filterRarity !== 'ALL' ? `&rarity=${filterRarity}` : '';
      const url = `http://localhost:5000/api/generate?num=${numItems}&temperature=${temperature}${rarityParam}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setItems(data.items);
      } else {
        setError(data.error || 'Generation failed');
      }
    } catch (err) {
      setError('Cannot connect to API server. Make sure api_server.py is running.');
      setApiStatus('disconnected');
    } finally {
      setLoading(false);
    }
  };
  
  const filteredItems = items.filter(item => {
    if (filterRarity !== 'ALL' && item.rarity !== filterRarity) return false;
    if (filterType !== 'ALL' && !item.type.includes(filterType)) return false;
    return true;
  });
  
  const rarityDistribution = items.reduce((acc, item) => {
    acc[item.rarity] = (acc[item.rarity] || 0) + 1;
    return acc;
  }, {});
  
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ 
          fontSize: '48px', 
          margin: '0 0 10px 0',
          background: 'linear-gradient(135deg, #ff8000 0%, #a335ee 50%, #0070dd 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 'bold'
        }}>
          RPG Item Generator
        </h1>
        <p style={{ color: '#999', fontSize: '16px', margin: '5px 0' }}>
          GPT-Powered Fantasy Loot Generation
        </p>
        
        {/* API Status */}
        <div style={{ marginTop: '10px' }}>
          {apiStatus === 'connected' && (
            <span style={{ color: '#1eff00', fontSize: '12px' }}>
              ● API Connected
            </span>
          )}
          {apiStatus === 'disconnected' && (
            <span style={{ color: '#ff0000', fontSize: '12px' }}>
              ● API Disconnected - Start api_server.py
            </span>
          )}
          {apiStatus === 'checking' && (
            <span style={{ color: '#ffaa00', fontSize: '12px' }}>
              ● Checking API...
            </span>
          )}
        </div>
      </div>
      
      {/* Controls */}
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto 30px', 
        display: 'flex', 
        gap: '15px',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        {/* Number of items */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ color: '#999', fontSize: '14px' }}>Items:</label>
          <input 
            type="number" 
            value={numItems} 
            onChange={(e) => setNumItems(Math.min(100, Math.max(1, parseInt(e.target.value) || 10)))}
            min="1"
            max="100"
            style={{
              background: '#1a1a1a',
              color: '#fff',
              border: '2px solid #444',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '14px',
              width: '70px'
            }}
          />
        </div>
        
        {/* Temperature */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ color: '#999', fontSize: '14px' }}>Temp:</label>
          <input 
            type="number" 
            value={temperature} 
            onChange={(e) => setTemperature(Math.min(2, Math.max(0.1, parseFloat(e.target.value) || 0.8)))}
            min="0.1"
            max="2"
            step="0.1"
            style={{
              background: '#1a1a1a',
              color: '#fff',
              border: '2px solid #444',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '14px',
              width: '70px'
            }}
          />
        </div>
        
        {/* Rarity filter */}
        <select value={filterRarity} onChange={(e) => setFilterRarity(e.target.value)}
          style={{
            background: '#1a1a1a',
            color: '#fff',
            border: '2px solid #444',
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer'
          }}>
          <option value="ALL">All Rarities</option>
          <option value="COMMON">Common</option>
          <option value="UNCOMMON">Uncommon</option>
          <option value="RARE">Rare</option>
          <option value="EPIC">Epic</option>
          <option value="LEGENDARY">Legendary</option>
        </select>
        
        {/* Type filter */}
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)}
          style={{
            background: '#1a1a1a',
            color: '#fff',
            border: '2px solid #444',
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer'
          }}>
          <option value="ALL">All Types</option>
          <option value="weapon">Weapons</option>
          <option value="armor">Armor</option>
          <option value="accessory">Accessories</option>
        </select>
        
        {/* Generate button */}
        <button 
          onClick={generateItems}
          disabled={loading || apiStatus === 'disconnected'}
          style={{
            background: loading ? '#666' : 'linear-gradient(135deg, #ff8000 0%, #ff6000 100%)',
            color: '#fff',
            border: 'none',
            padding: '12px 30px',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: loading || apiStatus === 'disconnected' ? 'not-allowed' : 'pointer',
            boxShadow: loading ? 'none' : '0 4px 15px rgba(255, 128, 0, 0.4)',
            transition: 'transform 0.2s',
            opacity: loading || apiStatus === 'disconnected' ? 0.6 : 1
          }}
          onMouseEnter={(e) => !loading && apiStatus === 'connected' && (e.currentTarget.style.transform = 'scale(1.05)')}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}>
          {loading ? '⏳ Generating...' : '⚡ Generate Items'}
        </button>
      </div>
      
      {/* Error message */}
      {error && (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto 20px',
          padding: '12px 20px',
          background: '#2d0a0a',
          border: '2px solid #ff0000',
          borderRadius: '6px',
          color: '#ff6666',
          fontSize: '14px',
          textAlign: 'center'
        }}>
          ⚠️ {error}
        </div>
      )}
      
      {/* Stats */}
      {items.length > 0 && (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto 30px',
          display: 'flex',
          gap: '10px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {Object.entries(rarityDistribution).map(([rarity, count]) => (
            <div key={rarity} style={{
              background: '#1a1a1a',
              border: `2px solid ${RARITY_COLORS[rarity]?.border || '#999'}`,
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              color: RARITY_COLORS[rarity]?.border || '#999'
            }}>
              <strong>{rarity}</strong>: {count}
            </div>
          ))}
        </div>
      )}
      
      {/* Items grid */}
      {filteredItems.length > 0 ? (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '20px',
        }}>
          {filteredItems.map((item, idx) => (
            <ItemCard key={idx} item={item} />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', color: '#999', marginTop: '60px', fontSize: '18px' }}>
          {items.length === 0 ? (
            <>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚔️</div>
              <div>Click "Generate Items" to create new loot!</div>
            </>
          ) : (
            'No items match the current filters'
          )}
        </div>
      )}
      
      {/* Footer */}
      <div style={{ textAlign: 'center', marginTop: '60px', color: '#666', fontSize: '14px' }}>
        <p>Built with PyTorch · GPT-style Transformer · Live Generation</p>
        <p style={{ marginTop: '10px', fontSize: '12px' }}>
          {items.length > 0 ? `Generated ${items.length} items from trained model` : 'Ready to generate'}
        </p>
      </div>
    </div>
  );
}