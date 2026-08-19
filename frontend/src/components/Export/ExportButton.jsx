/**
 * ExportButton — Handles JSON and PDF export of product intelligence
 * 
 * Two buttons:
 * - Download JSON: Calls GET /download-json/{productId}
 * - Download PDF: Calls GET /download-pdf/{productId}
 * Reference: architecture_final.md §10 (Export)
 */
import React from 'react';
import { Button, Stack } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

function ExportButton({ productId, onExportJSON, onExportPDF }) {
  const handleExportJSON = async () => {
    if (onExportJSON) {
      onExportJSON(productId);
    } else {
      // Default: trigger download via API
      const url = `${process.env.REACT_APP_API_URL}/download-json/${productId}`;
      window.open(url, '_blank');
    }
  };

  const handleExportPDF = async () => {
    if (onExportPDF) {
      onExportPDF(productId);
    } else {
      const url = `${process.env.REACT_APP_API_URL}/download-pdf/${productId}`;
      window.open(url, '_blank');
    }
  };

  return (
    <Stack direction="row" spacing={2}>
      <Button
        variant="contained"
        startIcon={<DownloadIcon />}
        onClick={handleExportJSON}
      >
        Download JSON
      </Button>
      <Button
        variant="contained"
        color="secondary"
        startIcon={<PictureAsPdfIcon />}
        onClick={handleExportPDF}
      >
        Download PDF
      </Button>
    </Stack>
  );
}

export default ExportButton;
