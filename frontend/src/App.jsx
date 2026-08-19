/**
 * AI Product Intelligence Platform — App Root Component
 * 
 * Sets up Material UI theme, React Router, and global layout.
 * Pages: Home, Analysis, History, About, Dashboard
 * Reference: architecture_final.md §9.1 (Page Structure)
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Layout Components
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';

// Pages
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import History from './pages/History';
import About from './pages/About';

// Create Material UI theme
const theme = createTheme({
  palette: {
    primary: { main: '#1565c0' },
    secondary: { main: '#00897b' },
    background: { default: '#f5f5f5' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Header />
        <main style={{ minHeight: 'calc(100vh - 160px)' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/analysis/:productId" element={<Analysis />} />
            <Route path="/history" element={<History />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </Router>
    </ThemeProvider>
  );
}

export default App;

