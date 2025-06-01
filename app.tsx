import React, { useState, useEffect } from "react";
import axios from "axios";
import "./styles.css";

interface Result {
  input: string;
  output: string;
  confidence: number;
  model_id: string;
  timestamp: number;
}

interface DACert {
  task_id: string;
  output_hash: string;
  signers: string[];
  signatures: string[];
  quorum: number;
}

interface Response {
  task_id: string;
  session_id: string;
  result: Result;
  dacert?: DACert;
}

const API_BASE = "http://localhost:8080";

export default function App() {
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState(() => {
    const saved = localStorage.getItem("session_id");
    if (saved) return saved;
    const generated = "sess-" + Date.now().toString();
    localStorage.setItem("session_id", generated);
    return generated;
  });
  const [results, setResults] = useState<Response[]>([]);
  const [loading, setLoading] = useState(false);

  const submitQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);

    try {
      const payload = {
        query,
        session_id: sessionId,
        model_id: "parallax-llm-v1",
        return_dacert: true
      };

      const response = await axios.post(`${API_BASE}/query`, payload);
      setResults((prev) => [response.data, ...prev]);
      setQuery("");
    } catch (error) {
      console.error("Error submitting query:", error);
    }

    setLoading(false);
  };

  useEffect(() => {
    const fetchHistory = async () => {
      const res = await axios.get(`${API_BASE}/history/${sessionId}`);
      if (res.data && Array.isArray(res.data.history)) {
        setResults(res.data.history.reverse());
      }
    };
    fetchHistory();
  }, [sessionId]);

  return (
    <div className="container">
      <h1>PARALLAX AI Dashboard</h1>

      <div className="query-section">
        <input
          type="text"
          value={query}
          placeholder="Ask something related to crypto, AI, or trading..."
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submitQuery();
          }}
        />
        <button disabled={loading} onClick={submitQuery}>
          {loading ? "Running..." : "Submit"}
        </button>
      </div>

      <div className="result-section">
        {results.length === 0 && <p>No queries yet. Start with something simple.</p>}

        {results.map((res, index) => (
          <div key={res.task_id + index} className="result-card">
            <p><strong>Input:</strong> {res.result.input}</p>
            <p><strong>Sentiment:</strong> {res.result.output}</p>
            <p><strong>Confidence:</strong> {res.result.confidence}</p>
            <p><strong>Model:</strong> {res.result.model_id}</p>
            <p><strong>Time:</strong> {new Date(res.result.timestamp * 1000).toLocaleString()}</p>

            {res.dacert && (
              <div className="dacert">
                <p><strong>DACert Task ID:</strong> {res.dacert.task_id}</p>
                <p><strong>Output Hash:</strong> {res.dacert.output_hash}</p>
                <p><strong>Quorum:</strong> {res.dacert.quorum}</p>
                <p><strong>Signers:</strong> {res.dacert.signers.join(", ")}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
