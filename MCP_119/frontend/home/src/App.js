import React, { useState, useEffect } from 'react';
import './App.css';
import Loader from './Loader';
import ChartView from './ChartView';
import HistorySidebar from './HistorySidebar';
import MapContainer from './MapContainer';
import FinalResponse from './FinalResponse';
import ModelSelector from './ModelSelector';
import QuestionInput from './QuestionInput';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [sql, setSql] = useState('');
  const [summary, setSummary] = useState('');
  const [answer, setAnswer] = useState('');
  const [activeTab, setActiveTab] = useState('query');
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
const [useHistory, setUseHistory] = useState(true);
  const [hoveredMenu, setHoveredMenu] = useState(null);

  useEffect(() => {
    localStorage.setItem('history', JSON.stringify(history));
  }, [history]);

  const deleteHistoryItem = (idx) => {
    setHistory(history => {
      const newHistory = history.filter((_, i) => i !== idx);
      localStorage.setItem('history', JSON.stringify(newHistory));
      return newHistory;
    });
  };

  const addHistory = (question, summaryText, answerText, sqlText, resultData, modelName) => {
    setHistory((prev) => [
      {
        question,
        summary: summaryText,
        answer: answerText,
        sql: sqlText,
        result: Array.isArray(resultData) ? resultData.slice(0, 5) : resultData,
        model: modelName,
      },
      ...prev
    ].slice(0, 30));
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
      body: JSON.stringify({ query: querySql, model, question: questionParam, use_history: useHistory })
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
        body: JSON.stringify({ question: query, model, use_history: useHistory })
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
    <div className="min-h-screen bg-gray-50 flex">
      <div className="w-40 bg-gray-100 p-4 space-y-2 relative">
        <div onMouseEnter={() => setHoveredMenu('query')} className="relative">
          <button className={`w-full p-2 rounded ${activeTab === 'query' ? 'bg-blue-500 text-white' : 'bg-white'}`} onClick={() => setActiveTab('query')}>查詢</button>
        </div>
        <div onMouseEnter={() => setHoveredMenu('table')} className="relative">
          <button className={`w-full p-2 rounded ${activeTab === 'table' ? 'bg-blue-500 text-white' : 'bg-white'}`} onClick={() => setActiveTab('table')}>表格</button>
        </div>
        <div onMouseEnter={() => setHoveredMenu('chart')} className="relative">
          <button className={`w-full p-2 rounded ${activeTab === 'chart' ? 'bg-blue-500 text-white' : 'bg-white'}`} onClick={() => setActiveTab('chart')}>圖表</button>
        </div>
        <button className={`w-full p-2 rounded ${activeTab === 'map' ? 'bg-blue-500 text-white' : 'bg-white'}`} onClick={() => setActiveTab('map')}>地圖</button>
      </div>

      <div className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen">
        {/* 美化後的 sticky header區塊 */}
        <div className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-blue-100 rounded-xl shadow-md px-6 pb-4 mb-6">
          <h1 className="text-3xl font-extrabold text-center text-blue-600 tracking-wide pt-4">自然語言 SQL 查詢系統</h1>
          <div className="text-center mt-2">
            <h2 className="text-lg font-semibold text-gray-700">輸入查詢與選擇模型</h2>
            <p className="text-sm text-gray-500">請選擇模型並輸入你的問題，系統將轉換為 SQL 並顯示查詢結果。</p>
          </div>
          <div className="flex flex-wrap md:flex-nowrap gap-2 md:gap-4 items-center justify-center mt-4">
            <ModelSelector model={model} models={models} setModel={setModel} />
            <QuestionInput query={query} setQuery={setQuery} loading={loading} />
            <label className="flex items-center gap-2 mr-4 text-gray-600 bg-gray-100 px-3 py-2 rounded shadow-sm">
              <input type="checkbox" checked={useHistory} onChange={e => setUseHistory(e.target.checked)} className="accent-blue-500" />
              參考歷史查詢紀錄
            </label>
            <button onClick={handleSubmit} disabled={loading} className="flex items-center gap-2 bg-gradient-to-r from-blue-500 to-blue-400 text-white px-6 py-2 rounded-lg shadow hover:from-blue-600 hover:to-blue-500 transition font-semibold disabled:opacity-60">
              <span className="material-icons text-base">search</span>
              {loading ? <Loader /> : '查詢'}
            </button>
          </div>
        </div>
        <div className="flex flex-row gap-8">

          <div className="flex-1 min-w-0">
        {activeTab === 'query' && (
              <div className="bg-white shadow-md rounded-lg p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-700">輸入查詢與選擇模型</h2>
                <p className="text-sm text-gray-500 mb-2">請選擇模型並輸入你的問題，系統將轉換為 SQL 並顯示查詢結果。</p>
              </div>
                <div className="space-y-2">
                  <textarea value={sql} onChange={(e) => setSql(e.target.value)} placeholder="SQL" className="w-full border rounded p-2 h-40 font-mono" />
                  <button onClick={handleSqlExecute} disabled={loading || !sql.trim()} className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition">{loading ? <Loader /> : '執行 SQL'}</button>
                </div>
              {loading && (
                <div className="flex items-center gap-2 text-blue-500">
                  <Loader />
                  <span>查詢中，請稍候...</span>
                </div>
              )}
                <FinalResponse answer={answer} summary={summary} showFallback={Array.isArray(result) && result.length === 0} />
          </div>
        )}
            {activeTab === 'table' && (
          <div className="space-y-4">
            {Array.isArray(result) && result.length > 0 && (
              <section className="bg-gray-100 p-4 rounded shadow-inner space-y-4">
                <h2 className="text-lg font-bold text-gray-700">查詢結果</h2>
                <div className="overflow-auto max-h-96">
                  <table className="min-w-full border text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        {Object.keys(result[0]).map((key, idx) => (
                              <th key={key} className={`border px-2 py-1 text-left font-semibold sticky top-0 bg-white ${idx === 0 ? 'left-0 z-10' : ''}`}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.map((row, idx) => (
                        <tr key={idx} className="even:bg-gray-50 hover:bg-gray-100">
                          {Object.values(row).map((val, i) => (
                                <td key={i} className={`border px-2 py-1 ${i === 0 ? 'bg-white sticky left-0' : ''}`}>{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
              </div>
            )}
            {activeTab === 'chart' && (
              <div className="space-y-4">
            {Array.isArray(result) && result.length > 0 && <ChartView result={result} />}
          </div>
        )}
            {activeTab === 'map' && (
              <div>
                <MapContainer />
              </div>
            )}
          </div>
          <div className="w-full md:w-72 flex-shrink-0">
            <HistorySidebar history={history} clearHistory={clearHistory} openHistory={openHistory} deleteHistoryItem={deleteHistoryItem} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
