/**
 * AttributeTable — Displays specification attributes in a table
 * 
 * Each row shows: attribute name, value, and confidence score.
 * Reference: architecture_final.md §10 (Specifications Table)
 */
import React from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography
} from '@mui/material';
import ConfidenceBadge from './ConfidenceBadge';

function AttributeTable({ attributes, confidenceScores = {}, title }) {
  if (!attributes || Object.keys(attributes).length === 0) return null;

  return (
    <TableContainer>
      {title && <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>{title}</Typography>}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600 }}>Attribute</TableCell>
            <TableCell sx={{ fontWeight: 600 }}>Value</TableCell>
            <TableCell sx={{ fontWeight: 600 }} align="right">Confidence</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(attributes).map(([key, value]) => {
            const score = confidenceScores[key] ?? null;
            return (
              <TableRow key={key}>
                <TableCell sx={{ fontWeight: 500 }}>{key}</TableCell>
                <TableCell>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</TableCell>
                <TableCell align="right">
                  {score !== null ? (
                    <ConfidenceBadge score={score} size="small" />
                  ) : (
                    <Typography variant="caption" color="text.secondary">N/A</Typography>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default AttributeTable;
