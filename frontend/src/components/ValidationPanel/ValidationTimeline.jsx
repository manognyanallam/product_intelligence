/**
 * ValidationTimeline — Displays the agent processing timeline
 * 
 * Shows the three agents (Retrieval, Intelligence, Validation) with:
 * - Status (completed, active, pending)
 * - Duration
 * - Key metrics
 * Reference: architecture_final.md §11.2 (Agent Timeline)
 */
import React from 'react';
import {
  Box, Typography, Stepper, Step, StepLabel, StepContent, Paper, Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

const defaultSteps = [
  { label: 'Retrieval Agent', description: 'Searching ChromaDB and cache for product information...' },
  { label: 'Product Intelligence Agent', description: 'Generating structured product attributes via Gemini...' },
  { label: 'Validation & Confidence Agent', description: 'Validating data, assigning confidence scores, tracking sources...' },
];

function ValidationTimeline({ activeStep = -1, steps = defaultSteps, metrics }) {
  return (
    <Box sx={{ maxWidth: 400 }}>
      <Typography variant="subtitle2" gutterBottom>Agent Timeline</Typography>
      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={index}>
            <StepLabel
              StepIconComponent={() => {
                if (index < activeStep) return <CheckCircleIcon color="success" />;
                if (index === activeStep) return <HourglassEmptyIcon color="primary" />;
                return <HourglassEmptyIcon color="disabled" />;
              }}
            >
              <Typography variant="body2" fontWeight={500}>{step.label}</Typography>
            </StepLabel>
            <StepContent>
              <Typography variant="caption" color="text.secondary">
                {step.description}
              </Typography>
              {metrics && metrics[index] && (
                <Chip label={`${metrics[index].duration_ms}ms`} size="small" variant="outlined" sx={{ mt: 0.5 }} />
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
}

export default ValidationTimeline;
