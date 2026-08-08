/**
 * Design tokens shared between `tailwind.config.js` and any place that
 * needs raw hex values (charts, inline styles, canvas drawing, etc).
 * Keep this file as the single source of truth for brand colors so the
 * Tailwind config and runtime chart code never drift apart.
 */

export const primary = {
  50: '#f5f3ff',
  100: '#ede9fe',
  200: '#ddd6fe',
  300: '#c4b5fd',
  400: '#a78bfa',
  500: '#8b5cf6',
  600: '#7c3aed',
  700: '#6d28d9',
  800: '#5b21b6',
  900: '#4c1d95',
} as const;

export const secondary = {
  50: '#fff1f2',
  100: '#ffe4e6',
  200: '#fecdd3',
  300: '#fda4af',
  400: '#fb7185',
  500: '#f43f5e',
  600: '#e11d48',
  700: '#be123c',
  800: '#9f1239',
  900: '#881337',
} as const;

export const neutral = {
  50: '#fafafa',
  100: '#f4f4f5',
  200: '#e4e4e7',
  300: '#d4d4d8',
  400: '#a1a1aa',
  500: '#71717a',
  600: '#52525b',
  700: '#3f3f46',
  800: '#27272a',
  900: '#18181b',
  950: '#09090b',
} as const;

/** Colors used for the three fusion tiers in the dashboard cockpit view. */
export const tierColors = {
  early: primary[400],
  mid: secondary[400],
  late: neutral[300],
  final: primary[500],
} as const;

/** Colors used per input modality (distinct from emotion tag colors). */
export const modalityColors = {
  text: primary[400],
  audio: secondary[400],
  facial: '#38bdf8',
} as const;
