// Slide-over panel where the patient uploads their own documents
// (lab reports, prescriptions, etc.) and sees what's already uploaded.
// Uploaded PDFs are also ingested into the RAG index (backend-side),
// so the assistant can answer questions about them afterward.
import { useEffect, useState } from 'react'
import { uploadDocument, listMyDocuments } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

const DOCUMENT_TYPES = [
  { value: 'lab_report', label: 'Lab report' },
  { value: 'prescription', label: 'Prescription' },
  { value: 'imaging', label: 'Imaging report' },
  { value: 'discharge_summary', label: 'Discharge summary' },
  { value: 'other', label: 'Other' },
]

export default function DocumentsPanel({ onClose }) {
  const { session } = useAuth()
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedFile, setSelectedFile] = useState(null)
  const [documentType, setDocumentType] = useState('other')
  const [isUploading, setIsUploading] = useState(false)

  const loadDocuments = async () => {
    try {
      setDocuments(await listMyDocuments(session.access_token))
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) return

    setIsUploading(true)
    setError('')
    try {
      await uploadDocument(session.access_token, { file: selectedFile, documentType })
      setSelectedFile(null)
      e.target.reset()
      await loadDocuments()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="absolute inset-y-0 right-0 z-10 flex w-full max-w-sm flex-col border-l border-ink/10 bg-surface shadow-xl dark:border-ink-dark/10 dark:bg-surface-dark">
      <div className="flex items-center justify-between border-b border-ink/10 px-4 py-4 dark:border-ink-dark/10">
        <h2 className="font-display text-base font-medium text-ink dark:text-ink-dark">My Documents</h2>
        <button onClick={onClose} className="text-sm text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark">
          Close
        </button>
      </div>

      <form onSubmit={handleUpload} className="space-y-3 border-b border-ink/10 p-4 dark:border-ink-dark/10">
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="w-full rounded-lg border border-ink/15 bg-transparent px-3 py-2 text-sm text-ink dark:border-ink-dark/15 dark:text-ink-dark"
        >
          {DOCUMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          className="w-full text-sm text-ink dark:text-ink-dark"
        />
        <p className="text-xs text-muted dark:text-muted-dark">PDF only, up to 10 MB.</p>

        <button
          type="submit"
          disabled={!selectedFile || isUploading}
          className="w-full rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white transition disabled:opacity-50"
        >
          {isUploading ? 'Uploading…' : 'Upload'}
        </button>
      </form>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {isLoading && <p className="text-sm text-muted dark:text-muted-dark">Loading…</p>}
        {error && <p className="text-sm text-danger">{error}</p>}
        {!isLoading && documents.length === 0 && (
          <p className="text-sm text-muted dark:text-muted-dark">
            No documents yet — upload a report or prescription above.
          </p>
        )}
        {documents.map((doc) => (
          <div key={doc.id} className="rounded-lg border border-ink/10 p-3 dark:border-ink-dark/10">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-ink dark:text-ink-dark">{doc.original_filename}</p>
              {doc.doctor_id && (
                <span className="rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                  From your doctor
                </span>
              )}
            </div>
            <p className="text-xs text-muted dark:text-muted-dark">
              {DOCUMENT_TYPES.find((t) => t.value === doc.document_type)?.label ?? doc.document_type} ·{' '}
              {new Date(doc.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}