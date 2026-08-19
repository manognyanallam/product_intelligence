/**
 * ProductForm — Input form for product information
 * 
 * Accepts: Manufacturer Part Number, Brand, Short Description
 * Validates input before submitting to the analysis pipeline.
 * Reference: architecture_final.md §9.2 (Analysis Page — Input Form)
 */
import React from 'react';
import { TextField, Button, Stack, CircularProgress } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function ProductForm({ onAnalyze, isLoading }) {
  const [formData, setFormData] = React.useState({
    mpn: '',
    brand: '',
    description: '',
  });
  const [errors, setErrors] = React.useState({});

  const validate = () => {
    const newErrors = {};
    if (!formData.mpn.trim()) newErrors.mpn = 'MPN is required';
    if (!formData.brand.trim()) newErrors.brand = 'Brand is required';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onAnalyze(formData);
    }
  };

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: undefined });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack spacing={2.5}>
        <TextField
          label="Manufacturer Part Number"
          placeholder="e.g., SN74LS00N"
          value={formData.mpn}
          onChange={handleChange('mpn')}
          error={!!errors.mpn}
          helperText={errors.mpn}
          fullWidth
          required
          disabled={isLoading}
        />
        <TextField
          label="Brand"
          placeholder="e.g., Texas Instruments"
          value={formData.brand}
          onChange={handleChange('brand')}
          error={!!errors.brand}
          helperText={errors.brand}
          fullWidth
          required
          disabled={isLoading}
        />
        <TextField
          label="Short Description"
          placeholder="e.g., Quad 2-input NAND gate"
          value={formData.description}
          onChange={handleChange('description')}
          error={!!errors.description}
          helperText={errors.description}
          fullWidth
          required
          multiline
          rows={3}
          disabled={isLoading}
        />
        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Product'}
        </Button>
      </Stack>
    </form>
  );
}

export default ProductForm;
