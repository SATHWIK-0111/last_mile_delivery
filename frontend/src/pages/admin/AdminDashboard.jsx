import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminNavbar from "../../components/AdminNavbar";
import AdminSidebar from "../../components/AdminSidebar";
import {
  getAdminOrders,
  getAdminAgents,
  assignAgent,
  autoAssignAgent,
} from "../../api/adminApi";


function AdminDashboard() {

  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [agents, setAgents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedOrder, setSelectedOrder] =
    useState(null);

  const [selectedAgent, setSelectedAgent] =
    useState("");

  const [assigning, setAssigning] =
    useState(false);


  // ==========================================
  // LOAD DATA
  // ==========================================

  const loadDashboard = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        ordersData,
        agentsData,
      ] = await Promise.all([
        getAdminOrders(),
        getAdminAgents(),
      ]);

      setOrders(ordersData);
      setAgents(agentsData);

    } catch (error) {

      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Failed to load admin dashboard"
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    loadDashboard();
  }, []);


  // ==========================================
  // STATISTICS
  // ==========================================

  const statistics = useMemo(() => {

    return {
      total: orders.length,

      created: orders.filter(
        order =>
          order.current_status === "CREATED"
      ).length,

      assigned: orders.filter(
        order =>
          order.current_status === "ASSIGNED"
      ).length,

      inTransit: orders.filter(
        order =>
          order.current_status === "IN_TRANSIT"
      ).length,

      outForDelivery: orders.filter(
        order =>
          order.current_status ===
          "OUT_FOR_DELIVERY"
      ).length,

      delivered: orders.filter(
        order =>
          order.current_status === "DELIVERED"
      ).length,

      failed: orders.filter(
        order =>
          order.current_status === "FAILED"
      ).length,
    };

  }, [orders]);


  // ==========================================
  // MANUAL ASSIGN
  // ==========================================

  const handleAssign = async () => {

    if (!selectedOrder || !selectedAgent) {
      return;
    }

    try {

      setAssigning(true);

      await assignAgent(
        selectedOrder.id,
        Number(selectedAgent)
      );

      setSelectedOrder(null);
      setSelectedAgent("");

      await loadDashboard();

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Failed to assign agent"
      );

    } finally {

      setAssigning(false);

    }
  };


  // ==========================================
  // AUTO ASSIGN
  // ==========================================

  const handleAutoAssign = async (orderId) => {

    try {

      setAssigning(true);

      await autoAssignAgent(orderId);

      await loadDashboard();

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Failed to automatically assign agent"
      );

    } finally {

      setAssigning(false);

    }
  };


  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = () => {

    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/");

  };


  if (loading) {

    return (
  <div className="admin-layout">

    <AdminNavbar />

    <AdminSidebar />

    <main className="admin-main">

      <div className="admin-content">
        <p>Loading admin dashboard...</p>
      </div>

    </main>

  </div>
);

  }


  return (

    <div className="admin-layout">

      <AdminNavbar />

      <AdminSidebar />

      <main className="admin-main">

        <div className="admin-content">

          {/* HEADER */}

          <div className="admin-page-header">

            <div>

              <h1>
                Admin Dashboard
              </h1>

              <p>
                Manage orders, agents and delivery assignments
              </p>

            </div>

          </div>


          {/* ERROR */}

          {error && (
            <div className="error">
              {error}
            </div>
          )}


          {/* STATISTICS */}

          <section className="admin-stats">

            <div className="admin-stat-card">
              <span>Total Orders</span>
              <strong>{statistics.total}</strong>
            </div>

            <div className="admin-stat-card">
              <span>Created</span>
              <strong>{statistics.created}</strong>
            </div>

            <div className="admin-stat-card">
              <span>Assigned</span>
              <strong>{statistics.assigned}</strong>
            </div>

            <div className="admin-stat-card">
              <span>In Transit</span>
              <strong>{statistics.inTransit}</strong>
            </div>

            <div className="admin-stat-card">
              <span>Out for Delivery</span>
              <strong>
                {statistics.outForDelivery}
              </strong>
            </div>

            <div className="admin-stat-card">
              <span>Delivered</span>
              <strong>{statistics.delivered}</strong>
            </div>

            <div className="admin-stat-card">
              <span>Failed</span>
              <strong>{statistics.failed}</strong>
            </div>

          </section>


          {/* ORDERS */}

          <section className="admin-section">

            <div className="admin-section-header">

              <div>
                <h2>All Orders</h2>

                <p>
                  Manage delivery assignments
                </p>
              </div>

            </div>


            {orders.length === 0 ? (

              <div className="empty-state">
                No orders found.
              </div>

            ) : (

              <div className="admin-orders">

                {orders.map(order => (

                  <div
                    className="admin-order-card"
                    key={order.id}
                  >

                    <div className="admin-order-main">

                      <div>

                        <span className="order-label">
                          ORDER
                        </span>

                        <h3>
                          #{order.id}
                        </h3>

                      </div>

                      <span
                        className={`order-status status-${order.current_status
                          ?.toLowerCase()
                          .replaceAll("_", "-")}`}
                      >
                        {order.current_status}
                      </span>

                    </div>


                    <div className="admin-order-details">

                      <p>
                        <strong>
                          Pickup:
                        </strong>{" "}
                        {order.pickup_address}
                      </p>

                      <p>
                        <strong>
                          Drop:
                        </strong>{" "}
                        {order.drop_address}
                      </p>

                      <p>
                        <strong>
                          Agent:
                        </strong>{" "}
                        {order.agent_id
                          ? `Agent #${order.agent_id}`
                          : "Not assigned"}
                      </p>

                    </div>


                    <div className="admin-order-actions">

                      <button
                        onClick={() =>
                          navigate(
                            `/admin/orders/${order.id}/tracking`
                          )
                        }
                      >
                        Tracking
                      </button>


                      {order.current_status ===
                        "CREATED" && (

                        <>
                          <button
                            onClick={() =>
                              setSelectedOrder(order)
                            }
                          >
                            Assign Agent
                          </button>

                          <button
                            onClick={() =>
                              handleAutoAssign(
                                order.id
                              )
                            }
                            disabled={assigning}
                          >
                            Auto Assign
                          </button>
                        </>

                      )}

                    </div>

                  </div>

                ))}

              </div>

            )}

          </section>


          {/* AGENTS */}

          <section className="admin-section">

            <div className="admin-section-header">

              <div>
                <h2>Agents</h2>

                <p>
                  Current agent availability
                </p>
              </div>

            </div>


            <div className="admin-agents">

              {agents.map(agent => (

                <div
                  className="admin-agent-card"
                  key={agent.id}
                >

                  <div>

                    <h3>
                      Agent #{agent.id}
                    </h3>

                    <p>
                      Zone:{" "}
                      {agent.zone_id ?? "Not assigned"}
                    </p>

                  </div>

                  <span
                    className={`availability-status availability-${agent.availability_status
                      ?.toLowerCase()}`}
                  >
                    {agent.availability_status}
                  </span>

                </div>

              ))}

            </div>

          </section>


          {/* ASSIGN MODAL */}

          {selectedOrder && (

            <div className="modal-overlay">

              <div className="modal">

                <h2>
                  Assign Agent
                </h2>

                <p>
                  Order #{selectedOrder.id}
                </p>


                <select
                  value={selectedAgent}
                  onChange={(event) =>
                    setSelectedAgent(
                      event.target.value
                    )
                  }
                >

                  <option value="">
                    Select an agent
                  </option>

                  {agents
                    .filter(
                      agent =>
                        agent.availability_status ===
                        "AVAILABLE"
                    )
                    .map(agent => (

                      <option
                        key={agent.id}
                        value={agent.id}
                      >
                        Agent #{agent.id}
                        {" — "}
                        Zone {agent.zone_id}
                      </option>

                    ))}

                </select>


                <div className="modal-actions">

                  <button
                    onClick={() => {
                      setSelectedOrder(null);
                      setSelectedAgent("");
                    }}
                  >
                    Cancel
                  </button>

                  <button
                    onClick={handleAssign}
                    disabled={
                      !selectedAgent ||
                      assigning
                    }
                  >
                    {assigning
                      ? "Assigning..."
                      : "Assign Agent"}
                  </button>

                </div>

              </div>

            </div>

          )}

        </div>

      </main>

    </div>

  );
}

export default AdminDashboard;