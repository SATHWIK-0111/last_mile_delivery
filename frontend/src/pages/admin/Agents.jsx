import { useEffect, useState } from "react";
import AdminLayout from "../../components/AdminLayout";
import {
  getAdminAgents,
  updateAgentAvailability
} from "../../api/adminApi";

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getAdminAgents();
      setAgents(data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
        "Failed to load agents"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const changeAvailability = async (
    agentId,
    availability_status
  ) => {
    try {
      await updateAgentAvailability(
        agentId,
        availability_status
      );

      await loadAgents();
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to update agent"
      );
    }
  };

  return (
    <AdminLayout>

      <div className="admin-page-header">

        <div>
          <h1>Agents</h1>

          <p>
            Manage delivery agents and their availability
          </p>
        </div>

        <button
          className="admin-secondary-button"
          onClick={loadAgents}
        >
          Refresh
        </button>

      </div>


      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      <div className="admin-section">

        <div className="admin-section-header">

          <div>
            <h2>All Agents</h2>

            <p>
              {agents.length} agents
            </p>
          </div>

        </div>


        {loading ? (

          <div className="admin-empty">
            Loading agents...
          </div>

        ) : agents.length === 0 ? (

          <div className="admin-empty">
            No agents found.
          </div>

        ) : (

          <div className="admin-agents-list">

            {agents.map((agent) => (

              <div
                className="admin-agent-card"
                key={agent.id}
              >

                <div className="agent-info">

                  <div className="agent-avatar">
                    {(agent.name || "A")
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div>
                    <h3>
                      {agent.name}
                    </h3>

                    <p>
                      {agent.email}
                    </p>

                    <small>
                      Agent ID: {agent.id}
                    </small>
                  </div>

                </div>


                <div className="agent-zone">

                  <span>
                    Zone
                  </span>

                  <strong>
                    {agent.zone_id ?? "Not assigned"}
                  </strong>

                </div>


                <div className="agent-availability">

                  <span
                    className={`availability-badge ${String(
                      agent.availability_status || ""
                    ).toLowerCase()}`}
                  >
                    {agent.availability_status}
                  </span>

                  <select
                    value={
                      agent.availability_status
                    }
                    onChange={(e) =>
                      changeAvailability(
                        agent.id,
                        e.target.value
                      )
                    }
                  >
                    <option value="AVAILABLE">
                      Available
                    </option>

                    <option value="BUSY">
                      Busy
                    </option>

                    <option value="OFFLINE">
                      Offline
                    </option>
                  </select>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </AdminLayout>
  );
}

export default Agents;