// apps/web/src/lib/useApiData.ts
// Custom hook for API data fetching with mock fallback

import { useState, useEffect, useCallback } from 'react';

export type DataSourceState = 'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING';

interface UseApiDataOptions<T> {
  apiFn: () => Promise<T>;
  mockData: T;
  requiredFields?: (keyof T)[];
  enabled?: boolean;
}

interface UseApiDataResult<T> {
  data: T;
  state: DataSourceState;
  error: Error | null;
  refetch: () => void;
}

export function useApiData<T>({
  apiFn,
  mockData,
  requiredFields = [],
  enabled = true,
}: UseApiDataOptions<T>): UseApiDataResult<T> {
  const [apiResult, setApiResult] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    if (!enabled) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFn();
      setApiResult(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setApiResult(null);
    } finally {
      setLoading(false);
    }
  }, [apiFn, enabled]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Determine data source state
  let state: DataSourceState = 'MOCK';
  if (loading) state = 'LOADING';
  else if (error) state = 'ERROR';
  else if (apiResult !== null && apiResult !== undefined) {
    if (requiredFields.length > 0) {
      const hasAll = requiredFields.every(field => {
        const val = (apiResult as any)[field];
        if (Array.isArray(val)) return val.length > 0;
        if (typeof val === 'object' && val !== null) return Object.keys(val).length > 0;
        return val !== undefined && val !== null && val !== '';
      });
      state = hasAll ? 'LIVE' : 'PARTIAL';
    } else {
      state = 'LIVE';
    }
  }

  const data = (apiResult !== null && apiResult !== undefined ? apiResult : mockData) as T;

  return { data, state, error, refetch: fetchData };
}
