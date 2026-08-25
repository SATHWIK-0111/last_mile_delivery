import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getAgentOrders,
  getAgentProfile,
  updateAvailability,
  updateOrderStatus,
  failOrder,
} from "../../api/agentApi";

import {
  getAgentNotifications,
  markAgentNotificationRead,
} from "../../api/notificationApi";

function AgentDashboard() {
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [availability, setAvailability] = useState("");
  const [agent, setAgent] = useState(null);

  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  const [error, setError] = useState("");

  const [failedOrderId, setFailedOrderId] = useState(null);
  const [failureReason, setFailureReason] = useState("");

  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notificationLoading, setNotificationLoading] = useState(false);

  // ==========================================
  // LOAD ORDERS
  // ==========================================

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getAgentOrders();

      setOrders(data);
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "Failed to load orders"
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // LOAD NOTIFICATIONS
  // ==========================================

  const loadNotifications = async () => {
    try {
      setNotificationLoading(true);

      const data = await getAgentNotifications();

      setNotifications(data);
    } catch (error) {
      console.error("Failed to load notifications:", error);
    } finally {
      setNotificationLoading(false);
    }
  };

  // ==========================================
  // LOAD AGENT PROFILE
  // ==========================================

  const loadAgentProfile = async () => {
    try {
      const data = await getAgentProfile();

      setAgent(data);
      setAvailability(data.availability_status);
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "Failed to load agent profile"
      );
    }
  };

  useEffect(() => {
    loadAgentProfile();
    loadOrders();
    loadNotifications();
  }, []);

  // ==========================================
  // AVAILABILITY
  // ==========================================

  const handleAvailability = async (status) => {
    try {
      setUpdating(true);
      setError("");

      const data = await updateAvailability(status);

      setAvailability(data.availability_status);
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "Failed to update availability"
      );
    } finally {
      setUpdating(false);
    }
  };

  // ==========================================
  // STATUS UPDATE
  // ==========================================

  const handleStatusUpdate = async (orderId, status) => {
    try {
      setUpdating(true);
      setError("");

      await updateOrderStatus(orderId, status);

      await loadOrders();
      await loadAgentProfile();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "Failed to update order status"
      );
    } finally {
      setUpdating(false);
    }
  };

  // ==========================================
  // FAILED DELIVERY
  // ==========================================

  const handleFailedDelivery = async () => {
    if (!failureReason.trim()) {
      setError("Failure reason is required");
      return;
    }

    try {
      setUpdating(true);
      setError("");

      await failOrder(failedOrderId, failureReason);

      setFailedOrderId(null);
      setFailureReason("");

      await loadOrders();
      await loadAgentProfile();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail || "Failed to mark delivery as failed"
      );
    } finally {
      setUpdating(false);
    }
  };

  // ==========================================
  // NOTIFICATIONS
  // ==========================================

  const handleNotificationClick = async (notification) => {
    if (notification.status === "READ") {
      return;
    }

    try {
      await markAgentNotificationRead(notification.id);

      setNotifications((current) =>
        current.map((item) =>
          item.id === notification.id
            ? { ...item, status: "READ" }
            : item
        )
      );
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  // ==========================================
  // STATUS DISPLAY
  // ==========================================

  const getStatusClass = (status) => {
    switch (status) {
      case "ASSIGNED":
        return "status-assigned";
      case "PICKED_UP":
        return "status-picked-up";
      case "IN_TRANSIT":
        return "status-in-transit";
      case "OUT_FOR_DELIVERY":
        return "status-out-for-delivery";
      case "DELIVERED":
        return "status-delivered";
      case "FAILED":
        return "status-failed";
      case "RESCHEDULED":
        return "status-rescheduled";
      default:
        return "";
    }
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/");
  };

  return (
    <div className="agent-dashboard">
      {/* HEADER */}
      <header className="agent-header">
        <div>
          <h1>Agent Dashboard</h1>
          <p>Manage your deliveries</p>

          {agent && (
            <div className="agent-profile">
              Username: <strong>{agent.name}</strong><br />
              Email: <span>{agent.email}</span>
            </div>
          )}
        </div>

        <div className="agent-header-actions">
          {/* NOTIFICATION BELL */}
          <div className="notification-wrapper">
            <button
              className="notification-button"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              🔔
              {notifications.filter(
                (notification) => notification.status === "PENDING"
              ).length > 0 && (
                <span className="notification-badge">
                  {
                    notifications.filter(
                      (notification) => notification.status === "PENDING"
                    ).length
                  }
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="notification-dropdown">
                <div className="notification-header">
                  <strong>Notifications</strong>
                </div>

                {notificationLoading ? (
                  <p className="notification-empty">Loading...</p>
                ) : notifications.length === 0 ? (
                  <p className="notification-empty">No notifications</p>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={
                        notification.status === "PENDING"
                          ? "notification-item unread"
                          : "notification-item"
                      }
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div>
                        <strong>{notification.event_type}</strong>
                        <p>Order #{notification.order_id}</p>
                      </div>

                      <span
                        className={
                          notification.status === "PENDING"
                            ? "notification-status pending"
                            : "notification-status read"
                        }
                      >
                        {notification.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* LOGOUT */}
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="agent-content">
        {/* ERROR */}
        {error && <div className="error">{error}</div>}

        {/* AVAILABILITY */}
        <section className="agent-card">
          <div className="section-header">
            <div>
              <h2>Availability</h2>
              <p>
                Current status: <strong>{availability}</strong>
              </p>
            </div>
          </div>

          <div className="availability-buttons">
            <button
              className={availability === "AVAILABLE" ? "active" : ""}
              onClick={() => handleAvailability("AVAILABLE")}
              disabled={updating}
            >
              Available
            </button>

            <button
              className={availability === "BUSY" ? "active" : ""}
              onClick={() => handleAvailability("BUSY")}
              disabled={updating}
            >
              Busy
            </button>

            <button
              className={availability === "OFFLINE" ? "active" : ""}
              onClick={() => handleAvailability("OFFLINE")}
              disabled={updating}
            >
              Offline
            </button>
          </div>
        </section>

        {/* ORDERS */}
        <section className="agent-card">
          <div className="section-header">
            <div>
              <h2>My Assigned Orders</h2>
              <p>
                {orders.length} order{orders.length !== 1 ? "s" : ""}
              </p>
            </div>

            <button onClick={loadOrders} disabled={loading}>
              Refresh
            </button>
          </div>

          {loading ? (
            <p>Loading orders...</p>
          ) : orders.length === 0 ? (
            <div className="empty-state">
              <h3>No assigned orders</h3>
              <p>You currently have no deliveries assigned.</p>
            </div>
          ) : (
            <div className="agent-orders">
              {orders.map((order) => (
                <div className="agent-order" key={order.id}>
                  <div className="order-top">
                    <div>
                      <h3>Order #{order.id}</h3>
                      <span
                        className={`order-status ${getStatusClass(
                          order.current_status
                        )}`}
                      >
                        {order.current_status}
                      </span>
                    </div>

                    <button
                      onClick={() =>
                        navigate(`/agent/orders/${order.id}/tracking`)
                      }
                    >
                      Tracking
                    </button>
                  </div>

                  <div className="order-addresses">
                    <div>
                      <strong>Pickup</strong>
                      <p>{order.pickup_address}</p>
                    </div>

                    <div>
                      <strong>Drop</strong>
                      <p>{order.drop_address}</p>
                    </div>
                  </div>

                  {/* NEXT ACTION */}
                  <div className="order-actions">
                    {order.current_status === "ASSIGNED" && (
                      <button
                        onClick={() =>
                          handleStatusUpdate(order.id, "PICKED_UP")
                        }
                        disabled={updating}
                      >
                        Mark Picked Up
                      </button>
                    )}

                    {order.current_status === "PICKED_UP" && (
                      <button
                        onClick={() =>
                          handleStatusUpdate(order.id, "IN_TRANSIT")
                        }
                        disabled={updating}
                      >
                        Mark In Transit
                      </button>
                    )}

                    {order.current_status === "IN_TRANSIT" && (
                      <button
                        onClick={() =>
                          handleStatusUpdate(order.id, "OUT_FOR_DELIVERY")
                        }
                        disabled={updating}
                      >
                        Out for Delivery
                      </button>
                    )}

                    {order.current_status === "OUT_FOR_DELIVERY" && (
                      <>
                        <button
                          onClick={() =>
                            handleStatusUpdate(order.id, "DELIVERED")
                          }
                          disabled={updating}
                        >
                          Mark Delivered
                        </button>

                        <button
                          className="failed-button"
                          onClick={() => {
                            setFailedOrderId(order.id);
                            setFailureReason("");
                            setError("");
                          }}
                          disabled={updating}
                        >
                          Mark Failed
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* FAILED DELIVERY MODAL */}
      {failedOrderId && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Failed Delivery</h2>
            <p>Order #{failedOrderId}</p>

            <textarea
              value={failureReason}
              onChange={(event) => setFailureReason(event.target.value)}
              placeholder="Enter failure reason..."
              rows={5}
            />

            <div className="modal-actions">
              <button
                onClick={() => {
                  setFailedOrderId(null);
                  setFailureReason("");
                }}
                disabled={updating}
              >
                Cancel
              </button>

              <button
                className="failed-button"
                onClick={handleFailedDelivery}
                disabled={updating}
              >
                {updating ? "Submitting..." : "Confirm Failed Delivery"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentDashboard;