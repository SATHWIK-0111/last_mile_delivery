import { Link, useLocation, useNavigate } from "react-router-dom";

function AdminLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      label: "Dashboard",
      path: "/admin"
    },
    {
      label: "Orders",
      path: "/admin/orders"
    },
    {
      label: "Agents",
      path: "/admin/agents"
    },
    {
      label: "Assignment",
      path: "/admin/assignment"
    }
  ];

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="admin-layout">

      {/* ================= NAVBAR ================= */}

      <header className="admin-navbar">

        <div className="admin-brand">
          <h2>Last Mile Delivery</h2>
          <span>Admin Portal</span>
        </div>

        <div className="admin-user">

          <div className="admin-avatar">
            A
          </div>

          <div className="admin-user-info">
            <strong>Administrator</strong>
            <span>Admin</span>
          </div>

          <button
            className="admin-logout"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      {/* ================= BODY ================= */}

      <div className="admin-body">

        {/* ================= SIDEBAR ================= */}

        <aside className="admin-sidebar">

          <div className="sidebar-section-title">
            MANAGEMENT
          </div>

          {menuItems.map((item) => {

            const active =
              location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={
                  active
                    ? "admin-nav-item active"
                    : "admin-nav-item"
                }
              >

                <span className="admin-nav-icon">
                  {item.label === "Dashboard" && "📊"}
                  {item.label === "Orders" && "📦"}
                  {item.label === "Agents" && "👤"}
                  {item.label === "Assignment" && "🔄"}
                </span>

                {item.label}

              </Link>
            );

          })}


          <div className="sidebar-section-title system-title">
            SYSTEM
          </div>

          <Link
            to="/admin/settings"
            className={
              location.pathname === "/admin/settings"
                ? "admin-nav-item active"
                : "admin-nav-item"
            }
          >
            <span className="admin-nav-icon">
              ⚙️
            </span>

            Settings
          </Link>

        </aside>


        {/* ================= CONTENT ================= */}

        <main className="admin-main">

          {children}

        </main>

      </div>

    </div>
  );
}

export default AdminLayout;