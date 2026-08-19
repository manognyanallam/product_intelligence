/**
 * Header — Top app bar with navigation
 * 
 * Displays the app title, navigation links (Home, Analysis, History, About),
 * and a theme toggle. Uses Material UI AppBar.
 * Reference: architecture_final.md §9.1 (App Shell)
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Box, Container
} from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';

const navItems = [
  { label: 'Home', path: '/' },
  { label: 'Analysis', path: '/analysis' },
  { label: 'History', path: '/history' },
  { label: 'About', path: '/about' },
];

function Header() {
  const location = useLocation();

  return (
    <AppBar position="sticky" elevation={1}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Logo / Title */}
          <MemoryIcon sx={{ display: 'flex', mr: 1 }} />
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              fontWeight: 700,
              color: 'inherit',
              textDecoration: 'none',
              flexGrow: 0,
              mr: 4,
            }}
          >
            Product Intelligence
          </Typography>

          {/* Navigation Links */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                sx={{
                  color: 'white',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                  borderBottom: location.pathname === item.path ? '2px solid white' : '2px solid transparent',
                  borderRadius: 0,
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Header;

