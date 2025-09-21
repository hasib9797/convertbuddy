
import React from 'react';

export default function FileList({ files, onRemove }) {
  if (!files?.length) return null;
  return (
    <div className="mt-3 border rounded-xl divide-y">
      {files.map((f, i) => (
        <div key={i} className="flex items-center justify-between px-3 py-2 text-sm">
          <span className="truncate">{f.name} <span className="text-gray-400">({Math.round((f.size||0)/1024)} KB)</span></span>
          <button
            type="button"
            onClick={()=>onRemove(i)}
            className="text-red-600 hover:text-red-700"
            aria-label="Remove"
          >Remove</button>
        </div>
      ))}
    </div>
  );
}
