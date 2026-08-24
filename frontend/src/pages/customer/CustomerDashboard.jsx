import { useEffect, useState } from "react";
import {
  getMyOrders,
  getNotifications,
  rescheduleOrder,
  markNotificationRead,
} from "../../api/orderApi";
import { useNavigate } from "react-router-dom";

function CustomerDashboard() {

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const [rescheduleId, setRescheduleId] = useState(null);
  const [reason, setReason] = useState("");
  const [rescheduleLoading, setRescheduleLoading] = useState(false);
  const [rescheduleError, setRescheduleError] = useState("");

  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  const pendingCount = notifications.filter(
    (notification) =>
      notification.status === "PENDING"
  ).length;

  useEffect(() => {

    const loadOrders = async () => {

      try {

        const data = await getMyOrders();

        setOrders(data);

      } catch (error) {

        console.error(error);

        setError(
          error.response?.data?.detail ||
          "Failed to load orders"
        );

      } finally {

        setLoading(false);

      }
    };

    loadOrders();

  }, []);

  useEffect(() => {
    const loadNotifications = async () => {
      try {
        const data = await getNotifications();
        setNotifications(data);
      } catch (error) {
        console.error(
          "Failed to load notifications:",
          error
        );
      }
    };

    loadNotifications();
  }, []);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const handleLogout = () => {

    localStorage.removeItem("token");
    localStorage.removeItem("user");

    window.location.href = "/";

  };

  const handleReschedule = async () => {
    if (!reason.trim()) {
      setRescheduleError("Please enter a reason.");
      return;
    }

    try {
      setRescheduleLoading(true);
      setRescheduleError("");

      await rescheduleOrder(
        rescheduleId,
        reason
      );

      setRescheduleId(null);
      setReason("");

      // Reload orders
      const data = await getMyOrders();
      setOrders(data);

    } catch (error) {
      console.error(error);

      setRescheduleError(
        error.response?.data?.detail ||
        "Failed to reschedule order"
      );
    } finally {
      setRescheduleLoading(false);
    }
  };

  const handleNotificationClick = async (notification) => {
    try {
      if (notification.status === "PENDING") {
        await markNotificationRead(
          notification.id
        );

        setNotifications((previous) =>
          previous.map((item) =>
            item.id === notification.id
              ? {
                  ...item,
                  status: "READ",
                }
              : item
          )
        );
      }
    } catch (error) {
      console.error(
        "Failed to mark notification as read:",
        error
      );
    }
  };

  return (

    <div className="dashboard">

      {/* Header */}

      <header className="dashboard-header">

        <div>
          <h1>Last Mile Delivery</h1>

          <p>
            Welcome, {user?.name || "Customer"}
          </p>
        </div>

        <div className="header-actions">

          <div className="notification-wrapper">

            <button
              className="notification-button"
              onClick={() =>
                setShowNotifications(
                  !showNotifications
                )
              }
            >
              🔔

              {pendingCount > 0 && (
                <span className="notification-count">
                  {pendingCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="notification-dropdown">

                <div className="notification-header">
                  <strong>Notifications</strong>
                </div>

                {notifications.length === 0 ? (
                  <div className="no-notifications">
                    No notifications
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      className={`notification-item ${
                        notification.status === "PENDING"
                          ? "notification-unread"
                          : ""
                      }`}
                      key={notification.id}
                      onClick={() =>
                        handleNotificationClick(notification)
                      }
                    >
                      <div className="notification-title">
                        {notification.event_type}
                      </div>

                      <div className="notification-order">
                        Order #{notification.order_id}
                      </div>

                      <div className="notification-status">
                        {notification.status}
                      </div>

                      {notification.sent_at && (
                        <div className="notification-time">
                          {new Date(
                            notification.sent_at
                          ).toLocaleString()}
                        </div>
                      )}
                    </div>
                  ))
                )}

              </div>
            )}

          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      {/* Main content */}

      <main className="dashboard-content">

        <div className="dashboard-title">

          <div>
            <h2>My Orders</h2>

            <p>
              View and track your deliveries
            </p>
          </div>

          <button
            onClick={() =>
              navigate("/customer/create-order")
            }
          >
            + Create Order
          </button>

        </div>


        {/* Loading */}

        {loading && (
          <p>Loading orders...</p>
        )}


        {/* Error */}

        {error && (
          <div className="error">
            {error}
          </div>
        )}


        {/* No orders */}

        {!loading &&
          !error &&
          orders.length === 0 && (

            <div className="empty-state">

              <h3>No orders yet</h3>

              <p>
                Create your first delivery order.
              </p>

            </div>

          )}


        {/* Orders */}

        {!loading &&
          !error &&
          orders.length > 0 && (

            <div className="orders-list">

              {orders.map((order) => (

                <div
                  className="order-card"
                  key={order.id}
                >

                  <div className="order-card-header">

                    <div>

                      <h3>
                        Order #{order.id}
                      </h3>

                      <span
                        className={`status status-${order.current_status?.toLowerCase()}`}
                      >
                        {order.current_status}
                      </span>

                    </div>

                    <strong>
                      ₹{order.total_charge}
                    </strong>

                  </div>


                  <div className="route">

                    <div>

                      <span>Pickup</span>

                      <p>
                        {order.pickup_address}
                      </p>

                    </div>


                    <div className="arrow">
                      ↓
                    </div>


                    <div>

                      <span>Drop</span>

                      <p>
                        {order.drop_address}
                      </p>

                    </div>

                  </div>


                  <div className="order-actions">

                    <button
                      onClick={() =>
                        navigate(
                          `/customer/orders/${order.id}/tracking`
                        )
                      }
                    >
                      Track Order
                    </button>

                    {order.current_status ===
                      "FAILED" && (

                      <button
                        onClick={() => {
                          setRescheduleId(order.id);
                          setReason("");
                          setRescheduleError("");
                        }}
                      >
                        Reschedule
                      </button>

                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

      </main>


      {/* Reschedule modal */}

      {rescheduleId && (
        <div className="modal-overlay">

          <div className="modal">

            <h2>
              Reschedule Order #{rescheduleId}
            </h2>

            <p>
              Please provide a reason for rescheduling.
            </p>

            <textarea
              value={reason}
              onChange={(e) =>
                setReason(e.target.value)
              }
              placeholder="Example: Customer was unavailable..."
              rows={5}
            />

            {rescheduleError && (
              <div className="error">
                {rescheduleError}
              </div>
            )}

            <div className="modal-actions">

              <button
                className="cancel-button"
                onClick={() => {
                  setRescheduleId(null);
                  setReason("");
                  setRescheduleError("");
                }}
                disabled={rescheduleLoading}
              >
                Cancel
              </button>

              <button
                className="confirm-button"
                onClick={handleReschedule}
                disabled={rescheduleLoading}
              >
                {rescheduleLoading
                  ? "Rescheduling..."
                  : "Reschedule"}
              </button>

            </div>

          </div>

        </div>
      )}

    </div>

  );
}

export default CustomerDashboard;