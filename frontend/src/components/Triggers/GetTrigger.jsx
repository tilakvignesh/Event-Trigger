import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.css";

const TriggersComponent = () => {
  const [triggers, setTriggers] = useState(null);
  const [error, setError] = useState(null);
  const [isCollapsed, setIsCollapsed] = useState(true);

  const fetchTriggers = async () => {
    try {
      setError(null);
      const response = await fetch("http://localhost:8000/triggers/");
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setTriggers(data);
      setIsCollapsed(false); // Expand JSON box when data loads
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container mt-4">
      <h3 className="mb-3">Fetch Active Triggers</h3>
      <div className="d-flex gap-3 align-items-start">
      <button onClick={fetchTriggers} className="btn btn-primary">
        Load Triggers
      </button>

      {error && <div className="mt-3 text-danger">Error: {error}</div>}

      {triggers && (
        <>
          <button
            className="btn btn-secondary"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? "Show JSON" : "Hide JSON"}
          </button>
          <div className={`collapse ${isCollapsed ? "" : "show"}`}>
            <pre className="mt-3 p-3 bg-light border rounded">
              {JSON.stringify(triggers, null, 2)}
            </pre>
          </div>
        </>
      )}
      </div>
    </div>
  );
};

export default TriggersComponent;
