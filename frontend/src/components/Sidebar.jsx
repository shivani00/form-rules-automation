import React from "react";
import { FileText, GitBranch, Database, Layers } from "lucide-react";

export default function Sidebar({ setTab }) {
  const items = [
    { name: "AI - Generate Rules", key: "ai", icon: <GitBranch size={18}/> },
    { name: "Business Rules", key: "business", icon: <FileText size={18}/> },
    { name: "OSARI Mapping", key: "osari", icon: <Database size={18}/> },
    { name: "Forms", key: "forms", icon: <Layers size={18}/> }
  ];

  return (
    <div className="w-64 bg-white shadow-xl p-4">
      <h1 className="text-xl font-bold text-red-600 mb-4">Rule Platform</h1>

      {items.map(i => (
        <div
          key={i.key}
          onClick={() => setTab(i.key)}
          className="flex items-center gap-2 p-2 cursor-pointer hover:bg-red-100 rounded"
        >
          {i.icon}
          {i.name}
        </div>
      ))}
    </div>
  );
}