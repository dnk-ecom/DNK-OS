// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/design-system/tokens.ts"
// purpose: "TypeScript Design Tokens and Theme Provider contracts uniting Shopify Polaris 13+ with Dark Teal Spatial Canvas."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-26"
// author: "Antigravity & Gerych Prime"
// --- END DNK-MRH-HEADER ---

export interface SpatialCanvasTokens {
  bgAbyss: string;
  surfaceCard: string;
  surfaceElevated: string;
  borderSubtle: string;
  borderFocus: string;
  accentCyan: string;
  accentEmerald: string;
  accentAmber: string;
  accentRose: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
}

export interface ShopifyPolarisTokens {
  surfacePage: string;
  surfaceCard: string;
  borderSubdued: string;
  borderHover: string;
  interactivePrimary: string;
  interactiveHover: string;
  interactiveCritical: string;
  textDefault: string;
  textSubdued: string;
}

export interface TypographyTokens {
  fontFamilySans: string;
  fontFamilyMono: string;
  fontFamilyDisplay: string;
}

export interface SpacingTokens {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  "2xl": string;
}

export interface ElevationTokens {
  canvasNode: string;
  canvasNodeSelected: string;
  drawerFlyout: string;
}

export interface MotionTokens {
  transitionFast: string;
  transitionSpring: string;
}

export interface DnkPolarisDesignTokens {
  version: string;
  spatialCanvas: SpatialCanvasTokens;
  shopifyPolaris: ShopifyPolarisTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  elevation: ElevationTokens;
  motion: MotionTokens;
}

export const DNK_POLARIS_TOKENS: DnkPolarisDesignTokens = {
  version: "1.0.0",
  spatialCanvas: {
    bgAbyss: "#091114",
    surfaceCard: "#0f1d22",
    surfaceElevated: "#152830",
    borderSubtle: "#1e3842",
    borderFocus: "#14b8a6",
    accentCyan: "#38bdf8",
    accentEmerald: "#10b981",
    accentAmber: "#f59e0b",
    accentRose: "#f43f5e",
    textPrimary: "#f8fafc",
    textSecondary: "#94a3b8",
    textMuted: "#64748b",
  },
  shopifyPolaris: {
    surfacePage: "#f6f6f7",
    surfaceCard: "#ffffff",
    borderSubdued: "#e1e3e5",
    borderHover: "#8c9196",
    interactivePrimary: "#008060",
    interactiveHover: "#006e52",
    interactiveCritical: "#d82c0d",
    textDefault: "#202223",
    textSubdued: "#6d7175",
  },
  typography: {
    fontFamilySans: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
    fontFamilyMono: "'JetBrains Mono', 'Fira Code', monospace",
    fontFamilyDisplay: "Manrope, sans-serif",
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "32px",
    "2xl": "48px",
  },
  elevation: {
    canvasNode: "0 4px 14px 0 rgba(0, 0, 0, 0.45)",
    canvasNodeSelected: "0 0 0 2px #14b8a6, 0 8px 24px 0 rgba(20, 184, 166, 0.35)",
    drawerFlyout: "-8px 0 32px 0 rgba(0, 0, 0, 0.65)",
  },
  motion: {
    transitionFast: "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    transitionSpring: "300ms cubic-bezier(0.16, 1, 0.3, 1)",
  },
};
