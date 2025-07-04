import React, { useState, useEffect } from 'react';
import './App.css';
import Loader from './Loader';
import MapView from './MapView';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [sql, setSql] = useState('');
  const [summary, setSummary] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [models, setModels] = useState([]);
  const [model, setModel] = useState('');

  const loadCalls = async () => {
    setLoading(true);
    setError(null);
    setSql('');
    setSummary('');
    setAnswer('');
    try {
      const resp = await fetch('/api/calls');
      if (!resp.ok) throw new Error('Failed to fetch data');
      const data = await resp.json();
      setResult(data.rows || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
      } catch (_) {}
    };
    fetchModels();
  }, []);

  const executeSql = async (querySql, questionParam = query) => {
    const response = await fetch('/api/sql/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: querySql, model, question: questionParam })
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
      throw new Error(data.error.message || 'Server error');
    }
    setResult(data.result?.results || data.results || []);
    setSummary(data.result?.summary || data.summary || '');
    setAnswer(data.result?.answer || data.answer || '');
    setSql(data.result?.sql || querySql);
  };

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
    setAnswer('');
    try {
      const sqlResp = await fetch('/api/sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, model })
      });
      if (!sqlResp.ok) throw new Error('Failed to generate SQL');
      const sqlData = await sqlResp.json();
      if (sqlData.error) throw new Error(sqlData.error);
      setSql(sqlData.sql);
      await executeSql(sqlData.sql, query);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSqlExecute = async () => {
    if (!sql.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setSummary('');
    setAnswer('');
    try {
      await executeSql(sql, query);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-6 space-y-6">
        <h1 className="text-2xl font-bold text-center text-blue-600">自然語言 SQL 查詢系統</h1>

        <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="border rounded p-2 flex-1"
          >
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="輸入你的問題"
            className="border rounded p-2 flex-1"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            {loading ? <Loader /> : '查詢'}
          </button>
        </form>

        <button
          onClick={loadCalls}
          disabled={loading}
          className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition"
        >
          {loading ? <Loader /> : '載入示範資料'}
        </button>

        {sql && (
          <div className="space-y-2">
            <textarea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              className="w-full border rounded p-2 h-40 font-mono"
            />
            <button
              onClick={handleSqlExecute}
              disabled={loading}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
            >
              {loading ? <Loader /> : '執行 SQL'}
            </button>
          </div>
        )}

        {error && <div className="bg-red-100 text-red-700 p-3 rounded">{error}</div>}

        {loading && <Loader />}

        {Array.isArray(result) && result.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full border text-sm">
              <thead className="bg-gray-100">
                <tr>
                  {Object.keys(result[0]).map((key) => (
                    <th key={key} className="border px-2 py-1 text-left font-semibold">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.map((row, idx) => (
                  <tr key={idx} className="even:bg-gray-50 hover:bg-gray-100">
                    {Object.values(row).map((val, i) => (
                      <td key={i} className="border px-2 py-1">{String(val)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {Array.isArray(result) && result.length > 0 && (
          <MapView data={result} />
        )}

        {answer && <div className="text-gray-800">{answer}</div>}
        {summary && <div className="text-gray-600 italic">{summary}</div>}
      </div>
    </div>
  );
}

export default App;
