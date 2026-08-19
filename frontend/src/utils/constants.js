/**
 * Application-wide constants for the AI Product Intelligence Platform.
 * Reference: architecture_final.md §8 (API Design), §9 (Frontend Design)
 */

/** API Configuration */
export const API = {
  BASE_URL: 'https://product-intelligence-zpj7.onrender.com',
  TIMEOUT: 30000,
  ENDPOINTS: {
    ANALYZE: '/analyze',
    UPLOAD_DOCUMENT: '/upload-document',
    HISTORY: '/history',
    HEALTH: '/health',
    DOWNLOAD_JSON: '/download-json',
    DOWNLOAD_PDF: '/download-pdf',
  },
};

/** Agent definitions for the multi-agent pipeline */
export const AGENTS = {
  RETRIEVAL: { id: 'retrieval', label: 'Retrieval Agent', order: 0 },
  INTELLIGENCE: { id: 'intelligence', label: 'Product Intelligence Agent', order: 1 },
  VALIDATION: { id: 'validation', label: 'Validation & Confidence Agent', order: 2 },
};

/** Agent status values */
export const AGENT_STATUS = {
  PENDING: 'pending',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

/** Confidence thresholds */
export const CONFIDENCE = {
  HIGH: 0.8,
  MEDIUM: 0.5,
  LOW: 0.0,
};

/** Color coding for confidence levels */
export const CONFIDENCE_COLORS = {
  HIGH: 'success',
  MEDIUM: 'warning',
  LOW: 'error',
};

/** Validation status values */
export const VALIDATION_STATUS = {
  VERIFIED: 'verified',
  PARTIAL: 'partial',
  UNVERIFIED: 'unverified',
  CONTRADICTED: 'contradicted',
};

/** Navigation routes */
export const ROUTES = {
  HOME: '/',
  ANALYSIS: '/analysis',
  HISTORY: '/history',
  ABOUT: '/about',
};

/** Default pagination */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
};
