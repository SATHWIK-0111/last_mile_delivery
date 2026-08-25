import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getAdminOrders,
  getAdminAgents,
  assignAgent,
  autoAssignAgent
} from "../../api/adminApi";
import AdminLayout from "../../components/AdminLayout";

function Orders() {

  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [agents, setAgents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [assigningOrder, setAssigningOrder] =
    useState(null);

  const [selectedAgent, setSelectedAgent] =
    useState("");

  const [processing, setProcessing] =
    useState(false);

  // =====================================
  // LOAD DATA
  // =====================================

  const loadData = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        ordersData,
        agentsData
      ] = await Promise.all([
        getAdminOrders(),
        getAdminAgents()
      ]);

      setOrders(ordersData);
      setAgents(agentsData);

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load admin orders"
      );

    } finally {

      setLoading(false);

    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // =====================================
  // AUTO ASSIGN
  // =====================================

  const handleAutoAssign = async (orderId) => {

    try {

      setProcessing(true);

      await autoAssignAgent(orderId);

      await loadData();

    } catch (err) {

      alert(
        err.response?.data?.detail ||
        "Unable to auto assign order"
      );

    } finally {

      setProcessing(false);
    }
  };

  // =====================================
  // MANUAL ASSIGN
  // =====================================

  const handleAssign = async (orderId) => {

    if (!selectedAgent) {

      alert("Please select an agent");

      return;
    }

    try {

      setProcessing(true);

      await assignAgent(
        orderId,
        Number(selectedAgent)
      );

      setAssigningOrder(null);
      setSelectedAgent("");

      await loadData();

    } catch (err) {

      alert(
        err.response?.data?.detail ||
        "Unable to assign order"
      );

    } finally {

      setProcessing(false);
    }
  };

  // =====================================
  // LOADING
  // =====================================

  if (loading) {

    return (
      <AdminLayout>
        <div className="admin-page">

          <div className="admin-content">

            <p>Loading orders...</p>

          </div>

        </div>
      </AdminLayout>
    );
  }

  // =====================================
  // ERROR
  // =====================================

  if (error) {

    return (
      <AdminLayout>
        <div className="admin-page">

          <div className="admin-content">

            <div className="admin-error">
              {error}
            </div>

            <button
              onClick={loadData}
              className="admin-primary-button"
            >
              Retry
            </button>

          </div>

        </div>
      </AdminLayout>
    );
  }

  // =====================================
  // RENDER
  // =====================================

  return (
    <AdminLayout>

      <div className="admin-page">

        <div className="admin-content">

          {/* HEADER */}

          <div className="admin-page-header">

            <div>

              <h1>Orders</h1>

              <p>
                Manage all delivery orders and assignments
              </p>

            </div>

            <button
              className="admin-primary-button"
              onClick={loadData}
            >
              Refresh
            </button>

          </div>


          {/* ORDERS */}

          <div className="admin-section">

            <div className="admin-section-header">

              <div>

                <h2>
                  All Orders
                </h2>

                <p>
                  {orders.length} orders
                </p>

              </div>

            </div>


            {orders.length === 0 ? (

              <div className="admin-empty">
                No orders found.
              </div>

            ) : (

              <div className="admin-orders-list">

                {orders.map((order) => (

                  <div
                    className="admin-order-card"
                    key={order.id}
                  >

                    {/* TOP */}

                    <div className="admin-order-top">

                      <div>

                        <span className="admin-order-label">
                          ORDER
                        </span>

                        <h3>
                          #{order.id}
                        </h3>

                      </div>

                      <span
                        className={`status-badge status-${String(
                          order.current_status
                        ).toLowerCase()}`}
                      >
                        {order.current_status}
                      </span>

                    </div>


                    {/* DETAILS */}

                    <div className="admin-order-details">

                      <div>

                        <strong>
                          Pickup
                        </strong>

                        <p>
                          {order.pickup_address}
                        </p>

                      </div>


                      <div>

                        <strong>
                          Drop
                        </strong>

                        <p>
                          {order.drop_address}
                        </p>

                      </div>


                      <div>

                        <strong>
                          Agent
                        </strong>

                        <p>
                          {order.agent_id
                            ? `Agent #${order.agent_id}`
                            : "Not assigned"}
                        </p>

                      </div>

                    </div>


                    {/* ACTIONS */}

                    <div className="admin-order-actions">

                      <button
                        className="admin-secondary-button"
                        onClick={() =>
                          navigate(
                            `/admin/orders/${order.id}/tracking`
                          )
                        }
                      >
                        Tracking
                      </button>


                      {/* ASSIGNING */}

                      {assigningOrder === order.id ? (

                        <div className="assign-box">

                          <select
                            value={selectedAgent}
                            onChange={(e) =>
                              setSelectedAgent(
                                e.target.value
                              )
                            }
                          >

                            <option value="">
                              Select Agent
                            </option>

                            {agents.map((agent) => (

                              <option
                                key={agent.id}
                                value={agent.id}
                              >
                                Agent #{agent.id}
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
                            onClick={() => {

                              setAssigningOrder(null);
                              setSelectedAgent("");

                            }}
                          >
                            Cancel
                          </button>

                        </div>

                      ) : (

                        <>
                          {/* Only CREATED orders can normally
                              be assigned */}

                          {order.current_status ===
                            "CREATED" && (

                            <>

                              <button
                                className="admin-secondary-button"
                                onClick={() => {

                                  setAssigningOrder(
                                    order.id
                                  );

                                  setSelectedAgent("");

                                }}
                              >
                                Assign Agent
                              </button>


                              <button
                                className="admin-primary-button"
                                disabled={processing}
                                onClick={() =>
                                  handleAutoAssign(
                                    order.id
                                  )
                                }
                              >
                                Auto Assign
                              </button>

                            </>

                          )}

                        </>

                      )}

                    </div>

                  </div>

                ))}

              </div>

            )}

          </div>

        </div>

      </div>

    </AdminLayout>
  );
}

export default Orders;