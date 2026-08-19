/**
 * useProductIntelligence — Custom hook for product analysis state management
 * 
 * Manages:
 * - Loading state during analysis
 * - Product intelligence results
 * - Error handling
 * - History of past analyses
 * Reference: architecture_final.md §8 (API Design)
 */
import { useState, useCallback } from 'react';
import { analyzeProduct, getHistory } from '../services/api';

/**
 * Hook for managing product intelligence analysis workflow.
 */
export function useProductIntelligence() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [agentTimeline, setAgentTimeline] = useState([]);

  /**
   * Analyze a product by MPN, Brand, and Description.
   * @param {string} mpn - Manufacturer Part Number
   * @param {string} brand - Brand name
   * @param {string} description - Short product description
   */
  const analyze = useCallback(async (mpn, brand, description) => {
    setLoading(true);
    setError(null);
    setAgentTimeline([
      { agent: 'retrieval', status: 'pending' },
      { agent: 'intelligence', status: 'pending' },
      { agent: 'validation', status: 'pending' },
    ]);

    try {
      const data = await analyzeProduct(mpn, brand, description);
      console.log('[Analysis] Received data:', data);
      setResult(data);
      setAgentTimeline(data.agent_timeline || []);
    } catch (err) {
      console.error('[Analysis] Request error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch analysis history.
   * @param {number} page - Page number
   * @param {number} limit - Items per page
   */
  const fetchHistory = useCallback(async (page = 1, limit = 10) => {
    try {
      const data = await getHistory(page, limit);
      setHistory(data.results || []);
      return data;
    } catch (err) {
      setError(err.message);
      return { results: [], total: 0 };
    }
  }, []);

  /**
   * Reset the current analysis result.
   */
  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setAgentTimeline([]);
  }, []);

  return {
    loading,
    error,
    result,
    history,
    agentTimeline,
    analyze,
    fetchHistory,
    reset,
  };
}

export default useProductIntelligence;
