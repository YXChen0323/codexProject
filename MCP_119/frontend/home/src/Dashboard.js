import React from 'react';
import ChartView from './ChartView';
import HistorySidebar from './HistorySidebar';
import FinalResponse from './FinalResponse';

function Dashboard({ result, answer, summary, history, clearHistory, openHistory }) {
  return (
    <div className="flex flex-row min-h-screen">
      <div className="flex-1 space-y-4">
        {Array.isArray(result) && result.length > 0 && (
          <section className="bg-gray-100 p-4 rounded shadow-inner space-y-4">
            <h2 className="text-lg font-bold text-gray-700">查詢結果</h2>
            <div className="overflow-auto max-h-96">
              <table className="min-w-full border text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    {Object.keys(result[0]).map((key, idx) => (
                      <th
                        key={key}
                        className={`border px-2 py-1 text-left font-semibold sticky top-0 bg-white ${idx === 0 ? 'left-0 z-10' : ''}`}
                      >
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.map((row, idx) => (
                    <tr key={idx} className="even:bg-gray-50 hover:bg-gray-100">
                      {Object.values(row).map((val, i) => (
                        <td
                          key={i}
                          className={`border px-2 py-1 ${i === 0 ? 'bg-white sticky left-0' : ''}`}
                        >
                          {String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {Array.isArray(result) && result.length > 0 && <ChartView result={result} />}

        <FinalResponse
          answer={answer}
          summary={summary}
          showFallback={Array.isArray(result) && result.length === 0}
        />
      </div>
      <HistorySidebar history={history} clearHistory={clearHistory} openHistory={openHistory} />
    </div>
  );
}

export default Dashboard;
