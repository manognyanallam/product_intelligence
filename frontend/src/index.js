/**
 * AI Product Intelligence Platform — Frontend Entry Point
 * 
 * Renders the React application with Material UI theme and routing.
 * Reference: architecture_final.md §9 (Frontend Design)
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

