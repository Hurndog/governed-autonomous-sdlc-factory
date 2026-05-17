// apps/web/src/lib/theme.ts
// Design tokens for the SDLC Factory command center

export const theme = {
  colors: {
    // Backgrounds
    bg: {
      base: '#0a0b0f',
      surface: '#111318',
      elevated: '#181b22',
      overlay: '#1e2230',
      hover: '#252a36',
    },
    // Borders
    border: {
      subtle: '#1e2230',
      default: '#2a2f3c',
      strong: '#3a4050',
      accent: '#4a5060',
    },
    // Text
    text: {
      primary: '#e8eaed',
      secondary: '#9ca3af',
      tertiary: '#6b7280',
      disabled: '#4b5563',
    },
    // Semantic
    green: '#34d399',
    greenDim: '#065f46',
    blue: '#60a5fa',
    blueDim: '#1e3a5f',
    amber: '#fbbf24',
    amberDim: '#78350f',
    red: '#f87171',
    redDim: '#7f1d1d',
    purple: '#a78bfa',
    purpleDim: '#4c1d95',
    cyan: '#22d3ee',
    cyanDim: '#164e63',
    violet: '#c084fc',
    violetDim: '#581c87',
  },
  // Chart palette
  chart: ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee', '#c084fc', '#fb923c'],
  // Spacing
  space: { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, '2xl': 32, '3xl': 48 },
  // Radius
  radius: { sm: 4, md: 8, lg: 12, xl: 16 },
  // Shadows
  shadow: {
    sm: '0 1px 2px rgba(0,0,0,0.3)',
    md: '0 4px 12px rgba(0,0,0,0.4)',
    lg: '0 8px 24px rgba(0,0,0,0.5)',
    glow: '0 0 20px rgba(96,165,250,0.15)',
  },
} as const;

export type Theme = typeof theme;
