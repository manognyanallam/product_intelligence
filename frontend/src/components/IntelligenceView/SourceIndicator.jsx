/**
 * SourceIndicator — Displays source attribution for a data point
 * 
 * Shows source name, type, and relevance score.
 * Reference: architecture_final.md §10 (Sources)
 */
import React from 'react';
import { Box, Typography, Chip, Stack } from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import StorageIcon from '@mui/icons-material/Storage';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const sourceIcons = {
  datasheet: <ArticleIcon fontSize="small" />,
  vector_db: <StorageIcon fontSize="small" />,
  knowledge_base: <AutoAwesomeIcon fontSize="small" />,
};

function SourceIndicator({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>Sources</Typography>
      <Stack spacing={1}>
        {sources.map((source, index) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {sourceIcons[source.type] || <ArticleIcon fontSize="small" />}
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2">{source.name}</Typography>
              <Typography variant="caption" color="text.secondary">
                Relevance: {(source.relevance_score * 100).toFixed(0)}%
              </Typography>
            </Box>
            <Chip label={source.type} size="small" variant="outlined" />
          </Box>
        ))}
      </Stack>
    </Box>
  );
}

export default SourceIndicator;
