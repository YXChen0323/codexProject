import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [sql, setSql] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [models, setModels] = useState([]);
  const [model, setModel] = useState('');

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const resp = await fetch('/api/models');
        if (resp.ok) {
          const data = await resp.json();
          setModels(data.models);
          if (data.models && data.models.length > 0) {
            setModel(data.models[0]);
          }
        }
      } catch (err) {
        // ignore errors
      }
    };
    fetchModels();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('請輸入查詢內容');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setSql('');
    setSummary('');
    try {
      const sqlResp = await fetch('/api/sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, model })
      });
      if (!sqlResp.ok) {
        throw new Error('Failed to generate SQL');
      }
      const sqlData = await sqlResp.json();
      if (sqlData.error) {
        throw new Error(sqlData.error);
      }
      setSql(sqlData.sql);
      const response = await fetch('/api/sql/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sqlData.sql, model })
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
        setResult(data.result?.results || data.results || []);
        setSummary(data.result?.summary || data.summary || '');
        setSql(data.result?.sql || sqlData.sql);
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
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          {models.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
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
        {sql && (
          <pre className="generated-sql">{sql}</pre>
        )}
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
        {summary && <p className="summary">{summary}</p>}
      </div>
    </div>
  );
}

export default App;
