// Upload + list documents for one patient, shown inside the doctor's
// PatientDossierPanel. Anything uploaded here is marked SHARED, so it
// also shows up in the patient's own "My Documents" panel.
import { useEffect, useState } from 'react'
import { uploadDocumentForPatient, getPatientDocuments, getPatientDocumentDownloadUrl } from '../../lib/api.js'
import { useAuth } from '../../context/AuthContext.jsx'

const DOCUMENT_TYPES = [
  { value: 'lab_report', label: 'Lab report' },
  { value: 'prescription', label: 'Prescription' },
  { value: 'imaging', label: 'Imaging report' },
  { value: 'discharge_summary', label: 'Discharge summary' },
  { value: 'other', label: 'Other' },
]

export default function PatientDocuments({ patientId }) {
  const { session } = useAuth()
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedFile, setSelectedFile] = useState(null)
  const [documentType, setDocumentType] = useState('lab_report')
  const [isUploading, setIsUploading] = useState(false)
  const [openingId, setOpeningId] = useState(null)

  const handleOpen = async (documentId) => {
    setOpeningId(documentId)
    setError('')
    try {
      const { url } = await getPatientDocumentDownloadUrl(session.access_token, patientId, documentId)
      window.open(url, '_blank', 'noopener,noreferrer')
    } catch (err) {
      setError(err.message)
    } finally {
      setOpeningId(null)
    }
  }

  const loadDocuments = async () => {
    try {
      setDocuments(await getPatientDocuments(session.access_token, patientId))
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) return

    setIsUploading(true)
    setError('')
    try {
      await uploadDocumentForPatient(session.access_token, patientId, { file: selectedFile, documentType })
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
    <section>
      <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Documents</h3>

      <form onSubmit={handleUpload} className="mt-2 flex items-center gap-2">
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="rounded-lg border border-ink/15 bg-transparent px-2 py-1.5 text-xs text-ink dark:border-ink-dark/15 dark:text-ink-dark"
        >
          {DOCUMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          className="flex-1 text-xs text-ink dark:text-ink-dark"
        />
        <button
          type="submit"
          disabled={!selectedFile || isUploading}
          className="shrink-0 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-white transition disabled:opacity-50"
        >
          {isUploading ? 'Uploading…' : 'Share'}
        </button>
      </form>
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}

      <div className="mt-3 space-y-2">
        {isLoading && <p className="text-sm text-muted dark:text-muted-dark">Loading…</p>}
        {!isLoading && documents.length === 0 && (
          <p className="text-sm text-muted dark:text-muted-dark">No documents on file yet.</p>
        )}
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center justify-between rounded-lg bg-panel px-3 py-2 text-sm dark:bg-panel-dark">
            <button
              onClick={() => handleOpen(doc.id)}
              disabled={openingId === doc.id}
              className="text-ink underline-offset-2 hover:text-accent hover:underline disabled:opacity-60 dark:text-ink-dark"
            >
              {openingId === doc.id ? 'Opening…' : doc.original_filename}
            </button>
            <span className="text-xs text-muted dark:text-muted-dark">
              {doc.doctor_id ? 'Shared by doctor' : 'Uploaded by patient'}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}