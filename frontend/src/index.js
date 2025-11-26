// Entry point for the Project Puzzle React frontend.
// This file is intentionally lightweight and only sets up the root render
// and wraps the main App component.

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    {/* Router is configured here so that App can focus on page layout. */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
