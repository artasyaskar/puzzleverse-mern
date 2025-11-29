import React from 'react'

export default function App() {
  const [status, setStatus] = React.useState('loading...')
  React.useEffect(() => {
    fetch('/api/health').then(r => r.json()).then(d => setStatus(d.status)).catch(() => setStatus('error'))
  }, [])
  return (
    <div style={{fontFamily:'system-ui', padding: 24}}>
      <h1>PuzzleVerse MERN Starter</h1>
      <p>API status: {status}</p>
    </div>
  )
}
