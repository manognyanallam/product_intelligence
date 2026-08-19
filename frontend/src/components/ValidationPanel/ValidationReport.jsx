/**
 * ValidationReport — Displays validation results for each attribute
 * 
 * Shows per-attribute verification status:
 * - Verified (green check)
 * - Partial (yellow warning)
 * - Unverified (red error)
 * - Contradicted (red X)
 * Reference: architecture_final.md §10 (Validation Report)
 */
import React from 'react';
import { Box, Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';

const statusIcons = {
  verified: <CheckCircleIcon color="success" />,
  partial: <WarningIcon color="warning" />,
  unverified: <ErrorIcon color="error" />,
  contradicted: <ErrorIcon color="error" />,
};

function ValidationReport({ checks }) {
  if (!checks || checks.length === 0) return null;

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>Validation Report</Typography>
      <List dense>
        {checks.map((check, index) => (
          <ListItem key={index}>
            <ListItemIcon sx={{ minWidth: 36 }}>
              {statusIcons[check.status] || <WarningIcon />}
            </ListItemIcon>
            <ListItemText
              primary={check.attribute}
              secondary={check.message}
              primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

export default ValidationReport;
