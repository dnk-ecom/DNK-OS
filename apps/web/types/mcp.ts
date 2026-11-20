// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/types/mcp.ts"
// purpose: "Type definitions for MCP (Model Context Protocol) servers and multi-agent swarm node runtime."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym & Gerych"
// --- END DNK-MRH-HEADER ---

export type MCPConnectionType = 'stdio' | 'sse';

export interface StdioServerConfig {
  transport: 'stdio';
  command: string;
  args: string[];
  env?: Record<string, string>;
}

export interface SSEServerConfig {
  transport: 'sse';
  url: string;
  headers?: Record<string, string>;
}

export type MCPServerConfig = StdioServerConfig | SSEServerConfig;

export const MCP_STORAGE_KEY = 'dnk_os_mcp_servers_config';

export type AgentRunStatus = 'idle' | 'running' | 'completed' | 'failed' | 'paused';

export interface AgentExecutionStep {
  id: string;
  message: string;
  done: boolean;
  timestamp: number;
  nodeName?: string;
  level?: 'info' | 'warn' | 'error' | 'success';
}

export interface MultiAgentSwarmNodeData extends Record<string, any> {
  id: string;
  agentRole:
    | 'gerych_prime'
    | 'gerych_builder'
    | 'gerych_researcher'
    | 'gerych_auditor'
    | 'dnk_dev_fullstack'
    | 'dnk_shopify'
    | 'dnk_video_ai_creator'
    | 'dnk_scones_memory'
    | 'mcp_agent'
    | string;
  agentName: string;
  status: AgentRunStatus;
  activeNodeName?: string;
  taskGoal?: string;
  logs: AgentExecutionStep[];
  response?: string;
  mcpServers?: Record<string, MCPServerConfig>;
  metrics?: {
    tokensUsed?: number;
    durationMs?: number;
    toolCallsCount?: number;
  };
  onConfigureMCP?: (agentId: string) => void;
  onDispatch?: (agentId: string) => void;
  onPause?: (agentId: string) => void;
  community?: string;
  highlighted?: boolean;
  dimmed?: boolean;
}
