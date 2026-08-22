/**
 * API Service — Axios client for backend communication
 *
 * Provides methods for all API endpoints defined in architecture_final.md §8.
 * Endpoints:
 * - POST /analyze          — Analyze product and generate intelligence
 * - POST /upload-document  — Upload product document (PDF) for RAG
 * - GET  /history          — Get analysis history
 * - GET  /health           — Health check
 * - GET  /download-json    — Download analysis as JSON
 * - GET  /download-pdf     — Download analysis as PDF report
 * Reference: architecture_final.md §8 (API Design)
 */
import axios from 'axios';

const getApiBaseUrl = () => {
  const hostname = typeof window !== 'undefined' ? window.location?.hostname : '';
  const isLocalFrontend = hostname === 'localhost' || hostname === '127.0.0.1';

  // An explicit API URL is authoritative, including for LAN deployments.
  // Set REACT_APP_API_URL to the backend's reachable LAN address, e.g.
  // http://192.168.1.11:8000/api/v1
  const configuredApiUrl = process.env.REACT_APP_API_URL;
  const isProduction = process.env.NODE_ENV === 'production';
  const pointsToLocalhost = configuredApiUrl && /localhost|127\.0\.0\.1/.test(configuredApiUrl);

  // Do not ship a development localhost URL in a production bundle.
  if (configuredApiUrl && !(isProduction && pointsToLocalhost)) {
    return configuredApiUrl.replace(/\/$/, '');
  }

  if (isLocalFrontend) {
    return `http://${hostname}:8000/api/v1`;
  }

  if (hostname) {
    // Production frontend deployments use the deployed Render backend rather
    // than attempting to reach port 8000 on the frontend host.
    return 'https://product-intelligence-zpj7.onrender.com/api/v1';
  }

  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();
const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';
if (IS_DEVELOPMENT) console.log('[API DEBUG] Base URL:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120 seconds — Gemini analysis can take time
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — log request details
apiClient.interceptors.request.use(
  (config) => {
    if (IS_DEVELOPMENT) {
      const fullUrl = `${config.baseURL || ''}${config.url || ''}`;
      console.log('[API DEBUG] Request:', config.method?.toUpperCase(), fullUrl);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle errors and distinguish exact error types
apiClient.interceptors.response.use(
  (response) => {
    if (IS_DEVELOPMENT) {
      console.log('[API DEBUG] Response:', response.status, response.config?.url);
    }
    return response.data;
  },
  (error) => {
    let message = '';

    if (error.response) {
      // 1. Axios HTTP Error (Backend responded with status outside 2xx)
      const status = error.response.status;
      const detail = error.response.data?.detail;

      if (typeof detail === 'string') {
        message = `[HTTP ${status}] ${detail}`;
      } else if (Array.isArray(detail)) {
        message = `[HTTP ${status} Validation Error] ` + detail.map((e) => e.msg || JSON.stringify(e)).join('; ');
      } else if (detail && typeof detail === 'object') {
        message = `[HTTP ${status}] ${detail.message || detail.code || JSON.stringify(detail)}`;
      } else {
        message = `[HTTP ${status}] ${error.response.statusText || 'Server Error'}`;
      }
      console.error('[API DEBUG] Axios HTTP Error:', status, message, error.config?.url);
    } else if (error.request) {
      // 2. Request made but no response received (Network Error, CORS, Timeout, Server Down)
      const currentOrigin = typeof window !== 'undefined' && window.location ? window.location.origin : 'unknown';
      const targetUrl = error.config ? `${error.config.baseURL || ''}${error.config.url || ''}` : API_BASE_URL;

      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        message = `[Timeout Error] Request to ${targetUrl} timed out after 120s. Backend is not responding.`;
      } else if (error.message === 'Network Error') {
        message = `[Network Error / CORS Failure] Unable to connect to backend at ${targetUrl}. Ensure Uvicorn is running with host 0.0.0.0 on port 8000 and CORS allows origin ${currentOrigin}.`;
      } else {
        message = `[Backend Unavailable] Connection error to ${targetUrl}: ${error.message || 'No response from server'}`;
      }
      console.error('[API DEBUG] Axios Connection Error:', message, error);
    } else {
      // 3. Request setup error (Invalid URL, config issue)
      message = `[Request Setup Error / Invalid URL] ${error.message}`;
      console.error('[API DEBUG] Axios Request Setup Error:', message, error);
    }

    return Promise.reject(new Error(message));
  }
);


/**
 * Analyze a product and generate intelligence.
 * POST /api/v1/analyze
 * @param {string} mpn - Manufacturer Part Number
 * @param {string} brand - Brand name
 * @param {string} description - Short product description
 * @returns {Promise<Object>} ProductIntelligenceResponse
 */
export const analyzeProduct = async (mpn, brand, description) => {
  if (IS_DEVELOPMENT) {
    console.log('[API DEBUG] Analyze request:', { mpn, brand, descriptionLength: description?.length });
  }
  return apiClient.post('/api/v1/analyze', { mpn, brand, description });
};

/**
 * Upload a document (PDF) for RAG ingestion.
 * POST /api/v1/upload-document
 * @param {FormData} formData - Multipart form with file and optional mpn
 * @returns {Promise<Object>} { document_id, chunks_created, status }
 */
export const uploadDocument = async (formData) => {
  return apiClient.post('api/v1/upload-document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/**
 * Get analysis history.
 * GET /api/v1/history
 * @param {number} page - Page number
 * @param {number} limit - Items per page
 * @returns {Promise<Object>} { results, total, page, limit }
 */
export const getHistory = async (page = 1, limit = 10) => {
  return apiClient.get('api/v1/history', { params: { page, limit } });
};

/**
 * Health check endpoint.
 * GET /api/v1/health
 * @returns {Promise<Object>} { status, version, uptime, chromadb, gemini }
 */
export const getHealth = async () => {
  return apiClient.get('api/v1/health');
};

/** Run the 200-item ground-truth evaluation. */
export const evaluateDataset = async () => apiClient.post('api/v1/evaluate');

/** Process the 1000-item scale dataset after evaluation. */
export const process1000Dataset = async () => apiClient.post('api/v1/process-1000');

/**
 * Download analysis as JSON.
 * GET /api/v1/download-json/{productId}
 * @param {string} productId - Product ID
 * @returns {Promise<Blob>} JSON file
 */
export const downloadJson = async (productId) => {
  return apiClient.get(`api/v1/download-json/${productId}`, {
    responseType: 'blob',
  });
};

/**
 * Download analysis as PDF report.
 * GET /api/v1/download-pdf/{productId}
 * @param {string} productId - Product ID
 * @returns {Promise<Blob>} PDF file
 */
export const downloadPdf = async (productId) => {
  return apiClient.get(`api/v1/download-pdf/${productId}`, {
    responseType: 'blob',
  });
};

export default apiClient;
