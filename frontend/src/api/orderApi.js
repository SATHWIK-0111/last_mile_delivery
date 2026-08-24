import api from "./axios";

export const getMyOrders = async () => {
  const response = await api.get("/orders/my");
  return response.data;
};

export const getOrder = async (orderId) => {
  const response = await api.get(`/orders/${orderId}`);
  return response.data;
};

export const getOrderTracking = async (orderId) => {
  const response = await api.get(
    `/orders/${orderId}/tracking`
  );
  return response.data;
};

export const createOrder = async (orderData) => {
  const response = await api.post(
    "/orders",
    orderData
  );
  return response.data;
};

export const calculateOrder = async (orderData) => {
  const response = await api.post(
    "/orders/calculate",
    orderData
  );
  return response.data;
};

export const rescheduleOrder = async (
  orderId,
  reason
) => {
  const response = await api.patch(
    `/orders/${orderId}/reschedule`,
    { reason }
  );
  return response.data;
};

export const getNotifications = async () => {
  const response = await api.get(
    "/orders/notifications"
  );
  return response.data;
};

export const markNotificationRead = async (
  notificationId
) => {
  const response = await api.patch(
    `/orders/notifications/${notificationId}/read`
  );

  return response.data;
};