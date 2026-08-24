import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  calculateOrder,
  createOrder,
} from "../../api/orderApi";

function CreateOrder() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    pickup_address: "",
    pickup_latitude: "",
    pickup_longitude: "",

    drop_address: "",
    

    length: "",
    breadth: "",
    height: "",
    actual_weight: "",

    order_type: "B2C",
    payment_type: "COD",
  });

  const [charge, setCharge] = useState(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const buildPayload = () => ({
    pickup_address: form.pickup_address,
    pickup_latitude: Number(form.pickup_latitude),
    pickup_longitude: Number(form.pickup_longitude),

    drop_address: form.drop_address,

    length: Number(form.length),
    breadth: Number(form.breadth),
    height: Number(form.height),
    actual_weight: Number(form.actual_weight),

    order_type: form.order_type,
    payment_type: form.payment_type,
  });

  const handleCalculate = async (event) => {
    event.preventDefault();

    setError("");
    setCharge(null);
    setLoading(true);

    try {
      const data = await calculateOrder(
        buildPayload()
      );

      setCharge(data);

    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Failed to calculate delivery charge"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    setError("");
    setCreating(true);

    try {
      await createOrder(buildPayload());

      navigate("/customer");

    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Failed to create order"
      );
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="create-order-page">

      <div className="create-order-container">

        <button
          className="back-button"
          onClick={() => navigate("/customer")}
        >
          ← Back to Orders
        </button>

        <div className="create-order-header">
          <h1>Create New Order</h1>

          <p>
            Enter your delivery details below.
          </p>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <form
          className="order-form"
          onSubmit={handleCalculate}
        >

          {/* PICKUP */}

          <section className="form-section">

            <h2>Pickup Details</h2>

            <div className="form-group">
              <label>Pickup Address</label>

              <input
                name="pickup_address"
                value={form.pickup_address}
                onChange={handleChange}
                placeholder="Enter pickup address"
                required
              />
            </div>

            <div className="form-row">

              <div className="form-group">
                <label>Pickup Latitude</label>

                <input
                  type="number"
                  step="any"
                  name="pickup_latitude"
                  value={form.pickup_latitude}
                  onChange={handleChange}
                  placeholder="e.g. 16.3067"
                  required
                />
              </div>

              <div className="form-group">
                <label>Pickup Longitude</label>

                <input
                  type="number"
                  step="any"
                  name="pickup_longitude"
                  value={form.pickup_longitude}
                  onChange={handleChange}
                  placeholder="e.g. 80.4365"
                  required
                />
              </div>

            </div>

          </section>


          {/* DROP */}

          <section className="form-section">

            <h2>Drop Details</h2>

            <div className="form-group">
              <label>Drop Address</label>

              <input
                name="drop_address"
                value={form.drop_address}
                onChange={handleChange}
                placeholder="Enter drop address"
                required
              />
            </div>

          </section>


          {/* PACKAGE */}

          <section className="form-section">

            <h2>Package Details</h2>

            <div className="form-row">

              <div className="form-group">
                <label>Length</label>

                <input
                  type="number"
                  step="any"
                  name="length"
                  value={form.length}
                  onChange={handleChange}
                  placeholder="cm"
                  required
                />
              </div>

              <div className="form-group">
                <label>Breadth</label>

                <input
                  type="number"
                  step="any"
                  name="breadth"
                  value={form.breadth}
                  onChange={handleChange}
                  placeholder="cm"
                  required
                />
              </div>

              <div className="form-group">
                <label>Height</label>

                <input
                  type="number"
                  step="any"
                  name="height"
                  value={form.height}
                  onChange={handleChange}
                  placeholder="cm"
                  required
                />
              </div>

            </div>

            <div className="form-group">
              <label>Actual Weight</label>

              <input
                type="number"
                step="any"
                name="actual_weight"
                value={form.actual_weight}
                onChange={handleChange}
                placeholder="kg"
                required
              />
            </div>

          </section>


          {/* DELIVERY */}

          <section className="form-section">

            <h2>Delivery Options</h2>

            <div className="form-row">

              <div className="form-group">
                <label>Order Type</label>

                <select
                  name="order_type"
                  value={form.order_type}
                  onChange={handleChange}
                >
                  <option value="B2C">
                    B2C
                  </option>

                  <option value="B2B">
                    B2B
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label>Payment Type</label>

                <select
                  name="payment_type"
                  value={form.payment_type}
                  onChange={handleChange}
                >
                  <option value="COD">
                    Cash on Delivery
                  </option>

                  <option value="PREPAID">
                    Prepaid
                  </option>
                </select>
              </div>

            </div>

          </section>


          {/* CALCULATE */}

          <button
            className="calculate-button"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Calculating..."
              : "Calculate Delivery Charge"}
          </button>

        </form>


        {/* CHARGE */}

        {charge && (
          <div className="charge-card">

            <h2>Delivery Estimate</h2>

            <div className="charge-details">

              <span>
                Calculated Charge
              </span>

              <strong>
                ₹
                {charge.total_charge ??
                  charge.final_charge ??
                  charge.amount ??
                  "—"}
              </strong>

            </div>

            <button
              className="create-button"
              onClick={handleCreate}
              disabled={creating}
            >
              {creating
                ? "Creating Order..."
                : "Confirm & Create Order"}
            </button>

          </div>
        )}

      </div>

    </div>
  );
}

export default CreateOrder;