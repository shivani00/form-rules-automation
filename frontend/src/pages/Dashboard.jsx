import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import BusinessRules from "../components/BusinessRules";
import OsariMapping from "../components/OsariMapping";
import FormsExplorer from "../components/FormsExplorer";
import AIAssistant from "../components/AIAssistant";

export default function Dashboard() {
  const [tab, setTab] = useState("ai");

  const renderContent = () => {
    switch (tab) {
      case "business":
        return <BusinessRules />;
      case "osari":
        return <OsariMapping />;
      case "ai":
        return <AIAssistant />;
      case "forms":
        return <FormsExplorer />;
      default:
        return <BusinessRules />;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-white to-red-50">
      
      {/* SIDEBAR */}
      <Sidebar setTab={setTab} />

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col">
        
        {/* HEADER */}
        <Header />

        {/* CONTENT AREA */}
        <div className="flex-1 p-6 overflow-auto">
          
          {/* PAGE TITLE */}
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            {tab === "business" && "Business Rule Builder"}
            {tab === "osari" && "OSARI Mappings"}
            {tab === "ai" && "Generate Rules"}
            {tab === "forms" && "Forms Explorer"}
          </h2>

          {/* MAIN CARD WRAPPER */}
          <div className="bg-white rounded-2xl shadow-card p-6">
            {renderContent()}
          </div>

        </div>
      </div>
    </div>
  );
}