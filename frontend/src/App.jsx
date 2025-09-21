import React, { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const TARGETS = [
  { value: 'mp4->mp3', label: 'MP4 → MP3 (extract audio)' },
  { value: 'pdf->jpg', label: 'PDF → JPG (pages as images)' },
  { value: 'jpg->pdf', label: 'Image(s) → PDF (merge multiple)' },
  { value: 'docx->pdf', label: 'DOCX → PDF' },
]

function cls(...a){return a.filter(Boolean).join(' ')}

export default function App() {
  const [target, setTarget] = useState(TARGETS[0].value)
  const [file, setFile] = useState(null)             // single
  const [files, setFiles] = useState([])             // multi for jpg->pdf
  const [options, setOptions] = useState('')
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const pollRef = useRef(null)

  const multiMode = target === 'jpg->pdf'

  useEffect(() => {
    if (!jobId) return
    pollRef.current && clearInterval(pollRef.current)
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}`)
        const json = await res.json()
        setStatus(json)
        if (json.status === 'done' || json.status === 'error') {
          clearInterval(pollRef.current)
        }
      } catch (e) {
        console.error(e)
      }
    }, 1500)
    return () => pollRef.current && clearInterval(pollRef.current)
  }, [jobId])

  const resetSelected = () => { setFile(null); setFiles([]) }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (multiMode) {
      const list = Array.from(e.dataTransfer.files || [])
      if (list.length) setFiles(list)
    } else {
      const f = e.dataTransfer.files?.[0]
      if (f) setFile(f)
    }
  }

  const onFileInput = (e) => {
    if (multiMode) {
      setFiles(Array.from(e.target.files || []))
    } else {
      setFile(e.target.files?.[0] || null)
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    if (multiMode && files.length === 0) return alert('Choose one or more images')
    if (!multiMode && !file) return alert('Choose a file')
    setStatus(null); setJobId(null)
    try {
      const form = new FormData()
      form.append('target', target)
      // options
      try {
        const parsed = options ? JSON.parse(options) : {}
        form.append('options', JSON.stringify(parsed))
      } catch {
        form.append('options', '{}')
      }
      if (multiMode) {
        // append many under the field name "files"
        files.forEach(f => form.append('files', f))
      } else {
        form.append('file', file)
      }
      const res = await fetch(`${API_BASE}/jobs/`, { method:'POST', body: form })
      if (!res.ok) throw new Error(await res.text())
      const json = await res.json()
      setJobId(json.job_id)
      setStatus({ status: json.status, progress: json.progress })
    } catch (err) {
      console.error(err)
      alert('Failed to submit job: ' + err.message)
    }
  }

  const progressLabel = status?.status === 'done' ? 'Completed' :
                        status?.status === 'error' ? 'Failed' :
                        status?.status === 'processing' ? 'Processing' :
                        status?.status === 'queued' ? 'Queued' : ''

  const fileSummary = multiMode
    ? (files.length ? `${files.length} file(s) selected` : 'No files selected')
    : (file ? file.name : 'No file selected')

  return (
    <div className="min-h-screen p-4 sm:p-8 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-primary-700">Convert Buddy</h1>
          <p className="text-gray-600">Your all-in-one file friend</p>
        </header>

        <form onSubmit={submit} className="space-y-4 bg-white p-4 sm:p-6 rounded-2xl shadow">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Conversion</label>
            <select
              className="w-full rounded-lg border-gray-300 focus:border-primary-500 focus:ring-primary-500"
              value={target}
              onChange={(e)=>{ setTarget(e.target.value); resetSelected(); }}
            >
              {TARGETS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>

          <div
            className={
              "border-2 border-dashed rounded-2xl p-6 text-center transition " +
              (dragOver ? "border-primary-600 bg-primary-50" : "border-gray-300 bg-gray-50")
            }
            onDragOver={(e)=>{e.preventDefault(); setDragOver(true)}}
            onDragLeave={()=>setDragOver(false)}
            onDrop={onDrop}
          >
            <p className="mb-2 font-medium">Drag & drop {multiMode ? 'image files' : 'a file'} here</p>
            <p className="text-sm text-gray-500 mb-4">or click to choose</p>
            <input
              type="file"
              multiple={multiMode}
              accept={multiMode ? "image/*" : undefined}
              onChange={onFileInput}
              className="block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4
                         file:rounded-full file:border-0 file:font-semibold
                         file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200
                         cursor-pointer"
            />
            <p className="mt-2 text-sm text-gray-700">{fileSummary}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Options (JSON)</label>
            <textarea
              rows="3"
              value={options}
              onChange={(e)=>setOptions(e.target.value)}
              placeholder='e.g. {"dpi":300} or {"bitrate":"128k"}'
              className="w-full rounded-lg border-gray-300 focus:border-primary-500 focus:ring-primary-500 font-mono text-sm p-2"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800"
            >
              Convert
            </button>
            {jobId && <span className="text-xs text-gray-500">Job ID: {jobId}</span>}
          </div>
        </form>

        {status && (
          <div className="mt-6 bg-white p-4 sm:p-6 rounded-2xl shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="text-lg font-semibold">{progressLabel}</p>
              </div>
              <div className="w-48">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full transition-all" style={{width: `${status.progress || (status.status==='done'?100:10)}%`}} />
                </div>
              </div>
            </div>

            {status.error && (
              <div className="mt-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
                {status.error}
              </div>
            )}

            {status.download_url && status.status === 'done' && (
              <a
                className="mt-4 inline-flex items-center justify-center px-4 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-700"
                href={`${API_BASE}${status.download_url}`}
                target="_blank"
                rel="noreferrer"
              >
                Download
              </a>
            )}
          </div>
        )}

        <footer className="mt-10 text-center text-xs text-gray-500">
          <p>© {new Date().getFullYear()} Convert Buddy</p>
        </footer>
      </div>
    </div>
  )
}
