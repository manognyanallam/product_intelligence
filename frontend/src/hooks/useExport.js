/**
 * useExport — Custom hook for exporting product intelligence
 * 
 * Handles:
 * - JSON file download
 * - PDF report download
 * - Error handling during export
 * Reference: architecture_final.md §8 (API Design — Download endpoints)
 */
import { useState, useCallback } from 'react';
import { downloadJson, downloadPdf } from '../services/api';

/**
 * Hook for exporting product intelligence as JSON or PDF.
 */
export function useExport() {
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  /**
   * Trigger a file download in the browser.
   * @param {Blob} blob - File data
   * @param {string} filename - Download filename
   */
  const triggerDownload = useCallback((blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }, []);

  /**
   * Export product intelligence as JSON.
   * @param {string} productId - Product ID
   */
  const exportJSON = useCallback(async (productId) => {
    setExporting(true);
    setExportError(null);
    try {
      const blob = await downloadJson(productId);
      triggerDownload(blob, `product_${productId}.json`);
    } catch (err) {
      setExportError(err.message);
    } finally {
      setExporting(false);
    }
  }, [triggerDownload]);

  /**
   * Export product intelligence as PDF report.
   * @param {string} productId - Product ID
   */
  const exportPDF = useCallback(async (productId) => {
    setExporting(true);
    setExportError(null);
    try {
      const blob = await downloadPdf(productId);
      triggerDownload(blob, `product_${productId}.pdf`);
    } catch (err) {
      setExportError(err.message);
    } finally {
      setExporting(false);
    }
  }, [triggerDownload]);

  return {
    exporting,
    exportError,
    exportJSON,
    exportPDF,
  };
}

export default useExport;
