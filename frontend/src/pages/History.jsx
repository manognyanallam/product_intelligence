/**
 * History Page — Past product analysis records
 *
 * Displays:
 * - Data table with columns: MPN, Brand, Description, Confidence, Timestamp, Actions
 * - Search bar for filtering by MPN or Brand
 * - Sort by date, confidence, or brand
 * - Click row to navigate to Analysis page with that product's results
 * - Empty state when no history exists
 * Reference: architecture_final.md §9.2 (History Page)
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TextField, Box, Chip
} from '@mui/material';

function History() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  // Placeholder: Replace with actual API call via useProductIntelligence hook
  const historyRows = [];

  const filteredRows = historyRows.filter(
    (row) =>
      row.mpn?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      row.brand?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Analysis History
      </Typography>

      {/* Search Bar */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search by MPN or Brand..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3 }}
      />

      {/* History Table */}
      <TableContainer component={Paper}>
        {filteredRows.length === 0 ? (
          <Box sx={{ py: 8, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No analysis history yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start by analyzing a product on the Analysis page
            </Typography>
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>MPN</TableCell>
                <TableCell>Brand</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredRows.map((row) => (
                <TableRow
                  key={row.id}
                  hover
                  sx={{ cursor: 'pointer' }}
                  onClick={() => navigate(row.id ? `/analysis/${row.id}` : '/analysis')}
                >
                  <TableCell>{row.mpn}</TableCell>
                  <TableCell>{row.brand}</TableCell>
                  <TableCell>{row.description}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${(row.confidence * 100).toFixed(0)}%`}
                      color={row.confidence > 0.8 ? 'success' : row.confidence > 0.5 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{row.timestamp}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </TableContainer>
    </Container>
  );
}

export default History;

