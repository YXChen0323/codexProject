import React from 'react';

function HistorySidebar({ history, clearHistory, openHistory, deleteHistoryItem }) {
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
      <ul className="list-disc pl-5 space-y-2 overflow-y-auto max-h-96">
        {history && history.length > 0 ? (
          history.map((item, idx) => (
            <li key={idx} className="cursor-pointer group flex items-start justify-between hover:bg-gray-50 px-2 py-1 rounded relative">
              <div className="flex-1" onClick={() => openHistory(item)}>
            <div className="font-semibold">{item.question}</div>
            {item.answer ? (
              <div>{item.answer}</div>
            ) : item.summary ? (
              <div className="text-gray-600 italic">{item.summary}</div>
            ) : null}
              </div>
              <button
                className="ml-2 text-gray-400 hover:text-red-500 font-bold text-lg invisible group-hover:visible"
                title="刪除這筆紀錄"
                onClick={e => { e.stopPropagation(); deleteHistoryItem(idx); }}
              >
                ×
              </button>
          </li>
          ))
        ) : (
          <li className="text-gray-400 italic">尚無歷史紀錄</li>
        )}
      </ul>
    </div>
  );
}

export default HistorySidebar;
