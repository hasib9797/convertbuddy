
import React from 'react'
import TargetPicker, { TARGETS } from './components/TargetPicker.jsx'
import FileDrop from './components/FileDrop.jsx'
import FileList from './components/FileList.jsx'
import OptionsPanel from './components/OptionsPanel.jsx'
import JobStatus from './components/JobStatus.jsx'
import { useJobPoll } from './hooks/useJobPoll.js'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [target, setTarget] = React.useState(TARGETS[0].value)
  const multiMode = target === 'jpg->pdf'

  const [files, setFiles] = React.useState([])
  const [options, setOptions] = React.useState('')
  const [jobId, setJobId] = React.useState(null)
  const [status, setStatus] = React.useState(null)

  const hook = useJobPoll(API_BASE, jobId, setStatus)

  const onFiles = (incoming) => {
    if (!incoming?.length) return
    if (multiMode) setFiles(incoming)
    else setFiles([incoming[0]])
  }

  const removeAt = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i))

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!files.length) return alert('Choose file(s) first')
    setStatus(null); setJobId(null)
    try {
      const form = new FormData()
      form.append('target', target)
      try {
        const parsed = options ? JSON.parse(options) : {}
        form.append('options', JSON.stringify(parsed))
      } catch {
        form.append('options', '{}')
      }
      if (multiMode) files.forEach(f => form.append('files', f))
      else form.append('file', files[0])

      const res = await fetch(`${API_BASE}/jobs/`, { method:'POST', body: form })
      if (!res.ok) throw new Error(await res.text())
      const json = await res.json()
      setJobId(json.job_id)
      setStatus({ status: json.status, progress: json.progress })
      hook.start()
    } catch (err) {
      console.error(err)
      alert('Failed to submit job: ' + err.message)
    }
  }

  return (
    <div className="min-h-screen p-4 sm:p-8 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-primary-700">Convert Buddy</h1>
          <p className="text-gray-600">Your all-in-one file friend</p>
        </header>

        <form onSubmit={onSubmit} className="space-y-4 bg-white p-4 sm:p-6 rounded-2xl shadow">
          <TargetPicker value={target} onChange={(v)=>{ setTarget(v); setFiles([]); }} />
          <FileDrop multi={multiMode} accept={multiMode ? 'image/*' : undefined} onFiles={onFiles} />
          <FileList files={files} onRemove={removeAt} />
          <OptionsPanel value={options} onChange={setOptions} target={target} />

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

        <JobStatus status={status} apiBase={API_BASE} />

        <footer className="mt-10 text-center text-xs text-gray-500">
          <p>© {new Date().getFullYear()} Convert Buddy</p>
        </footer>
      </div>
    </div>
  )
}
