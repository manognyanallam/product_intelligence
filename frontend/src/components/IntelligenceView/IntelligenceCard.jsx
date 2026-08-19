/**
 * IntelligenceCard — Displays a single product intelligence attribute
 * 
 * Shows attribute name, value, and confidence badge.
 * Reference: architecture_final.md §10 (Dashboard Components)
 */
import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import ConfidenceBadge from './ConfidenceBadge';

function IntelligenceCard({ title, children, confidence }) {
  return (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle2" color="text.secondary">
            {title}
          </Typography>
          {confidence !== undefined && <ConfidenceBadge score={confidence} />}
        </Box>
        {children}
      </CardContent>
    </Card>
  );
}

export default IntelligenceCard;
