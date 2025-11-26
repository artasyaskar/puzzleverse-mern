// Top-level React component for the Project Puzzle frontend.
// This file currently only wires up high-level layout and placeholder routes.
// Routes are placeholders. Will link to real task pages later.

import React from 'react';
import { Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import Footer from './components/Footer';
import Dashboard from './components/Dashboard';

import Home from './pages/Home';
import Tasks from './pages/Tasks';

const App = () => {
  return (
    <div className="app-shell">
      {/* Simple app shell with header, main content, and footer. */}
      <Header />

      <main className="app-main">
        {/* Placeholder routing setup; more routes will be added as puzzle tasks grow. */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/tasks" element={<Tasks />} />
          {/* Dashboard is kept separate so it can be extended later. */}
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
};

export default App;
