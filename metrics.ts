import axios from "axios";

const API_BASE = "http://localhost:5050";

export interface Metrics {
  registered_nodes: number;
  pending_tasks: number;
  completed_tasks: number;
  average_latency: number;
  model_usage: Record<string, number>;
  system_uptime: string;
}

export async function fetchSystemMetrics(): Promise<Metrics> {
  try {
    const statusRes = await axios.get(`${API_BASE}/status`);
    const tasksRes = await axios.get(`${API_BASE}/analytics/tasks`);
    const usageRes = await axios.get(`${API_BASE}/analytics/models`);

    const uptime = Math.floor(Date.now() / 1000) - tasksRes.data.boot_time;

    return {
      registered_nodes: statusRes.data.registered_nodes,
      pending_tasks: statusRes.data.pending_tasks,
      completed_tasks: statusRes.data.completed_tasks,
      average_latency: tasksRes.data.average_latency,
      model_usage: usageRes.data.model_usage,
      system_uptime: `${Math.floor(uptime / 60)} minutes`
    };
  } catch (err) {
    console.error("Failed to fetch metrics:", err);
    return {
      registered_nodes: 0,
      pending_tasks: 0,
      completed_tasks: 0,
      average_latency: 0,
      model_usage: {},
      system_uptime: "unknown"
    };
  }
}

export async function fetchNodeHealth(): Promise<Record<string, any>> {
  try {
    const response = await axios.get(`${API_BASE}/analytics/nodes`);
    return response.data.nodes;
  } catch (err) {
    console.error("Failed to fetch node health:", err);
    return {};
  }
}

export async function fetchRecentActivity(): Promise<
  { task_id: string; model_id: string; timestamp: number; latency: number }[]
> {
  try {
    const res = await axios.get(`${API_BASE}/analytics/recent`);
    return res.data.recent_tasks;
  } catch (err) {
    console.error("Failed to fetch recent task activity:", err);
    return [];
  }
}
