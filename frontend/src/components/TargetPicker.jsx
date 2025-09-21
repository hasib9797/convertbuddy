
import React from 'react';

export const TARGETS = [
  { value: 'mp4->mp3', label: 'MP4 → MP3 (extract audio)' },
  { value: 'pdf->jpg', label: 'PDF → JPG (pages as images)' },
  { value: 'jpg->pdf', label: 'Image(s) → PDF (merge multiple)' },
  { value: 'docx->pdf', label: 'DOCX → PDF' },
];

export default function TargetPicker({ value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">Conversion</label>
      <select
        className="w-full rounded-lg border-gray-300 focus:border-primary-500 focus:ring-primary-500"
        value={value}
        onChange={(e)=>onChange(e.target.value)}
      >
        {TARGETS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
      </select>
    </div>
  );
}
