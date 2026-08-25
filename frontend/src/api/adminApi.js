import api from "./axios";

// ================================
// ORDERS
// ================================

export const getAdminOrders = async () => {
  const response = await api.get("/admin/orders");
  return response.data;
};

export const getAdminOrder = async (orderId) => {
  const response = await api.get(
    `/admin/orders/${orderId}`
  );

  return response.data;
};

export const autoAssignAgent = async (orderId) => {
  const response = await api.post(
    `/admin/orders/${orderId}/auto-assign`
  );

  return response.data;
};

export const assignAgent = async (
  orderId,
  agentId
) => {
  const response = await api.post(
    `/admin/orders/${orderId}/assign`,
    null,
    {
      params: {
        agent_id: agentId
      }
    }
  );

  return response.data;
};


// ================================
// AGENTS
// ================================

export const getAdminAgents = async () => {
  const response = await api.get(
    "/admin/agents"
  );

  return response.data;
};

export const updateAgentAvailability = async (
  agentId,
  availability_status
) => {
  const response = await api.patch(
    `/admin/agents/${agentId}/availability`,
    {
      availability_status
    }
  );

  return response.data;
};


// ================================
// ZONES
// ================================

export const getAdminZones = async () => {
  const response = await api.get(
    "/admin/zones"
  );

  return response.data;
};

export const updateAgentZone = async (
  agentId,
  zoneId
) => {
  const response = await api.put(
    `/admin/agents/${agentId}/zone`,
    null,
    {
      params: {
        zone_id: zoneId
      }
    }
  );

  return response.data;
};


// ================================
// TRACKING
// ================================

export const getAdminOrderTracking = async (
  orderId
) => {
  const response = await api.get(
    `/admin/orders/${orderId}/tracking`
  );

  return response.data;
};