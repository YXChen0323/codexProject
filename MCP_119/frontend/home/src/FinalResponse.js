import React from 'react';

function FinalResponse({ answer, summary }) {
  if (answer) {
    return <div className="text-gray-800 whitespace-pre-wrap">{answer}</div>;
  }
  if (summary) {
    return <div className="text-gray-600 italic">{summary}</div>;
  }
  return (
    <div className="text-gray-500 italic">
      目前無法提供自然語言回覆，請參考上方查詢結果。
    </div>
  );
}

export default FinalResponse;
