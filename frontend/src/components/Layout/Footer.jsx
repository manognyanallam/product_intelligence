/**
 * Footer — Site footer with links and attribution
 * 
 * Displays copyright, version info, and links.
 * Reference: architecture_final.md §9.1 (App Shell)
 */
import React from 'react';
import { Box, Container, Typography, Link, Divider } from '@mui/material';

function Footer() {
  return (
    <Box component="footer" sx={{ bgcolor: 'grey.100', py: 3, mt: 4 }}>
      <Container maxWidth="xl">
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          <Typography variant="body2" color="text.secondary">
            © 2025 AI Product Intelligence Platform
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Link href="https://github.com" target="_blank" variant="body2" color="text.secondary">
              GitHub
            </Link>
            <Link href="#" variant="body2" color="text.secondary">
              Documentation
            </Link>
            <Typography variant="body2" color="text.secondary">
              v2.0.0
            </Typography>
          </Box>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Built for UniHack by Unilog 2025
        </Typography>
      </Container>
    </Box>
  );
}

export default Footer;

