import React, { useState, useEffect } from 'react';
import './App.css';
import Loader from './Loader';
import Dashboard from './Dashboard';
import { Trash2 } from 'lucide-react';



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
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('history')) || [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('history', JSON.stringify(history));
  }, [history]);

  const addHistory = (question, summaryText, answerText, sqlText, resultData, modelName) => {
    setHistory((prev) => [
      ...prev,
      { question, summary: summaryText, answer: answerText, sql: sqlText, result: resultData, model: modelName },
    ]);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('history');
  };

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const resp = await fetch('/api/models');
        if (resp.ok) {
          const data = await resp.json();
          const ms = Array.isArray(data.models)
            ? data.models
            : Array.isArray(data.result?.models)
            ? data.result.models
            : [];
          setModels(ms);
          if (ms.length > 0) {
            setModel(ms[0]);
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
      if (data && data.error) throw new Error(data.error.message || 'Server error');
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (data.error) throw new Error(data.error.message || 'Server error');

    const results = data.result?.results || data.results || [];
    const summaryText = data.result?.summary || data.summary || '';
    const answerText = data.result?.answer || data.answer || '';
    const sqlText = data.result?.sql || querySql;

    setResult(results);
    setSummary(summaryText);
    setAnswer(answerText);
    setSql(sqlText);
    addHistory(questionParam, summaryText, answerText, sqlText, results, model);
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
      const resp = await fetch('/api/chart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, model })
      });
      if (!resp.ok) throw new Error('Failed to generate chart data');
      const data = await resp.json();
      if (data.error) throw new Error(data.error.message || 'Server error');
      const generatedSql = data.result?.sql || data.sql || '';
      const results = data.result?.results || data.results || [];
      const summaryText = data.result?.summary || data.summary || '';
      const answerText = data.result?.answer || data.answer || '';

      setSql(generatedSql);
      setResult(results);
      setSummary(summaryText);
      setAnswer(answerText);

      addHistory(query, summaryText, answerText, generatedSql, results, model);
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

  const openHistory = (item) => {
    setQuery(item.question || '');
    setSql(item.sql || '');
    setResult(item.result || null);
    setSummary(item.summary || '');
    setAnswer(item.answer || '');
    if (item.model) {
      setModel(item.model);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="flex flex-col md:flex-row max-w-6xl mx-auto">
        <div className="flex-1 bg-white shadow-md rounded-lg p-6 space-y-6">
          <h1 className="text-2xl font-bold text-center text-blue-600">自然語言 SQL 查詢系統</h1>

          <div>
            <h2 className="text-lg font-semibold text-gray-700">輸入查詢與選擇模型</h2>
            <p className="text-sm text-gray-500 mb-2">請選擇模型並輸入你的問題，系統將轉換為 SQL 並顯示查詢結果。</p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 md:gap-4 items-center">
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

          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3">
              ⚠️ {error}
            </div>
          )}

          <div className="space-y-2">
            <textarea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              placeholder="SQL"
              className="w-full border rounded p-2 h-40 font-mono"
            />
            <button
              onClick={handleSqlExecute}
              disabled={loading || !sql.trim()}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
            >
              {loading ? <Loader /> : '執行 SQL'}
            </button>
          </div>

          {loading && (
            <div className="flex items-center gap-2 text-blue-500">
              <Loader />
              <span>查詢中，請稍候...</span>
            </div>
          )}

          <Dashboard
            result={result}
            answer={answer}
            summary={summary}
            history={history}
            clearHistory={clearHistory}
            openHistory={openHistory}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
