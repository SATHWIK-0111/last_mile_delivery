import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Login from "./pages/Login";
import CustomerDashboard from "./pages/customer/CustomerDashboard";
import OrderTracking from "./pages/customer/OrderTracking";
import CreateOrder from "./pages/customer/CreateOrder";

function AgentDashboard() {
  return <h1>Agent Dashboard</h1>;
}

function AdminDashboard() {
  return <h1>Admin Dashboard</h1>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/customer"
          element={<CustomerDashboard />}
        />

        <Route
          path="/agent"
          element={<AgentDashboard />}
        />

        <Route
          path="/admin"
          element={<AdminDashboard />}
        />

        <Route
          path="/customer/orders/:orderId/tracking"
          element={<OrderTracking />}
        />

        <Route
  path="/customer/create-order"
  element={<CreateOrder />}
/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;