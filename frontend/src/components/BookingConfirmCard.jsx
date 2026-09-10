// The review/confirm step - nothing is booked until the patient
// explicitly presses Confirm here.
export default function BookingConfirmCard({ details, onConfirm, onCancel, isBooking }) {
  return (
    <div className="max-w-[85%] space-y-3 rounded-2xl rounded-bl-sm bg-panel p-4 dark:bg-panel-dark">
      <p className="text-sm font-medium text-ink dark:text-ink-dark">Please confirm your appointment:</p>
      <div className="rounded-lg bg-surface p-3 text-sm text-ink dark:bg-surface-dark dark:text-ink-dark">
        <p><span className="text-muted dark:text-muted-dark">Doctor: </span>{details.doctorName}</p>
        <p><span className="text-muted dark:text-muted-dark">Date: </span>{details.date}</p>
        <p><span className="text-muted dark:text-muted-dark">Time: </span>{details.time}</p>
        <p><span className="text-muted dark:text-muted-dark">Reason: </span>{details.reason}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          disabled={isBooking}
          className="flex-1 rounded-lg bg-accent py-2 text-sm font-medium text-white transition hover:bg-accent-light disabled:opacity-60"
        >
          {isBooking ? 'Booking…' : 'Confirm & Book'}
        </button>
        <button
          onClick={onCancel}
          disabled={isBooking}
          className="flex-1 rounded-lg border border-ink/15 py-2 text-sm font-medium text-ink transition hover:bg-ink/5 dark:border-ink-dark/15 dark:text-ink-dark"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}