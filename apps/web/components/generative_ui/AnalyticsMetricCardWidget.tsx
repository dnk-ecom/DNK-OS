// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_generative_ui_AnalyticsMetricCardWidget"
// purpose: "Astryx Generative UI: Interactive E-Commerce & CRO Analytics Metric Card with Live Sparkline"
// author: "DNK-e.com Maksym & Denchik"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// --- END DNK-MRH-HEADER ---

"use client";

import React, { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Percent,
  Zap,
  Gauge,
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  Info,
  Calendar,
  Layers,
  Activity,
} from "lucide-react";

export interface AnalyticsMetricCardWidgetProps {
  title: string;
  value: string | number;
  changePercent: number;
  timeframe: string;
  metricType: "aov" | "cvr" | "revenue" | "speed";
  sparklineData?: number[];
  className?: string;
  onDrillDown?: () => void;
}

export const AnalyticsMetricCardWidget: React.FC<AnalyticsMetricCardWidgetProps> = ({
  title,
  value,
  changePercent,
  timeframe,
  metricType,
  sparklineData = [28, 34, 32, 45, 42, 58, 65, 60, 78],
  className = "",
  onDrillDown,
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const isPositive = changePercent >= 0;

  // Icon and theme config based on metricType
  const getMetricConfig = () => {
    switch (metricType) {
      case "aov":
        return {
          icon: <DollarSign className="h-4 w-4" />,
          label: "Average Order Value",
          color: "text-emerald-400",
          bgColor: "bg-emerald-500/10",
          borderColor: "border-emerald-500/20",
          benchmark: "Top 15% DTC Industry Average ($115)",
        };
      case "cvr":
        return {
          icon: <Percent className="h-4 w-4" />,
          label: "Conversion Rate",
          color: "text-cyan-400",
          bgColor: "bg-cyan-500/10",
          borderColor: "border-cyan-500/20",
          benchmark: "SaaS & DTC Top Quartile (> 3.8%)",
        };
      case "revenue":
        return {
          icon: <TrendingUp className="h-4 w-4" />,
          label: "Gross Revenue Lift",
          color: "text-emerald-400",
          bgColor: "bg-emerald-500/10",
          borderColor: "border-emerald-500/20",
          benchmark: "+14.8% Incremental Lift vs Control",
        };
      case "speed":
        return {
          icon: <Gauge className="h-4 w-4" />,
          label: "Core Web Vitals LCP",
          color: "text-amber-400",
          bgColor: "bg-amber-500/10",
          borderColor: "border-amber-500/20",
          benchmark: "Sub-1.2s Fast Storefront Baseline",
        };
      default:
        return {
          icon: <Activity className="h-4 w-4" />,
          label: "Metric",
          color: "text-zinc-400",
          bgColor: "bg-zinc-800",
          borderColor: "border-white/10",
          benchmark: "Target Baseline",
        };
    }
  };

  const config = getMetricConfig();

  // SVG Sparkline calculation
  const data = sparklineData && sparklineData.length > 0 ? sparklineData : [10, 20, 15, 30, 25, 40];
  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;

  const svgWidth = 240;
  const svgHeight = 60;
  const paddingX = 4;
  const paddingY = 8;
  const usableWidth = svgWidth - paddingX * 2;
  const usableHeight = svgHeight - paddingY * 2;

  const points = data.map((val, idx) => {
    const x = paddingX + (idx / (data.length - 1)) * usableWidth;
    const y = svgHeight - paddingY - ((val - minVal) / range) * usableHeight;
    return { x, y, val };
  });

  const pathD = points.reduce((acc, pt, idx) => {
    return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
  }, "");

  const areaD = `${pathD} L ${points[points.length - 1].x} ${svgHeight} L ${points[0].x} ${svgHeight} Z`;

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-[#16181d] text-zinc-100 p-5 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-emerald-500/30 ${className}`}
      data-agent-target="analytics-metric-card-widget"
    >
      {/* Top Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div
            className={`flex h-8 w-8 items-center justify-center rounded-lg border ${config.bgColor} ${config.borderColor} ${config.color}`}
          >
            {config.icon}
          </div>
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-400">
              {config.label}
            </span>
            <h4 className="text-xs font-semibold text-zinc-200 line-clamp-1">{title}</h4>
          </div>
        </div>

        <div className="flex items-center gap-1.5 rounded-full border border-white/5 bg-zinc-900/80 px-2.5 py-1 text-[11px] text-zinc-400">
          <Calendar className="h-3 w-3 text-zinc-500" />
          <span>{timeframe}</span>
        </div>
      </div>

      {/* Main Metric Value & Change Delta */}
      <div className="flex items-baseline justify-between mb-3">
        <div className="text-2xl font-black tracking-tight text-zinc-100 font-mono">
          {value}
        </div>
        <div
          className={`flex items-center gap-0.5 rounded-md px-2 py-0.5 text-xs font-bold ${
            isPositive
              ? "bg-emerald-500/15 border border-emerald-500/30 text-emerald-400"
              : "bg-rose-500/15 border border-rose-500/30 text-rose-400"
          }`}
        >
          {isPositive ? (
            <ArrowUpRight className="h-3.5 w-3.5" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5" />
          )}
          <span>
            {isPositive ? "+" : ""}
            {changePercent.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Live SVG Sparkline Chart */}
      <div className="relative rounded-xl border border-white/5 bg-[#111317] p-2.5 mb-3 overflow-hidden">
        <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono mb-1 px-1">
          <span>Trend Horizon</span>
          <span>
            {hoveredIndex !== null
              ? `Point #${hoveredIndex + 1}: ${data[hoveredIndex]}`
              : `Latest: ${data[data.length - 1]}`}
          </span>
        </div>

        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-14 overflow-visible"
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <defs>
            <linearGradient id={`gradient-${metricType}`} x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="0%"
                stopColor={isPositive ? "#10b981" : "#ef4444"}
                stopOpacity="0.4"
              />
              <stop
                offset="100%"
                stopColor={isPositive ? "#10b981" : "#ef4444"}
                stopOpacity="0.0"
              />
            </linearGradient>
          </defs>

          {/* Area Fill */}
          <path d={areaD} fill={`url(#gradient-${metricType})`} />

          {/* Stroke Line */}
          <path
            d={pathD}
            fill="none"
            stroke={isPositive ? "#10b981" : "#ef4444"}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Points & Hover Interactivity */}
          {points.map((pt, idx) => (
            <g key={idx}>
              <circle
                cx={pt.x}
                cy={pt.y}
                r={hoveredIndex === idx ? 4.5 : 2}
                fill={hoveredIndex === idx ? "#ffffff" : isPositive ? "#10b981" : "#ef4444"}
                stroke="#111317"
                strokeWidth={hoveredIndex === idx ? 2 : 1}
                className="cursor-pointer transition-all duration-150"
                onMouseEnter={() => setHoveredIndex(idx)}
              />
            </g>
          ))}
        </svg>
      </div>

      {/* Benchmark & Action Footer */}
      <div className="flex items-center justify-between pt-1 border-t border-white/5 text-[11px] text-zinc-400">
        <div className="flex items-center gap-1.5 text-zinc-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span className="line-clamp-1">{config.benchmark}</span>
        </div>

        {onDrillDown && (
          <button
            type="button"
            onClick={onDrillDown}
            className="flex items-center gap-1 font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            <span>Deep Dive</span>
            <ChevronRight className="h-3 w-3" />
          </button>
        )}
      </div>
    </div>
  );
};
