import api from "./axios";

export const getAgentNotifications = async () => {
  const response = await api.get("/agent/notifications");
  return response.data;
};

export const markAgentNotificationRead = async (
  notificationId
) => {
  const response = await api.patch(
    `/agent/notifications/${notificationId}/read`
  );

  return response.data;
};