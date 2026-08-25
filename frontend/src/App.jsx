import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";
import Agents from "./pages/admin/Agents";
import Login from "./pages/Login";
import Register from "./pages/Register";  
import CustomerDashboard
  from "./pages/customer/CustomerDashboard";

import OrderTracking
  from "./pages/customer/OrderTracking";

import CreateOrder
  from "./pages/customer/CreateOrder";

import AgentDashboard
  from "./pages/agent/AgentDashboard";

import AgentOrderTracking
  from "./pages/agent/AgentOrderTracking";

import AdminDashboard
  from "./pages/admin/AdminDashboard";

import Orders
  from "./pages/admin/Orders";
import Assignment
  from "./pages/admin/Assignment";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Login */}

        <Route
          path="/"
          element={<Login />}
        />
        <Route
  path="/register"
  element={<Register />}
/>

        {/* Customer */}

        <Route
          path="/customer"
          element={<CustomerDashboard />}
        />

        <Route
          path="/customer/create-order"
          element={<CreateOrder />}
        />

        <Route
          path="/customer/orders/:orderId/tracking"
          element={<OrderTracking />}
        />


        {/* Agent */}

        <Route
          path="/agent"
          element={<AgentDashboard />}
        />

        <Route
          path="/agent/orders/:orderId/tracking"
          element={<AgentOrderTracking />}
        />


        {/* Admin */}

        <Route
          path="/admin"
          element={<AdminDashboard />}
        />

        <Route
  path="/admin/orders"
  element={<Orders />}
/>

<Route
  path="/admin/agents"
  element={<Agents />}
/>

<Route
  path="/admin/assignment"
  element={<Assignment />}
/>
      </Routes>

    </BrowserRouter>
  );
}


export default App;