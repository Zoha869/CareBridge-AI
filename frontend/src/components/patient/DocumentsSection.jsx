// Documents section for PatientDashboard - matches the card style of
// the Medications/Instructions sections rather than a slide-over panel,
// so it fits this page's anchor-link + scroll layout.
import { useEffect, useState } from 'react'
import { uploadDocument, listMyDocuments, getMyDocumentDownloadUrl } from '../../lib/api.js'
import { useAuth } from '../../context/AuthContext.jsx'

const DOCUMENT_TYPES = [
  { value: 'lab_report', label: 'Lab report' },
  { value: 'prescription', label: 'Prescription' },
  { value: 'imaging', label: 'Imaging report' },
  { value: 'discharge_summary', label: 'Discharge summary' },
  { value: 'other', label: 'Other' },
]

export default function DocumentsSection() {
  const { session } = useAuth()
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedFile, setSelectedFile] = useState(null)
  const [documentType, setDocumentType] = useState('other')
  const [isUploading, setIsUploading] = useState(false)
  const [openingId, setOpeningId] = useState(null)

  const handleOpen = async (documentId) => {
    setOpeningId(documentId)
    setError('')
    try {
      const { url } = await getMyDocumentDownloadUrl(session.access_token, documentId)
      window.open(url, '_blank', 'noopener,noreferrer')
    } catch (err) {
      setError(err.message)
    } finally {
      setOpeningId(null)
    }
  }

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
    <section id="documents" className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
      <h3 className="font-display text-base text-ink dark:text-ink-dark">Documents</h3>

      <form onSubmit={handleUpload} className="mt-3 flex flex-wrap items-center gap-2">
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="rounded-lg border border-ink/15 bg-transparent px-2 py-1.5 text-sm text-ink dark:border-ink-dark/15 dark:text-ink-dark"
        >
          {DOCUMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          className="text-sm text-ink dark:text-ink-dark"
        />
        <button
          type="submit"
          disabled={!selectedFile || isUploading}
          className="rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-white transition disabled:opacity-50"
        >
          {isUploading ? 'Uploading…' : 'Upload'}
        </button>
        <span className="text-xs text-muted dark:text-muted-dark">PDF only, up to 10 MB.</span>
      </form>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <div className="mt-4 space-y-2">
        {isLoading && <p className="text-sm text-muted dark:text-muted-dark">Loading…</p>}
        {!isLoading && documents.length === 0 && (
          <p className="text-sm text-muted dark:text-muted-dark">No documents yet.</p>
        )}
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center justify-between rounded-xl bg-surface p-3 dark:bg-surface-dark">
            <div>
              <button
                onClick={() => handleOpen(doc.id)}
                disabled={openingId === doc.id}
                className="text-sm font-medium text-ink underline-offset-2 hover:text-accent hover:underline disabled:opacity-60 dark:text-ink-dark"
              >
                {openingId === doc.id ? 'Opening…' : doc.original_filename}
              </button>
              <p className="text-xs text-muted dark:text-muted-dark">
                {DOCUMENT_TYPES.find((t) => t.value === doc.document_type)?.label ?? doc.document_type} ·{' '}
                {new Date(doc.created_at).toLocaleDateString()}
              </p>
            </div>
            {doc.doctor_id && (
              <span className="shrink-0 rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                From your doctor
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}