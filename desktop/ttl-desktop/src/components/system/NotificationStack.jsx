import { useEffect, useState } from "react";

import {
  subscribeToNotifications,
} from "../../services/runtime/notificationRuntime";

export default function NotificationStack() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    return subscribeToNotifications(setNotifications);
  }, []);

  return (
    <div className="fixed top-6 right-6 z-[9999] space-y-4">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className="
            w-[380px]
            rounded-2xl
            border
            border-slate-800
            bg-[#081028]
            shadow-2xl
            p-5
            backdrop-blur-xl
          "
        >
          <h3 className="text-xl font-bold text-white">
            {notification.title}
          </h3>

          <p className="mt-2 text-slate-400">
            {notification.message}
          </p>
        </div>
      ))}
    </div>
  );
}