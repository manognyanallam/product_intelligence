/**
 * Dashboard — Product intelligence results display
 * 
 * Displays all generated intelligence in a structured layout:
 * - Overall Confidence Score & Confidence Meter
 * - Specifications Table with per-attribute confidence
 * - Features, Applications, SEO Keywords, Compliance
 * - Validation Report
 * - Sources used
 * - Export buttons (JSON, PDF)
 * Reference: architecture_final.md §10 (Dashboard Components)
 */
import React from 'react';
import {
  Paper, Typography, Grid, Box, Chip, LinearProgress, Stack
} from '@mui/material';
import AttributeTable from '../components/IntelligenceView/AttributeTable';
import ConfidenceBadge from '../components/IntelligenceView/ConfidenceBadge';
import SourceIndicator from '../components/IntelligenceView/SourceIndicator';
import ValidationReport from '../components/ValidationPanel/ValidationReport';
import ExportButton from '../components/Export/ExportButton';
import { downloadJson, downloadPdf } from '../services/api';

function Dashboard({ data }) {
  if (!data) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="text.secondary">No data to display</Typography>
      </Paper>
    );
  }

  // Support both direct root properties and nested response structure (ProductResponse contract)
  const enriched = data.enriched_data || {};
  const input = data.input || {};
  const confidenceObj = data.confidence || {};

  const mpn = enriched.mpn || input.mpn || data.mpn || 'N/A';
  const brand = enriched.brand || input.brand || data.brand || 'N/A';
  const category = enriched.category || data.category || 'Product Intelligence';
  const title = enriched.title || data.title || `${brand} ${mpn}`;
  const description = enriched.description || input.description || data.description || '';

  // Overall confidence score (0.0 to 1.0)
  const overallConfidence = confidenceObj.overall ?? data.overall_confidence ?? data.confidence ?? null;
  const attributeConfidenceMap = confidenceObj.attributes || data.confidence_scores?.attributes || {};

  // Lists & Maps
  const specifications = enriched.specifications || data.specifications || {};
  const features = enriched.features || data.features || [];
  const applications = enriched.applications || data.applications || [];
  const seoKeywords = enriched.seo_keywords || data.seo_keywords || [];
  const compliance = enriched.compliance || data.compliance || [];

  // Validation & Sources
  const validation = data.validation || {};
  const validationChecks = validation.checks || [];
  const sources = data.sources || [];
  const productId = data.product_id || 'latest';

  const handleExportJSON = async (id) => {
    try {
      const response = await downloadJson(id || productId);
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `product_intelligence_${id || productId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download JSON:', err);
    }
  };

  const handleExportPDF = async (id) => {
    try {
      const response = await downloadPdf(id || productId);
      const url = window.URL.createObjectURL(new Blob([response], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `product_intelligence_${id || productId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download PDF:', err);
    }
  };

  return (
    <Box>
      {/* Header Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" fontWeight={600} gutterBottom>
          {title}
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" gap={1} sx={{ mt: 1 }}>
          <Chip label={`MPN: ${mpn}`} variant="outlined" color="primary" />
          <Chip label={`Brand: ${brand}`} variant="outlined" />
          {category && <Chip label={category} color="secondary" variant="filled" />}
        </Stack>
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            {description}
          </Typography>
        )}
      </Paper>

      <Grid container spacing={3}>
        {/* Overall Confidence Meter */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Overall Confidence
            </Typography>
            {overallConfidence !== null ? (
              <>
                <Typography variant="h2" color="primary" fontWeight={700} sx={{ my: 1 }}>
                  {(overallConfidence * 100).toFixed(0)}%
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <ConfidenceBadge score={overallConfidence} size="medium" />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={overallConfidence * 100}
                  sx={{ height: 10, borderRadius: 5, mt: 2 }}
                />
              </>
            ) : (
              <Typography variant="body1" color="text.secondary">N/A</Typography>
            )}
          </Paper>
        </Grid>

        {/* Specifications Table */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Technical Specifications
            </Typography>
            <AttributeTable attributes={specifications} confidenceScores={attributeConfidenceMap} />
          </Paper>
        </Grid>

        {/* Features */}
        {features.length > 0 && (
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>Key Features</Typography>
              {features.map((feature, i) => (
                <Typography key={i} variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}>
                  <Box component="span" sx={{ mr: 1, color: 'primary.main', fontWeight: 'bold' }}>•</Box>
                  {feature}
                </Typography>
              ))}
            </Paper>
          </Grid>
        )}

        {/* Applications */}
        {applications.length > 0 && (
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>Applications</Typography>
              {applications.map((app, i) => (
                <Typography key={i} variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}>
                  <Box component="span" sx={{ mr: 1, color: 'secondary.main', fontWeight: 'bold' }}>•</Box>
                  {app}
                </Typography>
              ))}
            </Paper>
          </Grid>
        )}

        {/* SEO Keywords */}
        {seoKeywords.length > 0 && (
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>SEO Keywords</Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                {seoKeywords.map((kw, i) => (
                  <Chip key={i} label={kw} size="small" variant="outlined" color="info" />
                ))}
              </Stack>
            </Paper>
          </Grid>
        )}

        {/* Compliance */}
        {compliance.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>Compliance & Certifications</Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                {compliance.map((comp, i) => (
                  <Chip key={i} label={comp} size="small" color="success" variant="outlined" />
                ))}
              </Stack>
            </Paper>
          </Grid>
        )}

        {/* Validation Report */}
        {validationChecks.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <ValidationReport checks={validationChecks} />
            </Paper>
          </Grid>
        )}

        {/* Sources */}
        {sources.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <SourceIndicator sources={sources} />
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Export Buttons */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <ExportButton
          productId={productId}
          onExportJSON={handleExportJSON}
          onExportPDF={handleExportPDF}
        />
      </Box>
    </Box>
  );
}

export default Dashboard;
