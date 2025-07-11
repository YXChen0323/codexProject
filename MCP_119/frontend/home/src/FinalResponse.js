import React from 'react';

function FinalResponse({ answer, summary }) {
  if (answer) {
    return <div className="text-gray-800 whitespace-pre-wrap">{answer}</div>;
  }
  if (summary) {
    return <div className="text-gray-600 italic">{summary}</div>;
  }
  return null;
}

export default FinalResponse;
