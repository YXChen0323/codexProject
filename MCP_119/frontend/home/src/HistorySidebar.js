import React from 'react';

function HistorySidebar({ history, clearHistory }) {
  if (!history || history.length === 0) return null;
  return (
    <div className="w-64 bg-white shadow-md rounded-lg p-4 space-y-2 md:ml-4 h-fit">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold">歷史紀錄</h2>
        <button
          onClick={clearHistory}
          className="text-sm text-blue-600 hover:underline"
        >
          清除紀錄
        </button>
      </div>
      <ul className="list-disc pl-5 space-y-2">
        {history.map((item, idx) => (
          <li key={idx}>
            <div className="font-semibold">{item.question}</div>
            {item.answer ? (
              <div>{item.answer}</div>
            ) : item.summary ? (
              <div className="text-gray-600 italic">{item.summary}</div>
            ) : Array.isArray(item.result) ? (
              <div className="text-gray-600 italic">共 {item.result.length} 筆資料</div>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default HistorySidebar;
