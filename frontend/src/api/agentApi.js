import api from "./axios";

export const getAgentOrders = async () => {
  const response = await api.get("/agent/orders");
  return response.data;
};

export const updateAvailability = async (
  availability_status
) => {
  const response = await api.patch(
    "/agent/availability",
    {
      availability_status,
    }
  );

  return response.data;
};

export const updateOrderStatus = async (
  orderId,
  status
) => {
  const response = await api.patch(
    `/agent/orders/${orderId}/status`,
    {
      status,
    }
  );

  return response.data;
};

export const failOrder = async (
  orderId,
  reason
) => {
  const response = await api.patch(
    `/agent/orders/${orderId}/failed`,
    {
      reason,
    }
  );

  return response.data;
};

export const getAgentOrderTracking = async (
  orderId
) => {
  const response = await api.get(
    `/agent/orders/${orderId}/tracking`
  );

  return response.data;
};

export const getAgentProfile = async () => {
  const response = await api.get("/agent/me");
  return response.data;
};

