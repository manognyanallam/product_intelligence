/**
 * ConfidenceBadge — Displays a confidence score as a colored chip
 * 
 * Color coding:
 * - Green: >= 0.8 (high confidence)
 * - Yellow: >= 0.5 (medium confidence)
 * - Red: < 0.5 (low confidence)
 * Reference: architecture_final.md §10 (Confidence Meter)
 */
import React from 'react';
import { Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';

function ConfidenceBadge({ score, size = 'small' }) {
  const pct = (score * 100).toFixed(0);
  let color = 'error';
  let icon = <ErrorIcon />;

  if (score >= 0.8) {
    color = 'success';
    icon = <CheckCircleIcon />;
  } else if (score >= 0.5) {
    color = 'warning';
    icon = <WarningIcon />;
  }

  return (
    <Chip
      icon={icon}
      label={`${pct}%`}
      color={color}
      size={size}
      variant="outlined"
    />
  );
}

export default ConfidenceBadge;
