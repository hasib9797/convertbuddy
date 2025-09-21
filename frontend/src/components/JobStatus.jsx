
import React from 'react';

export default function JobStatus({ status, apiBase }) {
  if (!status) return null;
  const isFullUrl = (u) => /^https?:\/\//i.test(u || '');
  const href = status.download_url
    ? (isFullUrl(status.download_url) ? status.download_url : `${apiBase}${status.download_url}`)
    : null;
  const progressPct = status.progress || (status.status==='done'?100:10);
  const label = status.status === 'done' ? 'Completed'
              : status.status === 'error' ? 'Failed'
              : status.status === 'processing' ? 'Processing'
              : status.status === 'queued' ? 'Queued' : '';
  return (
    <div className="mt-6 bg-white p-4 sm:p-6 rounded-2xl shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">Status</p>
          <p className="text-lg font-semibold">{label}</p>
        </div>
        <div className="w-48">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full transition-all" style={{width: `${progressPct}%`}} />
          </div>
        </div>
      </div>

      {status.error && (
        <div className="mt-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
          {status.error}
        </div>
      )}

      {href && status.status === 'done' && (
        <a
          className="mt-4 inline-flex items-center justify-center px-4 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-700"
          href={href}
          target="_blank"
          rel="noreferrer"
        >
          Download
        </a>
      )}
    </div>
  );
}
