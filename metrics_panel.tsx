import React, { useEffect, useState } from "react";
import { fetchSystemMetrics, fetchNodeHealth } from "../api/metrics";
import "./metrics_panel.css";

interface NodeInfo {
  id: string;
  capabilities: string[];
  last_seen: number;
}

export default function MetricsPanel() {
  const [metrics, setMetrics] = useState({
    registered_nodes: 0,
    pending_tasks: 0,
    completed_tasks: 0,
    average_latency: 0,
    model_usage: {},
    system_uptime: "loading..."
  });

  const [nodes, setNodes] = useState<Record<string, NodeInfo>>({});

  useEffect(() => {
    const refresh = async () => {
      const m = await fetchSystemMetrics();
      const n = await fetchNodeHealth();
      setMetrics(m);
      setNodes(n);
    };

    refresh();
    const interval = setInterval(refresh, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="metrics-panel">
      <h2>System Metrics</h2>

      <div className="metrics-grid">
        <div className="metric">
          <p className="label">Nodes Online</p>
          <p className="value">{metrics.registered_nodes}</p>
        </div>

        <div className="metric">
          <p className="label">Pending Tasks</p>
          <p className="value">{metrics.pending_tasks}</p>
        </div>

        <div className="metric">
          <p className="label">Completed Tasks</p>
          <p className="value">{metrics.completed_tasks}</p>
        </div>

        <div className="metric">
          <p className="label">Avg Latency</p>
          <p className="value">{metrics.average_latency}s</p>
        </div>

        <div className="metric">
          <p className="label">Uptime</p>
          <p className="value">{metrics.system_uptime}</p>
        </div>
      </div>

      <h3>Model Usage</h3>
      <ul className="model-list">
        {Object.entries(metrics.model_usage).map(([model, count]) => (
          <li key={model}>
            <strong>{model}</strong>: {count}
          </li>
        ))}
      </ul>

      <h3>Active Nodes</h3>
      <ul className="node-list">
        {Object.entries(nodes).map(([id, info]) => (
          <li key={id}>
            <span className="node-id">{id}</span>
            <span className="node-meta">{info.capabilities.join(", ")}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
