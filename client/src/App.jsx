import React from 'react'
import Header from './components/Header.jsx'

export default function App() {
  const [status, setStatus] = React.useState('loading...')
  React.useEffect(() => {
    fetch('/api/health').then(r => r.json()).then(d => setStatus(d.status)).catch(() => setStatus('error'))
  }, [])
  return (
    <div style={{fontFamily:'system-ui'}}>
      <Header />
      <main style={{ padding: 24 }}>
        <h1>PuzzleVerse MERN Starter</h1>
        <p>API status: {status}</p>
        <InfoPanel />
      </main>
    </div>
  )
}

function InfoPanel() {
  return (
    <section style={{ marginTop: 24, padding: 16, border: '1px solid #e5e7eb', borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>About</h3>
      <ul>
        <li>This is a minimal MERN starter structured for task-based grading.</li>
        <li>Client is powered by Vite + React.</li>
        <li>Server is Express with a health endpoint.</li>
      </ul>
    </section>
  )
}
