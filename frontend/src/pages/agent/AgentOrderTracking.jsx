import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getAgentOrderTracking } from "../../api/agentApi";

function AgentOrderTracking() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadTracking = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getAgentOrderTracking(orderId);

        setTracking(data);
      } catch (error) {
        console.error(error);

        setError(
          error.response?.data?.detail ||
          "Failed to load tracking information"
        );
      } finally {
        setLoading(false);
      }
    };

    loadTracking();
  }, [orderId]);

  if (loading) {
    return (
      <div className="tracking-page">
        <div className="tracking-container">
          <p>Loading tracking information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tracking-page">
        <div className="tracking-container">

          <button
            className="back-button"
            onClick={() => navigate("/agent")}
          >
            ← Back to Dashboard
          </button>

          <div className="error">
            {error}
          </div>

        </div>
      </div>
    );
  }

  const events =
    tracking?.events ||
    tracking?.history ||
    tracking?.tracking_history ||
    [];

  const currentStatus =
    tracking?.current_status ||
    tracking?.status ||
    events[events.length - 1]?.status ||
    "UNKNOWN";

  return (
    <div className="tracking-page">

      <div className="tracking-container">

        {/* BACK BUTTON */}

        <button
          className="back-button"
          onClick={() => navigate("/agent")}
        >
          ← Back to Dashboard
        </button>


        {/* ORDER HEADER */}

        <div className="tracking-header">

          <div>

            <p className="tracking-label">
              ORDER
            </p>

            <h1>
              Order #{orderId}
            </h1>

          </div>

          <span className="tracking-current-status">
            {currentStatus}
          </span>

        </div>


        {/* TRACKING HISTORY */}

        <div className="tracking-card">

          <h2>
            Tracking History
          </h2>

          {events.length === 0 ? (

            <p className="no-events">
              No tracking events available.
            </p>

          ) : (

            <div className="timeline">

              {events.map((event, index) => (

                <div
                  className="timeline-item"
                  key={event.id || index}
                >

                  <div className="timeline-marker">
                    ✓
                  </div>

                  <div className="timeline-content">

                    <div className="timeline-top">

                      <h3>
                        {event.status}
                      </h3>

                      <span>
                        {event.timestamp
                          ? new Date(
                              event.timestamp
                            ).toLocaleString()
                          : ""}
                      </span>

                    </div>

                    {event.remarks && (
                      <p>
                        {event.remarks}
                      </p>
                    )}

                    {event.actor_role && (
                      <small>
                        Updated by {event.actor_role}
                      </small>
                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </div>
  );
}

export default AgentOrderTracking;