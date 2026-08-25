import { useNavigate } from "react-router-dom";

function AdminNavbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/");
  };

  return (
    <header className="admin-navbar">

      <div className="admin-navbar-brand">
        <h2>Last Mile Delivery</h2>
        <span>Admin Portal</span>
      </div>

      <div className="admin-navbar-right">

        <div className="admin-user">
          <div className="admin-avatar">
            A
          </div>

          <div>
            <strong>Administrator</strong>
            <small>Admin</small>
          </div>
        </div>

        <button
          className="admin-logout"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

    </header>
  );
}

export default AdminNavbar;