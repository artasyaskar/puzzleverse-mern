// Simple header component for Project Puzzle.
// This will eventually host navigation, branding, and quick access links
// related to various puzzle tasks.

import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="app-header">
      <div className="header-inner">
        <h1 className="logo">Project Puzzle</h1>
        <nav className="nav-links">
          {/* Routes kept minimal for now; more entries can be added as needed. */}
          <Link to="/">Home</Link>
          <Link to="/tasks">Tasks</Link>
          <Link to="/dashboard">Dashboard</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
