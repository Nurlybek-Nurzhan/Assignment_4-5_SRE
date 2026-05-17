export default function StatusDot({ status }) {
  if (status === 'ok') {
    return (
      <span
        className="inline-block w-2.5 h-2.5 rounded-full bg-green-400 dot-pulse flex-shrink-0"
        style={{ color: '#4ade80' }}
        title="Healthy"
      />
    )
  }
  if (status === 'error') {
    return (
      <span
        className="inline-block w-2.5 h-2.5 rounded-full bg-red-500 flex-shrink-0"
        title="Error"
      />
    )
  }
  // loading / default
  return (
    <span
      className="inline-block w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse flex-shrink-0"
      title="Checking..."
    />
  )
}
