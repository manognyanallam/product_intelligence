/**
 * Analysis Page — Main product intelligence interface
 * 
 * Two-panel layout:
 * - Left: Input form (MPN, Brand, Description)
 * - Right: Dashboard with results (after analysis)
 * 
 * Displays agent timeline during processing.
 * Reference: architecture_final.md §9.2 (Analysis Page)
 * Reference: architecture_final.md §10 (Dashboard Components)
 */
import React from 'react';
import { Container, Grid, Paper, Typography, Alert } from '@mui/material';
import ProductForm from '../components/ProductInput/ProductForm';
import Dashboard from './Dashboard';
import { useProductIntelligence } from '../hooks/useProductIntelligence';

function Analysis() {
  const { loading, error, result, analyze } = useProductIntelligence();

  const handleAnalyze = async (formData) => {
    console.log('[Analysis] Analyze clicked with:', formData);
    await analyze(formData.mpn, formData.brand, formData.description);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Product Analysis
      </Typography>

      <Grid container spacing={3}>
        {/* Left Panel — Input Form */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Input Product Information
            </Typography>
            <ProductForm
              onAnalyze={handleAnalyze}
              isLoading={loading}
            />
          </Paper>
        </Grid>

        {/* Right Panel — Dashboard / Results */}
        <Grid item xs={12} md={8}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {loading ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6">Analyzing product...</Typography>
              {/* Agent Timeline visualization will go here */}
            </Paper>
          ) : result ? (
            <Dashboard data={result} />
          ) : (
            <Paper sx={{ p: 6, textAlign: 'center', bgcolor: 'grey.50' }}>
              <Typography variant="h6" color="text.secondary">
                Enter product information and click "Analyze" to generate intelligence
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default Analysis;

