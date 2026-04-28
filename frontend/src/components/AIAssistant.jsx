import React, { useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

export default function AIAssistant() {
  const [jiraUrl, setJiraUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [intent, setIntent] = useState(null);
  const [diffData, setDiffData] = useState(null);
  const [showDiff, setShowDiff] = useState(false);
  const [editedCode, setEditedCode] = useState("");
  const [prLink, setPrLink] = useState("");

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8080/ai/analyze-jira", {
        jira_url: jiraUrl
      });
      setIntent(res.data?.intent || res.data);
    } catch (e) {
      alert("Failed to analyze Jira");
    }
    setLoading(false);
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      const res = await axios.post(
        "http://localhost:8080/automation/generate",
        { intent }
      );

      setDiffData(res.data);
      const code =
        res.data?.diff?.changes?.map(l => l.content).join("\n") || "";
      setEditedCode(code);
      setShowDiff(true);
    } catch (e) {
      alert("Automation failed");
    }
    setLoading(false);
  };

  const handleCreatePR = async () => {
    try {
      const res = await axios.post(
        "http://localhost:8080/automation/create-pr",
        { intent, code: editedCode }
      );

      setPrLink(res.data.pr_url);
    } catch (e) {
      alert("Failed to create PR");
    }
  };

  return (
    <div className="space-y-6">

      {/* HEADER */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-2">
          Generate Rule from Jira
        </h2>

        <div className="flex gap-3">
          <input
            className="input flex-1"
            value={jiraUrl}
            onChange={(e) => setJiraUrl(e.target.value)}
            placeholder="Paste Jira URL"
          />
          <button className="btn" onClick={handleAnalyze}>
            Analyze
          </button>
        </div>
      </div>

      {loading && <div className="text-gray-500">Processing...</div>}

      {/* INTENT CARD */}
      {intent && !showDiff && (
        <div className="bg-white rounded-xl shadow p-5">
          <h3 className="font-semibold text-gray-800 mb-3">
            Extracted Intent
          </h3>

          <div className="border rounded-lg overflow-hidden">

            {/* HEADER */}
            <div className="bg-gray-100 px-3 py-2 text-xs font-semibold text-gray-600">
              Extracted JSON
            </div>

            {/* BODY */}
            <div className="bg-white max-h-[250px] overflow-auto p-3">
              <pre className="text-xs font-mono whitespace-pre-wrap">
                {intent ? JSON.stringify(intent, null, 2) : ""}
              </pre>
            </div>

          </div>

          <div className="flex gap-2 mt-4">
            <button className="btn" onClick={handleApprove}>
              Approve
            </button>
            <button className="btn bg-gray-400">Reject</button>
          </div>
        </div>
      )}

      {/* CODE EDITOR */}
      {showDiff && diffData && (
        <div className="bg-white rounded-xl shadow p-5">

          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Edit Generated Code</h3>
            <span className="text-xs text-gray-500 font-mono">
              {diffData.file_path}
            </span>
          </div>

          {/* EDITOR */}
          <div className="border rounded overflow-hidden">
            <Editor
              height="400px"
              defaultLanguage="javascript"
              value={editedCode}
              onChange={(v) => setEditedCode(v || "")}
            />
          </div>

          {/* VALIDATION */}
          {diffData?.validation && !diffData.validation.is_valid && (
            <div className="bg-red-50 border border-red-300 p-3 rounded mt-3">
              {diffData.validation.errors.map((e, i) => (
                <div key={i}>• {e}</div>
              ))}
            </div>
          )}

          <div className="flex gap-3 mt-4">
            <button
              className="btn bg-green-600"
              onClick={handleCreatePR}
            >
              Create PR
            </button>

            <button
              className="btn bg-gray-400"
              onClick={() => setShowDiff(false)}
            >
              Back
            </button>
          </div>

          {/* PR SUCCESS */}
          {prLink && (
            <div className="mt-4 bg-green-50 border border-green-300 p-4 rounded">
              <div className="font-semibold text-green-700">
                PR Created Successfully 🎉
              </div>
              <a
                href={prLink}
                target="_blank"
                className="text-blue-600 underline text-sm"
              >
                View Pull Request
              </a>
            </div>
          )}

        </div>
      )}
    </div>
  );
}