import React from "react";

export default function FormsExplorer() {
  return (
    <div className="card">
      <h2 className="text-xl text-red-600 mb-4">Forms Explorer</h2>

      <div className="grid grid-cols-3 gap-4">
        {[1,2,3].map(i => (
          <div key={i} className="p-4 border rounded shadow">
            <h3 className="font-bold">Form WA1200{i}</h3>
            <p className="text-sm text-gray-600">State: MI, RI</p>
          </div>
        ))}
      </div>
    </div>
  );
}