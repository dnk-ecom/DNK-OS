// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/modals/MCPConfigModal.tsx"
// purpose: "Assimilated MCP Server Configuration Modal with local persistence for Stdio and SSE transports."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym & Gerych"
// --- END DNK-MRH-HEADER ---

import React, { useState, useEffect } from 'react';
import { X, Plus, Server, Globe, Trash2, Cpu } from 'lucide-react';
import {
  MCPServerConfig,
  MCPConnectionType,
  MCP_STORAGE_KEY,
} from '@/types/mcp';

interface MCPConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: (configs: Record<string, MCPServerConfig>) => void;
}

export function MCPConfigModal({ isOpen, onClose, onSave }: MCPConfigModalProps) {
  const [configs, setConfigs] = useState<Record<string, MCPServerConfig>>({});
  const [serverName, setServerName] = useState('');
  const [connectionType, setConnectionType] = useState<MCPConnectionType>('stdio');
  const [command, setCommand] = useState('');
  const [args, setArgs] = useState('');
  const [url, setUrl] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Load from local storage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem(MCP_STORAGE_KEY);
        if (stored) {
          setConfigs(JSON.parse(stored));
        }
      } catch (err) {
        console.error('Failed to parse MCP configs from localStorage:', err);
      }
    }
  }, [isOpen]);

  const persistConfigs = (updated: Record<string, MCPServerConfig>) => {
    setConfigs(updated);
    if (typeof window !== 'undefined') {
      localStorage.setItem(MCP_STORAGE_KEY, JSON.stringify(updated));
    }
    onSave?.(updated);
  };

  const addConfig = () => {
    if (!serverName.trim()) return;

    const newConfig: MCPServerConfig =
      connectionType === 'stdio'
        ? {
            transport: 'stdio',
            command: command.trim(),
            args: args.split(' ').filter((a) => a.trim() !== ''),
          }
        : {
            transport: 'sse',
            url: url.trim(),
          };

    const updated = {
      ...configs,
      [serverName.trim()]: newConfig,
    };

    persistConfigs(updated);

    // Reset form
    setServerName('');
    setCommand('');
    setArgs('');
    setUrl('');
    setShowAddForm(false);
  };

  const removeConfig = (name: string) => {
    const updated = { ...configs };
    delete updated[name];
    persistConfigs(updated);
  };

  if (!isOpen) return null;

  const totalServers = Object.keys(configs).length;
  const stdioServers = Object.values(configs).filter((c) => c.transport === 'stdio').length;
  const sseServers = Object.values(configs).filter((c) => c.transport === 'sse').length;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
      <div className="bg-[#162c2f] border border-[#224447] text-[#d4d8db] rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#112224] border-b border-[#224447]">
          <div className="flex items-center space-x-3">
            <div className="p-1.5 rounded-lg bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">MCP Server Configuration</h2>
              <p className="text-xs text-slate-400">
                Model Context Protocol (Stdio & SSE) transports for Swarm Workers
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#162c2f] text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-[#112224] border border-[#224447]">
              <span className="text-xs text-slate-400">Total MCP Servers</span>
              <div className="text-2xl font-bold text-[#35d5d5] mt-1">{totalServers}</div>
            </div>
            <div className="p-4 rounded-lg bg-[#112224] border border-[#224447]">
              <span className="text-xs text-slate-400">Stdio Transports</span>
              <div className="text-2xl font-bold text-emerald-400 mt-1">{stdioServers}</div>
            </div>
            <div className="p-4 rounded-lg bg-[#112224] border border-[#224447]">
              <span className="text-xs text-slate-400">SSE Transports</span>
              <div className="text-2xl font-bold text-sky-400 mt-1">{sseServers}</div>
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">Configured Endpoints</h3>
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#35d5d5] hover:bg-[#35d5d5]/80 text-[#112224] text-xs font-semibold rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add MCP Server</span>
            </button>
          </div>

          {/* Server List */}
          {totalServers === 0 ? (
            <div className="p-8 text-center border border-dashed border-[#224447] rounded-xl text-slate-500 text-sm">
              No MCP servers registered yet. Click &quot;Add MCP Server&quot; to hook tools into the swarm.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(configs).map(([name, conf]) => (
                <div
                  key={name}
                  className="p-4 rounded-lg bg-[#112224] border border-[#224447] flex flex-col justify-between space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-semibold text-slate-200">{name}</h4>
                      <span className="inline-flex items-center px-2 py-0.5 mt-1 rounded text-[10px] font-mono bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
                        {conf.transport === 'stdio' ? (
                          <Server className="w-3 h-3 mr-1 text-emerald-400" />
                        ) : (
                          <Globe className="w-3 h-3 mr-1 text-sky-400" />
                        )}
                        {conf.transport.toUpperCase()}
                      </span>
                    </div>
                    <button
                      onClick={() => removeConfig(name)}
                      className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                      title="Remove Server"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="text-xs text-slate-400 font-mono bg-[#162c2f]/60 p-2 rounded border border-[#224447]/60 truncate">
                    {conf.transport === 'stdio' ? (
                      <>
                        <div>cmd: {conf.command}</div>
                        <div className="truncate">args: {conf.args.join(' ')}</div>
                      </>
                    ) : (
                      <div>url: {conf.url}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Add Form Drawer */}
          {showAddForm && (
            <div className="p-4 rounded-xl bg-[#112224] border border-[#35d5d5]/40 space-y-4 animate-in fade-in duration-150">
              <div className="flex items-center justify-between border-b border-[#224447] pb-2">
                <span className="text-xs font-bold text-[#35d5d5] uppercase tracking-wider">
                  New MCP Server Registration
                </span>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Server Identifier
                  </label>
                  <input
                    type="text"
                    value={serverName}
                    onChange={(e) => setServerName(e.target.value)}
                    placeholder="e.g. github_mcp, filesystem_tools, postgres_db"
                    className="w-full px-3 py-2 bg-[#162c2f] border border-[#224447] rounded-lg text-xs text-slate-200 focus:outline-none focus:border-[#35d5d5]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Transport Protocol
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setConnectionType('stdio')}
                      className={`px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-center space-x-1.5 border transition-colors ${
                        connectionType === 'stdio'
                          ? 'bg-[#35d5d5]/20 border-[#35d5d5] text-[#35d5d5]'
                          : 'bg-[#162c2f] border-[#224447] text-slate-400'
                      }`}
                    >
                      <Server className="w-3.5 h-3.5" />
                      <span>Standard IO (stdio)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setConnectionType('sse')}
                      className={`px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-center space-x-1.5 border transition-colors ${
                        connectionType === 'sse'
                          ? 'bg-[#35d5d5]/20 border-[#35d5d5] text-[#35d5d5]'
                          : 'bg-[#162c2f] border-[#224447] text-slate-400'
                      }`}
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>Server-Sent Events (SSE)</span>
                    </button>
                  </div>
                </div>

                {connectionType === 'stdio' ? (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Executable Command
                      </label>
                      <input
                        type="text"
                        value={command}
                        onChange={(e) => setCommand(e.target.value)}
                        placeholder="e.g. npx, uvx, python3"
                        className="w-full px-3 py-2 bg-[#162c2f] border border-[#224447] rounded-lg text-xs text-slate-200 focus:outline-none focus:border-[#35d5d5]"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Arguments (space-separated)
                      </label>
                      <input
                        type="text"
                        value={args}
                        onChange={(e) => setArgs(e.target.value)}
                        placeholder="e.g. -y @modelcontextprotocol/server-github"
                        className="w-full px-3 py-2 bg-[#162c2f] border border-[#224447] rounded-lg text-xs text-slate-200 focus:outline-none focus:border-[#35d5d5]"
                      />
                    </div>
                  </>
                ) : (
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      SSE Endpoint URL
                    </label>
                    <input
                      type="text"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="e.g. http://localhost:8000/sse"
                      className="w-full px-3 py-2 bg-[#162c2f] border border-[#224447] rounded-lg text-xs text-slate-200 focus:outline-none focus:border-[#35d5d5]"
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="px-3 py-1.5 text-xs text-slate-400 hover:text-white border border-[#224447] rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={addConfig}
                    className="px-4 py-1.5 bg-[#35d5d5] hover:bg-[#35d5d5]/80 text-[#112224] text-xs font-semibold rounded-lg transition-colors"
                  >
                    Save MCP Server
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
