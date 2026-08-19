/**
 * Utility functions for formatting product intelligence data.
 * Reference: architecture_final.md §8 (API Response Schemas)
 */

/**
 * Format a confidence score as a percentage string.
 * @param {number} score - Confidence score (0.0 – 1.0)
 * @returns {string} Formatted percentage (e.g., "94%")
 */
export const formatConfidence = (score) => {
  if (score === null || score === undefined) return 'N/A';
  return `${(score * 100).toFixed(0)}%`;
};

/**
 * Format a timestamp to a human-readable date string.
 * @param {string} isoString - ISO 8601 timestamp
 * @returns {string} Formatted date string
 */
export const formatTimestamp = (isoString) => {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format a duration in milliseconds to a human-readable string.
 * @param {number} ms - Duration in milliseconds
 * @returns {string} Formatted duration (e.g., "1.2s" or "320ms")
 */
export const formatDuration = (ms) => {
  if (ms === null || ms === undefined) return 'N/A';
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
};

/**
 * Convert a product intelligence response to CSV format.
 * @param {Object} data - ProductIntelligenceResponse
 * @returns {string} CSV string
 */
export const toCSV = (data) => {
  if (!data || !data.enriched_data) return '';
  const specs = data.enriched_data.specifications || {};
  const headers = ['Attribute', 'Value', 'Confidence'];
  const rows = Object.entries(specs).map(([key, value]) => {
    const confidence = data.confidence_scores?.attributes?.[key] || 0;
    return [key, value, formatConfidence(confidence)].join(',');
  });
  return [headers.join(','), ...rows].join('\n');
};

/**
 * Validate a product input object.
 * @param {Object} input - { mpn, brand, description }
 * @returns {Object} { valid: boolean, errors: { field: message } }
 */
export const validateProductInput = (input) => {
  const errors = {};
  if (!input.mpn?.trim()) errors.mpn = 'Manufacturer Part Number is required';
  if (!input.brand?.trim()) errors.brand = 'Brand is required';
  if (!input.description?.trim()) errors.description = 'Short description is required';
  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
};
