
import React from 'react';

export default function OptionsPanel({ value, onChange, target }) {
  const placeholder = target === 'mp4->mp3'
    ? '{"bitrate":"128k"}'
    : target === 'pdf->jpg'
      ? '{"dpi":300}'
      : target === 'jpg->pdf'
        ? '{"dpi":300}'
        : '{}';
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">Options (JSON)</label>
      <textarea
        rows="3"
        value={value}
        onChange={(e)=>onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border-gray-300 focus:border-primary-500 focus:ring-primary-500 font-mono text-sm p-2"
      />
      <p className="text-xs text-gray-500 mt-1">
        Examples — PDF→JPG: {"{dpi:150|200|300}"} | MP4→MP3: {"{bitrate:'128k'|'192k'}"}
      </p>
    </div>
  );
}
