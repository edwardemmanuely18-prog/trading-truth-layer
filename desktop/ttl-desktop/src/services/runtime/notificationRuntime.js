let listeners = [];

let notifications = [];

const MAX_NOTIFICATIONS = 4;

function emit() {
  listeners.forEach((listener) => {
    listener([...notifications]);
  });
}

export function subscribeToNotifications(callback) {
  listeners.push(callback);

  callback([...notifications]);

  return () => {
    listeners = listeners.filter(
      (listener) => listener !== callback
    );
  };
}

export function removeNotification(id) {
  notifications = notifications.filter(
    (notification) => notification.id !== id
  );

  emit();
}

export function pushNotification(notification) {
  const title =
    notification.title || "System Notification";

  const message =
    notification.message || "";

  const type =
    notification.type || "info";

  /* =========================================
     DEDUPLICATION
  ========================================= */

  const duplicate = notifications.find(
    (item) =>
      item.title === title &&
      item.message === message
  );

  if (duplicate) {
    return;
  }

  /* =========================================
     CREATE NOTIFICATION
  ========================================= */

  const id = crypto.randomUUID();

  const item = {
    id,
    title,
    message,
    type,
    createdAt: Date.now(),
  };

  /* =========================================
     STACK LIMIT
  ========================================= */

  notifications = [
    item,
    ...notifications,
  ].slice(0, MAX_NOTIFICATIONS);

  emit();

  /* =========================================
     AUTO REMOVE
  ========================================= */

  setTimeout(() => {
    removeNotification(id);
  }, 5000);
}