// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/VisualShellSidebar.tsx"
// purpose: "Icon-only collapsible sidebar for DNK OS Visual Shell. Navigation hub for all kernel modules."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Bot,
  Layers,
  GitBranch,
  ShoppingBag,
  BarChart3,
  Settings,
  Zap,
} from 'lucide-react';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Shell',    href: '/shell',    color: '#00dc82' },
  { icon: Bot,             label: 'Agents',   href: '/agents',   color: '#a78bfa' },
  { icon: Layers,          label: 'Services', href: '/services', color: '#22d3ee' },
  { icon: GitBranch,       label: 'Canvas',   href: '/canvas',   color: '#f59e0b' },
  { icon: ShoppingBag,     label: 'Shopify',  href: '/shopify',  color: '#34d399' },
  { icon: BarChart3,       label: 'Analytics',href: '/analytics',color: '#f472b6' },
];

export default function VisualShellSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[68px] bg-[#080b12] border-r border-white/[0.06] flex flex-col items-center py-3 gap-1 shrink-0 z-40">
      {/* Logo */}
      <Link href="/shell" className="mb-4 mt-1 flex items-center justify-center">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00dc82] to-[#00a854] flex items-center justify-center shadow-lg shadow-emerald-500/30 text-base select-none">
          🧬
        </div>
      </Link>

      {/* Nav items */}
      <div className="flex flex-col gap-1 w-full px-2">
        {NAV_ITEMS.map(({ icon: Icon, label, href, color }) => {
          const isActive = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link
              key={href}
              href={href}
              title={label}
              className={`
                group relative flex flex-col items-center justify-center w-full py-3 rounded-xl
                transition-all duration-200 cursor-pointer
                ${isActive
                  ? 'bg-white/[0.08]'
                  : 'hover:bg-white/[0.04]'}
              `}
              style={isActive ? { boxShadow: `0 0 0 1px ${color}33, inset 0 0 12px ${color}0d` } : {}}
            >
              <Icon
                size={20}
                style={{ color: isActive ? color : undefined }}
                className={isActive ? '' : 'text-slate-500 group-hover:text-slate-300 transition-colors'}
              />
              <span
                className="text-[9px] mt-1 font-medium tracking-wide"
                style={{ color: isActive ? color : undefined }}
              >
                {isActive ? <span className="opacity-90">{label}</span> : <span className="text-slate-600 group-hover:text-slate-400 transition-colors">{label}</span>}
              </span>
              {/* Active indicator dot */}
              {isActive && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full"
                  style={{ background: color }}
                />
              )}
            </Link>
          );
        })}
      </div>

      {/* Bottom */}
      <div className="mt-auto px-2 w-full">
        <button
          title="Settings"
          className="group flex flex-col items-center justify-center w-full py-3 rounded-xl hover:bg-white/[0.04] transition-colors"
        >
          <Settings size={18} className="text-slate-600 group-hover:text-slate-300 transition-colors" />
          <span className="text-[9px] mt-1 text-slate-600 group-hover:text-slate-400 transition-colors font-medium">Config</span>
        </button>

        {/* Kernel status */}
        <div className="flex items-center justify-center gap-1.5 py-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-[8px] text-emerald-500/70 font-mono uppercase tracking-widest">Live</span>
        </div>
      </div>
    </aside>
  );
}
