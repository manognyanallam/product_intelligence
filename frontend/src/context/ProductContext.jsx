/**
 * ProductContext — Shared state for product intelligence across components
 * 
 * Provides:
 * - Current product analysis state
 * - Analysis history
 * - Analysis actions (analyze, reset)
 * Reference: architecture_final.md §9.1 (App Shell)
 */
import React, { createContext, useContext, useMemo } from 'react';
import useProductIntelligence from '../hooks/useProductIntelligence';

const ProductContext = createContext(null);

/**
 * ProductProvider — Wraps the app with product intelligence state.
 * @param {Object} props - { children }
 */
export function ProductProvider({ children }) {
  const intelligence = useProductIntelligence();

  const value = useMemo(() => intelligence, [intelligence]);

  return (
    <ProductContext.Provider value={value}>
      {children}
    </ProductContext.Provider>
  );
}

/**
 * useProductContext — Hook to access product intelligence context.
 * @returns {Object} Product intelligence state and actions
 */
export function useProductContext() {
  const context = useContext(ProductContext);
  if (!context) {
    throw new Error('useProductContext must be used within a ProductProvider');
  }
  return context;
}

export default ProductContext;
