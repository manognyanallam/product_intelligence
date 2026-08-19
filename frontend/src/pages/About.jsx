/**
 * About Page — Project information and technology stack
 * 
 * Displays:
 * - Project description and hackathon context
 * - Architecture overview (simplified)
 * - Technology stack cards with icons
 * - Team information
 * Reference: architecture_final.md §9.2 (About Page)
 */
import React from 'react';
import {
  Container, Typography, Grid, Card, CardContent, Box, Chip, Stack
} from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const techStack = [
  { name: 'React 18', category: 'Frontend', icon: <CodeIcon /> },
  { name: 'Material UI', category: 'Frontend', icon: <CodeIcon /> },
  { name: 'FastAPI', category: 'Backend', icon: <StorageIcon /> },
  { name: 'Python 3.11', category: 'Backend', icon: <StorageIcon /> },
  { name: 'Google Gemini', category: 'AI', icon: <AutoAwesomeIcon /> },
  { name: 'LangChain', category: 'AI', icon: <AutoAwesomeIcon /> },
  { name: 'ChromaDB', category: 'Database', icon: <StorageIcon /> },
  { name: 'Vercel + Render', category: 'Deployment', icon: <CodeIcon /> },
];

function About() {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        About the Platform
      </Typography>

      <Typography variant="body1" paragraph>
        The AI Product Intelligence Platform was built for the <strong>UniHack by Unilog</strong> hackathon.
        It addresses a critical challenge in industrial commerce: transforming minimal manufacturer product
        information into rich, structured, validated product intelligence.
      </Typography>

      <Typography variant="body1" paragraph>
        Using a three-agent AI pipeline powered by <strong>Google Gemini</strong>, <strong>LangChain</strong>,
        and <strong>ChromaDB</strong>, the system retrieves relevant product knowledge, generates structured
        attributes, validates every data point, and assigns confidence scores — all in under 5 seconds.
      </Typography>

      {/* Technology Stack */}
      <Typography variant="h5" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
        Technology Stack
      </Typography>

      <Grid container spacing={2}>
        {techStack.map((tech, index) => (
          <Grid item xs={6} sm={3} key={index}>
            <Card variant="outlined" sx={{ textAlign: 'center', py: 2 }}>
              <CardContent>
                <Box sx={{ color: 'primary.main', mb: 1 }}>{tech.icon}</Box>
                <Typography variant="body2" fontWeight={600}>{tech.name}</Typography>
                <Chip label={tech.category} size="small" variant="outlined" sx={{ mt: 0.5 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Architecture Note */}
      <Typography variant="h5" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
        Architecture
      </Typography>
      <Typography variant="body2" color="text.secondary">
        See <code>architecture_final.md</code> for the complete system architecture,
        including folder structure, data flow, API design, database schema, multi-agent
        workflow, RAG pipeline, and deployment strategy.
      </Typography>
    </Container>
  );
}

export default About;

