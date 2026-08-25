import { NavLink } from "react-router-dom";

function AdminSidebar() {

  const menuItems = [
    {
      label: "Dashboard",
      path: "/admin",
      icon: "📊",
      end: true
    },
    {
      label: "Orders",
      path: "/admin/orders",
      icon: "📦"
    },
    {
      label: "Agents",
      path: "/admin/agents",
      icon: "👤"
    },
    {
      label: "Assignment",
      path: "/admin/assignment",
      icon: "🔄"
    },
    
  ];

  return (
    <aside className="admin-sidebar">

      <div className="sidebar-title">
        MANAGEMENT
      </div>

      <nav>

        {menuItems.map((item) => (

          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              `admin-nav-item ${
                isActive
                  ? "admin-nav-item-active"
                  : ""
              }`
            }
          >

            <span className="admin-nav-icon">
              {item.icon}
            </span>

            <span>
              {item.label}
            </span>

          </NavLink>

        ))}

      </nav>

    </aside>
  );
}

export default AdminSidebar;