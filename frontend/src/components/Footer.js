// Basic footer component for Project Puzzle.
// Intentionally lightweight; can later be expanded with links, metadata,
// or status information about the puzzle tasks.

import React from 'react';

const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <p>Project Puzzle &copy; {year}. Placeholder UI ready for future tasks.</p>
    </footer>
  );
};

export default Footer;
