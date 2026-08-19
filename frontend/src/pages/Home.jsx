/**
 * Home Page — Landing page with hero section and feature highlights
 * 
 * Displays:
 * - Hero section with value proposition
 * - Three-step quick start guide
 * - Feature highlights (confidence scoring, source attribution, RAG pipeline)
 * - Call-to-action button to navigate to Analysis page
 * Reference: architecture_final.md §9.2 (Home Page)
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Button, Box, Grid, Card, CardContent, Stack
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import FactCheckIcon from '@mui/icons-material/FactCheck';

const features = [
  {
    icon: <SearchIcon sx={{ fontSize: 40 }} />,
    title: 'Retrieval-Augmented Generation',
    description: 'Retrieve relevant product specifications from vector database before generating intelligence.',
  },
  {
    icon: <AutoAwesomeIcon sx={{ fontSize: 40 }} />,
    title: 'Multi-Agent AI Pipeline',
    description: 'Three specialized agents collaborate: Retrieval, Intelligence, and Validation for accurate results.',
  },
  {
    icon: <FactCheckIcon sx={{ fontSize: 40 }} />,
    title: 'Confidence Scoring & Validation',
    description: 'Every attribute includes a confidence score and source attribution for trust and explainability.',
  },
];

function Home() {
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero Section */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 8 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h2" fontWeight={700} gutterBottom>
            AI Product Intelligence Platform
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
            Turn minimal product data — MPN, Brand, and Description — into rich,
            structured, validated commerce-ready product intelligence.
          </Typography>
          <Button
            variant="contained"
            size="large"
            color="secondary"
            onClick={() => navigate('/analysis')}
            sx={{ px: 6, py: 1.5, fontSize: '1.1rem' }}
          >
            Start Analysis
          </Button>
        </Container>
      </Box>

      {/* Quick Start Guide */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" align="center" gutterBottom fontWeight={600}>
          How It Works
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center" sx={{ mb: 6 }}>
          <Box sx={{ textAlign: 'center', px: 3 }}>
            <Typography variant="h5" color="primary" fontWeight={700}>1</Typography>
            <Typography variant="body1">Enter MPN, Brand & Description</Typography>
          </Box>
          <Box sx={{ textAlign: 'center', px: 3 }}>
            <Typography variant="h5" color="primary" fontWeight={700}>2</Typography>
            <Typography variant="body1">AI Enriches with Specs & Attributes</Typography>
          </Box>
          <Box sx={{ textAlign: 'center', px: 3 }}>
            <Typography variant="h5" color="primary" fontWeight={700}>3</Typography>
            <Typography variant="body1">Export JSON or PDF</Typography>
          </Box>
        </Stack>

        {/* Feature Cards */}
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card sx={{ textAlign: 'center', py: 3, height: '100%' }}>
                <CardContent>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}

export default Home;

