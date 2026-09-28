"use client";

import React, { useState, useEffect } from "react";
import { Bell, Check, ExternalLink, Info } from "lucide-react";
import Link from "next/link";
import { api } from "../../lib/api";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadNotifs = () => {
    setLoading(true);
    api.getNotifications()
      .then((data) => setNotifications(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadNotifs();
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-slate-800 pb-5 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Notification Center</h1>
          <p className="text-xs text-slate-400 mt-1">Alerts for grant matches, deadlines, and human approval gates.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : notifications.length > 0 ? (
        <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-850">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 flex items-start justify-between gap-4 transition-colors ${
                notif.is_read ? "bg-slate-950/40" : "bg-indigo-950/20"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                  <Bell className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{notif.title}</h4>
                  <p className="text-xs text-slate-300 mt-0.5">{notif.message}</p>
                  <span className="text-[10px] text-slate-500 mt-1 block">
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {notif.reference_link && (
                  <Link
                    href={notif.reference_link}
                    className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 text-xs flex items-center gap-1"
                  >
                    <span>View</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                )}
                {!notif.is_read && (
                  <button
                    onClick={() => handleMarkRead(notif.id)}
                    className="p-1.5 text-slate-400 hover:text-emerald-400 rounded hover:bg-slate-800"
                    title="Mark as read"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-12 text-center text-xs text-slate-400">
          <Info className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="font-semibold text-slate-300 mb-1">No notifications</p>
          <p className="text-slate-500">You are all caught up on grant alerts and verification updates.</p>
        </div>
      )}
    </div>
  );
}
