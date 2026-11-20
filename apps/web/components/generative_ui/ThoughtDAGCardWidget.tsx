// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_generative_ui_ThoughtDAGCardWidget"
// purpose: "Astryx Generative UI: Epistemic ThoughtDAG Node Card (Goal, Hypothesis, Critique 3-Flaws, Decision)"
// author: "DNK-e.com Maksym & Denchik"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// --- END DNK-MRH-HEADER ---

"use client";

import React, { useState } from "react";
import {
  Compass,
  Lightbulb,
  ShieldAlert,
  CheckCircle2,
  Lock,
  GitFork,
  Copy,
  Check,
  Bot,
  AlertTriangle,
  ChevronRight,
  ExternalLink,
  Sparkles,
} from "lucide-react";

export interface ThoughtDAGCardWidgetProps {
  nodeKind: "goal" | "hypothesis" | "critique" | "decision";
  title: string;
  agent: string;
  summary: string;
  flaws?: string[];
  lockedDecRef?: string;
  onBranchFork?: () => void;
  className?: string;
}

export const ThoughtDAGCardWidget: React.FC<ThoughtDAGCardWidgetProps> = ({
  nodeKind,
  title,
  agent,
  summary,
  flaws,
  lockedDecRef,
  onBranchFork,
  className = "",
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isForking, setIsForking] = useState<boolean>(false);

  const handleCopy = () => {
    const text = `[ThoughtDAG Node: ${nodeKind.toUpperCase()}] ${title}\nAgent: ${agent}\nSummary: ${summary}${
      lockedDecRef ? `\nLocked Ref: ${lockedDecRef}` : ""
    }${flaws ? `\nFlaws:\n${flaws.map((f, i) => `  ${i + 1}. ${f}`).join("\n")}` : ""}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFork = () => {
    setIsForking(true);
    if (onBranchFork) {
      onBranchFork();
    }
    setTimeout(() => setIsForking(false), 2000);
  };

  // Node Kind theme configuration
  const getNodeConfig = () => {
    switch (nodeKind) {
      case "goal":
        return {
          label: "Epistemic Goal",
          icon: <Compass className="h-4 w-4" />,
          badgeColor: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
          cardBorder: "border-cyan-500/30",
          dotColor: "bg-cyan-400",
        };
      case "hypothesis":
        return {
          label: "Testing Hypothesis",
          icon: <Lightbulb className="h-4 w-4" />,
          badgeColor: "bg-amber-500/10 text-amber-400 border-amber-500/20",
          cardBorder: "border-amber-500/30",
          dotColor: "bg-amber-400",
        };
      case "critique":
        return {
          label: "Mandatory Critique (3 Flaws)",
          icon: <ShieldAlert className="h-4 w-4" />,
          badgeColor: "bg-rose-500/10 text-rose-400 border-rose-500/20",
          cardBorder: "border-rose-500/30",
          dotColor: "bg-rose-400",
        };
      case "decision":
        return {
          label: "Locked Decision SSOT",
          icon: <Lock className="h-4 w-4" />,
          badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
          cardBorder: "border-emerald-500/40",
          dotColor: "bg-emerald-400",
        };
    }
  };

  const config = getNodeConfig();

  // Agent avatar accent color
  const getAgentColor = () => {
    if (agent.toLowerCase().includes("antigravity")) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    if (agent.toLowerCase().includes("denchik")) return "text-blue-400 bg-blue-500/10 border-blue-500/20";
    if (agent.toLowerCase().includes("gerych")) return "text-purple-400 bg-purple-500/10 border-purple-500/20";
    return "text-zinc-300 bg-zinc-800 border-white/10";
  };

  return (
    <div
      className={`rounded-2xl border ${config.cardBorder} bg-[#16181d] text-zinc-100 p-5 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:shadow-emerald-500/5 ${className}`}
      data-agent-target="thought-dag-card-widget"
    >
      {/* Top Bar: Node Kind Badge, Agent Moniker & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pb-3.5 mb-3.5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span
            className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold border ${config.badgeColor}`}
          >
            {config.icon}
            {config.label}
          </span>

          {lockedDecRef && (
            <span className="flex items-center gap-1 rounded-md bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[11px] font-mono font-bold text-emerald-300">
              <Lock className="h-3 w-3" />
              [🔒 LOCKED: {lockedDecRef}]
            </span>
          )}
        </div>

        {/* Agent attribution badge */}
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1.5 rounded-lg border px-2 py-1 text-[11px] font-mono ${getAgentColor()}`}
          >
            <Bot className="h-3.5 w-3.5" />
            <span>{agent}</span>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="rounded-lg border border-white/10 bg-zinc-900 p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
            title="Copy thought summary"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Title & Summary Body */}
      <div className="space-y-2 mb-4">
        <h3 className="text-sm sm:text-base font-bold text-zinc-100 tracking-tight leading-snug">
          {title}
        </h3>
        <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed bg-[#111317] border border-white/5 rounded-xl p-3.5">
          {summary}
        </p>
      </div>

      {/* 3 Mandatory Flaws Section (ArXiv 2602.23971 Epistemic Dissent) */}
      {(nodeKind === "critique" || (flaws && flaws.length > 0)) && (
        <div className="rounded-xl border border-rose-500/20 bg-rose-950/10 p-3.5 mb-4">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase tracking-wider font-mono">
              <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
              <span>Mandatory 3-Flaws Epistemic Dissent</span>
            </div>
            <span className="text-[10px] font-mono text-zinc-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
              Anti-Sycophancy Gate
            </span>
          </div>

          <div className="space-y-2">
            {flaws && flaws.length > 0 ? (
              flaws.map((flaw, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2.5 rounded-lg border border-white/5 bg-zinc-900/80 p-2.5 text-xs"
                >
                  <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-rose-500/20 font-mono font-bold text-rose-400 text-[10px]">
                    F{idx + 1}
                  </span>
                  <span className="text-zinc-200 leading-snug">{flaw}</span>
                </div>
              ))
            ) : (
              <>
                <div className="flex items-start gap-2.5 rounded-lg border border-white/5 bg-zinc-900/80 p-2.5 text-xs">
                  <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-rose-500/20 font-mono font-bold text-rose-400 text-[10px]">
                    F1
                  </span>
                  <span className="text-zinc-200">
                    Boundary failure under high-concurrency mutation collisions.
                  </span>
                </div>
                <div className="flex items-start gap-2.5 rounded-lg border border-white/5 bg-zinc-900/80 p-2.5 text-xs">
                  <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-rose-500/20 font-mono font-bold text-rose-400 text-[10px]">
                    F2
                  </span>
                  <span className="text-zinc-200">
                    Excessive memory footprint when context exceeds 40k tokens.
                  </span>
                </div>
                <div className="flex items-start gap-2.5 rounded-lg border border-white/5 bg-zinc-900/80 p-2.5 text-xs">
                  <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-rose-500/20 font-mono font-bold text-rose-400 text-[10px]">
                    F3
                  </span>
                  <span className="text-zinc-200">
                    Sycophantic confirmation loop without explicit falsification oracle.
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Footer: Living Canvas Integration & Branch Fork */}
      <div className="flex items-center justify-between pt-2 border-t border-white/5">
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
          <span className={`h-2 w-2 rounded-full ${config.dotColor}`} />
          <span>ThoughtDAG Typed Wire: Node Active</span>
        </div>

        <button
          type="button"
          onClick={handleFork}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
            isForking
              ? "bg-emerald-500 text-zinc-950 font-bold"
              : "border border-white/10 bg-zinc-900 text-zinc-200 hover:border-emerald-500/40 hover:text-emerald-300"
          }`}
        >
          <GitFork className="h-3.5 w-3.5" />
          <span>{isForking ? "Branch Forked!" : "Fork Counter-Branch"}</span>
        </button>
      </div>
    </div>
  );
};
