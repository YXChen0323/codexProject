import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('請輸入查詢內容');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/api/sql/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        if (data && data.error) {
          throw new Error(data.error.message || 'Server error');
        }
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      if (data.error) {
        setError(data.error.message || 'Server error');
      } else {
        setResult(data.result ?? data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Natural Language Query</h1>
      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your question"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Submit'}
        </button>
      </form>
      <div className="query-result">
        {error && <p className="error">{error}</p>}
        {Array.isArray(result) ? (
          <table className="result-table">
            <thead>
              <tr>
                {Object.keys(result[0] || {}).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((val, i) => (
                    <td key={i}>{String(val)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          result && <pre>{JSON.stringify(result, null, 2)}</pre>
        )}
      </div>
    </div>
  );
}

export default App;
