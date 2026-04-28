import { Sparkles, Bell, User } from "lucide-react";

export default function Header() {
  return (
    <div className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-3 flex items-center justify-between shadow-md">

      {/* LEFT: BRAND */}
      <div className="flex items-center gap-3">
        
        {/* ICON */}
        <div className="bg-white rounded-full w-10 h-10 flex items-center justify-center shadow">
          <Sparkles className="text-red-600" size={18} />
        </div>

        {/* TITLE */}
        <div>
          <h1 className="font-bold text-lg">
            AI Rule Authoring Studio
          </h1>
          <p className="text-xs opacity-90">
            Intelligent Rule Generation • Validation • Governance
          </p>
        </div>
      </div>

      {/* RIGHT: ACTIONS */}
      <div className="flex items-center gap-4">

        {/* Notifications */}
        <div className="relative cursor-pointer">
          <Bell size={18} />
          <span className="absolute -top-1 -right-1 bg-white text-red-600 text-[10px] px-1 rounded-full">
            3
          </span>
        </div>

        {/* User */}
        <div className="flex items-center gap-2 cursor-pointer">
          <User size={18} />
          <span className="text-sm">Shivani</span>
        </div>

      </div>
    </div>
  );
}