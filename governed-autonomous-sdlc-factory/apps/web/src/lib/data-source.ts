// apps/web/src/lib/data-source.ts
// Data source architecture: LIVE / PARTIAL / MOCK / ERROR states

export type DataSourceState = 'LIVE' | 'PARTIAL' | 'MOCK' | 'ERROR' | 'LOADING';

export interface DataSourceBadgeProps {
  state: DataSourceState;
  className?: string;
}

const stateConfig: Record<DataSourceState, { label: string; color: string; bg: string; border: string }> = {
  LIVE: { label: 'LIVE', color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20' },
  PARTIAL: { label: 'PARTIAL', color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20' },
  MOCK: { label: 'MOCK', color: 'text-zinc-400', bg: 'bg-zinc-700/30', border: 'border-zinc-600/30' },
  ERROR: { label: 'ERROR', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20' },
  LOADING: { label: 'LOADING', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20' },
};

export function getDataSourceConfig(state: DataSourceState) {
  return stateConfig[state] || stateConfig.MOCK;
}

// Helper to determine data source state from API result
export function resolveDataSourceState<T>(
  apiData: T | null | undefined,
  mockData: T,
  requiredFields: (keyof T)[]
): DataSourceState {
  if (apiData === null || apiData === undefined) return 'MOCK';
  
  const hasAllRequired = requiredFields.every(field => {
    const val = apiData[field];
    if (Array.isArray(val)) return val.length > 0;
    if (typeof val === 'object' && val !== null) return Object.keys(val).length > 0;
    return val !== undefined && val !== null && val !== '';
  });
  
  if (hasAllRequired) return 'LIVE';
  return 'PARTIAL';
}
