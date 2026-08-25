import { useEffect, useState } from "react";

import AdminLayout from "../../components/AdminLayout";

import {
  getAdminOrders,
  getAdminAgents,
  assignAgent,
  autoAssignAgent
} from "../../api/adminApi";

function Assignment() {

  const [orders, setOrders] = useState([]);
  const [agents, setAgents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");

  const [selectedAgents, setSelectedAgents] = useState({});


  // =========================================
  // LOAD ORDERS + AGENTS
  // =========================================

  const loadData = async () => {

    try {

      setLoading(true);
      setError("");

      const [ordersData, agentsData] =
        await Promise.all([
          getAdminOrders(),
          getAdminAgents()
        ]);

      setOrders(ordersData);
      setAgents(agentsData);

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load assignment data"
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    loadData();
  }, []);


  // =========================================
  // SELECT AGENT
  // =========================================

  const handleAgentChange = (
    orderId,
    agentId
  ) => {

    setSelectedAgents((previous) => ({
      ...previous,
      [orderId]: agentId
    }));

  };


  // =========================================
  // MANUAL ASSIGN
  // =========================================

  const handleAssign = async (orderId) => {

    const agentId =
      selectedAgents[orderId];

    if (!agentId) {

      alert("Please select an agent");

      return;
    }

    try {

      setProcessing(true);

      await assignAgent(
        orderId,
        Number(agentId)
      );

      await loadData();

      setSelectedAgents(
        (previous) => {

          const updated = {
            ...previous
          };

          delete updated[orderId];

          return updated;
        }
      );

    } catch (err) {

      console.error(err);

      alert(
        err.response?.data?.detail ||
        "Failed to assign order"
      );

    } finally {

      setProcessing(false);

    }

  };


  // =========================================
  // AUTO ASSIGN
  // =========================================

  const handleAutoAssign = async (
    orderId
  ) => {

    try {

      setProcessing(true);

      await autoAssignAgent(orderId);

      await loadData();

    } catch (err) {

      console.error(err);

      alert(
        err.response?.data?.detail ||
        "Automatic assignment failed"
      );

    } finally {

      setProcessing(false);
    }

  };


  // =========================================
  // ONLY UNASSIGNED CREATED ORDERS
  // =========================================

  const pendingOrders = orders.filter(
    (order) =>
      order.current_status === "CREATED" &&
      !order.agent_id
  );


  // =========================================
  // LOADING
  // =========================================

  if (loading) {

    return (
      <AdminLayout>

        <div className="admin-empty">
          Loading assignments...
        </div>

      </AdminLayout>
    );

  }


  return (
    <AdminLayout>

      {/* PAGE HEADER */}

      <div className="admin-page-header">

        <div>

          <h1>
            Assignment
          </h1>

          <p>
            Assign delivery orders to agents
          </p>

        </div>

        <button
          className="admin-secondary-button"
          onClick={loadData}
        >
          Refresh
        </button>

      </div>


      {/* ERROR */}

      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      {/* SUMMARY */}

      <div className="assignment-summary">

        <div className="assignment-stat">

          <span>
            Pending Orders
          </span>

          <strong>
            {pendingOrders.length}
          </strong>

        </div>


        <div className="assignment-stat">

          <span>
            Available Agents
          </span>

          <strong>
            {
              agents.filter(
                (agent) =>
                  agent.availability_status ===
                  "AVAILABLE"
              ).length
            }
          </strong>

        </div>


        <div className="assignment-stat">

          <span>
            Total Agents
          </span>

          <strong>
            {agents.length}
          </strong>

        </div>

      </div>


      {/* ASSIGNMENT CARD */}

      <div className="admin-section">

        <div className="admin-section-header">

          <div>

            <h2>
              Pending Assignments
            </h2>

            <p>
              Orders waiting for an agent
            </p>

          </div>

        </div>


        {pendingOrders.length === 0 ? (

          <div className="admin-empty">

            🎉

            <br />

            No orders are waiting for assignment.

          </div>

        ) : (

          <div className="assignment-list">

            {pendingOrders.map(
              (order) => (

              <div
                className="assignment-card"
                key={order.id}
              >

                {/* ORDER */}

                <div className="assignment-order">

                  <span>
                    ORDER
                  </span>

                  <h3>
                    #{order.id}
                  </h3>

                  <div className="assignment-route">

                    <div>

                      <small>
                        Pickup
                      </small>

                      <p>
                        {order.pickup_address}
                      </p>

                    </div>

                    <div className="route-arrow">
                      →
                    </div>

                    <div>

                      <small>
                        Drop
                      </small>

                      <p>
                        {order.drop_address}
                      </p>

                    </div>

                  </div>

                </div>


                {/* CONTROLS */}

                <div className="assignment-controls">

                  <select
                    value={
                      selectedAgents[order.id] ||
                      ""
                    }
                    onChange={(e) =>
                      handleAgentChange(
                        order.id,
                        e.target.value
                      )
                    }
                  >

                    <option value="">
                      Select Agent
                    </option>

                    {agents.map(
                      (agent) => (

                      <option
                        key={agent.id}
                        value={agent.id}
                        disabled={
                          agent.availability_status !==
                          "AVAILABLE"
                        }
                      >

                        {agent.name ||
                          `Agent #${agent.id}`}

                        {" - "}

                        {agent.availability_status}

                      </option>

                    ))}

                  </select>


                  <button
                    className="admin-primary-button"
                    disabled={processing}
                    onClick={() =>
                      handleAssign(order.id)
                    }
                  >
                    Assign
                  </button>


                  <button
                    className="admin-secondary-button"
                    disabled={processing}
                    onClick={() =>
                      handleAutoAssign(
                        order.id
                      )
                    }
                  >
                    Auto Assign
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </AdminLayout>
  );
}

export default Assignment;