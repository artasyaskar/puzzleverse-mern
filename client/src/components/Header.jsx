import React from 'react'

export default function Header({ title = 'PuzzleVerse MERN' }) {
  return (
    <header style={{
      padding: '16px 24px',
      borderBottom: '1px solid #e5e7eb',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: '#fafafa'
    }}>
      <h2 style={{ margin: 0, fontSize: 18 }}>{title}</h2>
      <nav style={{ display: 'flex', gap: 12 }}>
        <a href="/" style={{ color: '#2563eb', textDecoration: 'none' }}>Home</a>
        <a href="https://github.com/artasyaskar/puzzleverse-mern" target="_blank" rel="noreferrer" style={{ color: '#2563eb', textDecoration: 'none' }}>Repo</a>
      </nav>
    </header>
  )
}
