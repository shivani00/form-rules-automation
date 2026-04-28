import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import BusinessRules from "../components/BusinessRules";
import OsariMapping from "../components/OsariMapping";
import FormsExplorer from "../components/FormsExplorer";
import AIAssistant from "../components/AIAssistant";

export default function Dashboard() {
  const [tab, setTab] = useState("ai");

  // 🔥 controls reset of AI assistant
  const [aiSessionKey, setAiSessionKey] = useState(Date.now());

  const handleNewSession = () => {
    setAiSessionKey(Date.now()); // 🔥 forces remount
  };

  const renderContent = () => {
    switch (tab) {
      case "business":
        return <BusinessRules />;
      case "osari":
        return <OsariMapping />;
      case "ai":
        return <AIAssistant key={aiSessionKey} />; // 🔥 important
      case "forms":
        return <FormsExplorer />;
      default:
        return <BusinessRules />;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-white to-red-50">

      {/* SIDEBAR */}
      <div className="flex-shrink-0">
        <Sidebar setTab={setTab} />
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col">

        {/* HEADER */}
        <Header />

        {/* CONTENT AREA */}
        <div className="flex-1 p-6 overflow-hidden flex flex-col">

          {/* 🔥 TITLE + BUTTON ROW */}
          <div className="flex justify-between items-center mb-4">

            <h2 className="text-2xl font-semibold text-gray-800">
              {tab === "business" && "Business Rule Builder"}
              {tab === "osari" && "OSARI Mappings"}
              {tab === "ai" && "Generate Rules"}
              {tab === "forms" && "Forms Explorer"}
            </h2>

            {/* 🔥 ONLY SHOW FOR AI TAB */}
            {tab === "ai" && (
              <button
                onClick={handleNewSession}
                className="bg-red-600 text-white px-4 py-2 rounded-full text-sm"
              >
                New Session
              </button>
            )}

          </div>

          {/* MAIN CARD */}
          <div className="bg-white rounded-2xl shadow-card p-6 flex-1 flex flex-col overflow-x-auto">
            {renderContent()}
          </div>

        </div>
      </div>
    </div>
  );
}