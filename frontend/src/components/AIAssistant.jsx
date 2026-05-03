import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [intent, setIntent] = useState(null);
  const [editedCode, setEditedCode] = useState("");
  const [testCode, setTestCode] = useState(""); // 🔥 NEW
  const [showEditor, setShowEditor] = useState(false);
  const [activeTab, setActiveTab] = useState("rule"); // 🔥 NEW
  const [sessionId, setSessionId] = useState(Date.now().toString());

  const bottomRef = useRef(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  const initializedRef = useRef(false);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    addMessage(
      "assistant",
      "Hi 👋\n\nNeed help with a form rule?\n\nJust paste the Jira story and I’ll take care of the rest."
    );
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const saved = localStorage.getItem("ai-editor");
    if (saved) {
      const parsed = JSON.parse(saved);
      setEditedCode(parsed.code || "");
      setTestCode(parsed.test || "");
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "ai-editor",
      JSON.stringify({
        code: editedCode,
        test: testCode
      })
    );
  }, [editedCode, testCode]);

  const addMessage = (role, content, actions = []) => {
    setMessages(prev => [...prev, { role, content, actions }]);
  };

  const handleAnalyze = async (jira) => {
    setLoading(true);
    addMessage("assistant", "Got it. Let me understand this story...");

    try {
      const res = await axios.post(
        "http://localhost:8080/ai/analyze-jira",
        { jira_url: jira, session_id: sessionId }
      );

      const data = res.data?.intent || res.data;
      setIntent(data);

      addMessage("assistant", "Here’s what I understood 👇");

      addMessage(
        "assistant",
        JSON.stringify(data, null, 2),
        ["approve", "analyze_more"]
      );
    } catch {
      addMessage("assistant", "Something went wrong while analyzing the story.");
    }

    setLoading(false);
  };

  const handleApprove = async () => {
    setLoading(true);
    addMessage("assistant", "Perfect 👍 Generating the rule now...");

    try {
      const res = await axios.post(
        "http://localhost:8080/automation/generate",
        { intent, session_id: sessionId }
      );

      const code = res.data?.code || "";
      const test = res.data?.test_code || "";

      setEditedCode(code);
      setTestCode(test);
      setShowEditor(true);

      addMessage(
        "assistant",
        "I’ve generated the rule and test cases.\n\nYou can review them.",
        ["create_pr", "make_changes"]
      );
    } catch {
      addMessage("assistant", "Failed to generate rule.");
    }

    setLoading(false);
  };

  const handleChanges = async (text) => {
    setLoading(true);
    addMessage("assistant", "Updating based on your input...");

    try {
      const res = await axios.post(
        "http://localhost:8080/automation/generate",
        {
          intent,
          feedback: text,
          session_id: sessionId
        }
      );

      const code = res.data?.code || "";
      const test = res.data?.test_code || "";

      setEditedCode(code);
      setTestCode(test);
      setShowEditor(true);

      addMessage("assistant", "Done 👍 Let me know if you want more changes.");
    } catch {
      addMessage("assistant", "Couldn't apply those changes.");
    }

    setLoading(false);
  };

  const handleCreatePR = async () => {
    addMessage("assistant", "Creating PR...");

    try {
      const res = await axios.post(
        "http://localhost:8080/automation/create-pr",
        {
          intent,
          code: editedCode,
          test_code: testCode,
          file_path: null, // 🔥 IMPORTANT (or store from generate if you want)
          test_file_path: null
        }
      );

      addMessage(
        "assistant",
        `All set 🎉\n\nHere’s your PR:\n${res.data.pr_url}`
      );
    } catch {
      addMessage("assistant", "Failed to create PR.");
    }
  };

  const handleMakeChanges = async (text) => {
    const instruction = text || input;

    if (!instruction?.trim()) return;

    setLoading(true);
    setInput("");

    addMessage("assistant", "Applying your changes...");

    try {
      const res = await axios.post(
        "http://localhost:8080/automation/make-changes",
        {
          instruction,
          session_id: sessionId,
          code: editedCode,        // fallback safety
          test_code: testCode      // fallback safety
        }
      );

      const updatedCode = res.data?.code || editedCode;
      const updatedTest = res.data?.test_code || testCode;

      setEditedCode(updatedCode);
      setTestCode(updatedTest);
      setShowEditor(true);

      addMessage("assistant", "Done 👍 Your changes have been applied.");
    } catch (err) {
      addMessage("assistant", "Failed to apply changes.");
    }

    setLoading(false);
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userInput = input;
    setInput("");

    addMessage("user", userInput);

    if (!intent) {
      await handleAnalyze(userInput);
    } else {
      await handleMakeChanges(userInput);
    }
  };

  const handleAction = (action, payload) => {
    if (action === "approve") handleApprove();
    if (action === "create_pr") handleCreatePR();
    if (action === "view_jira_stories") handleViewJiraStories();
    if (action === "select_rule") handleSelectRule(payload);
    if (action === "analyze_more") handleMoreAnalysis();
    if (action === "make_changes") {
      addMessage("assistant", "Tell me what changes you want.");
      setTimeout(() => {
        document.querySelector("input")?.focus();
      }, 100);
    }
  };

  const handleViewJiraStories = async () => {
    setLoading(true);
    addMessage("assistant", "Fetching available rules...");

    try {
      const res = await axios.get("http://localhost:8080/ai/jira-rules");

      const rules = res.data || [];

      if (rules.length === 0) {
        addMessage("assistant", "No rules found.");
      } else {
        addMessage(
          "assistant",
          "Select a rule:",
          rules.map(r => ({
            label: `${r.rule_number} (${r.story_count} stories)`,
            value: r.rule_number
          }))
        );
      }
    } catch {
      addMessage("assistant", "Failed to fetch rules.");
    }

    setLoading(false);
  };

  const handleMoreAnalysis = async () => {
    setLoading(true);
    addMessage("assistant", "Analyzing the story in more detail...");

    try {
      const res = await axios.post(
        "http://localhost:8080/ai/analyze-jira",
        { jira_url: intent?.jira_url }
      );

      const data = res.data?.intent || res.data;

      addMessage("assistant", JSON.stringify(data, null, 2));
    } catch {
      addMessage("assistant", "Couldn't analyze further.");
    }

    setLoading(false);
  };

  const handleNewSession = async () => {
    await axios.post("http://localhost:8080/automation/reset-session", {
      session_id: sessionId
    });

    setMessages([]);
    setIntent(null);
    setEditedCode("");
    setTestCode("");
    setShowEditor(false);

    const newSession = Date.now().toString();
    setSessionId(newSession);

    addMessage("assistant", "New session started 🚀");
  };

  const handleSelectRule = async (ruleNumber) => {
    setLoading(true);
    addMessage("assistant", `Fetching Jira stories for ${ruleNumber}...`);

    try {
      const res = await axios.get(
        `http://localhost:8080/ai/jira-by-rule/${ruleNumber}`
      );

      const data = res.data;

      if (!data || data.message) {
        addMessage("assistant", "No Jira found.");
      } else {
        const formatted = data.stories.map((s, i) =>
          `🔹 Story ${i + 1}
Jira: ${s.jira_url}
Created: ${s.created_at}`
        ).join("\n\n");

        addMessage("assistant", formatted);
      }
    } catch {
      addMessage("assistant", "Error fetching Jira.");
    }

    setLoading(false);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">

      {/* CHAT */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className="max-w-xl px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap bg-white shadow">

              {msg.content.split("\n").map((line, i) => {
                const urlMatch = line.match(/https?:\/\/[^\s]+/);

                if (urlMatch) {
                  const url = urlMatch[0];

                  return (
                    <div key={i}>
                      {line.replace(url, "")}
                      <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline break-all"
                      >
                        {url}
                      </a>
                    </div>
                  );
                }

                return <div key={i}>{line}</div>;
              })}

              {msg.actions?.length > 0 && (
                <div className="flex gap-2 mt-3 flex-wrap">

                  {msg.actions.map((a, idx) => {

                    if (a === "approve") {
                      return (
                        <button key={idx} className="bg-red-600 text-white px-4 py-2 rounded-full" onClick={() => handleAction(a)}>
                          APPROVE
                        </button>
                      );
                    }

                    if (a === "analyze_more") {
                      return (
                        <button key={idx} className="bg-red-600 text-white px-5 py-2 rounded-full" onClick={() => handleAction(a)}>
                          MORE ANALYSIS
                        </button>
                      );
                    }

                    if (a === "create_pr") {
                      return (
                        <div key={idx} className="flex gap-2 flex-wrap">

                          <button
                            className="bg-red-600 text-white px-4 py-2 rounded-full"
                            onClick={() => handleAction("create_pr")}
                          >
                            CREATE PR
                          </button>

                          <button
                            className="bg-red-600 text-white px-4 py-2 rounded-full"
                            onClick={() => {
                              addMessage("assistant", "Tell me what changes you want.");
                              document.querySelector("input")?.focus();
                            }}
                          >
                            MAKE CHANGES
                          </button>

                          <button
                            className="bg-red-600 text-white px-5 py-2 rounded-full"
                            onClick={() => setShowEditor(true)}
                          >
                            OPEN EDITOR
                          </button>

                        </div>
                      );
                    }

                    if (typeof a === "object" && a.label && a.value) {
                      return (
                        <button
                          key={idx}
                          className="bg-blue-100 px-3 py-1 rounded-full"
                          onClick={() => handleAction("select_rule", a.value)}
                        >
                          {a.label}
                        </button>
                      );
                    }

                    return null;
                  })}

                </div>
              )}

            </div>
          </div>
        ))}

        {loading && <div className="text-gray-400">Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      {/* 🔥 EDITOR MODAL */}
      {showEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white w-[90%] h-[85%] rounded-xl flex flex-col shadow-lg">

            <div className="flex justify-between items-center p-4 border-b">
              <div className="flex gap-3">
                <button
                  className={`px-4 py-1 rounded-full ${activeTab === "rule" ? "bg-red-600 text-white" : "bg-gray-200"}`}
                  onClick={() => setActiveTab("rule")}
                >
                  Rule File
                </button>
                <button
                  className={`px-4 py-1 rounded-full ${activeTab === "test" ? "bg-red-600 text-white" : "bg-gray-200"}`}
                  onClick={() => setActiveTab("test")}
                >
                  Test File
                </button>
              </div>

              <button onClick={() => setShowEditor(false)}>✕</button>
            </div>

            <Editor
              height="100%"
              language="javascript"
              value={activeTab === "rule" ? editedCode : testCode}
              onChange={(value) => {
                if (activeTab === "rule") setEditedCode(value);
                else setTestCode(value);
              }}
            />

            <div className="p-4 border-t flex justify-end gap-3">
              <button className="bg-red-600 text-white px-5 py-2 rounded-full" onClick={() => {
                addMessage("assistant", "What changes should I apply?");
                document.querySelector("input")?.focus();
              }}>
                MAKE CHANGES
              </button>
              <button
                className="bg-red-600 text-white px-5 py-2 rounded-full"
                onClick={handleCreatePR}
              >
                CREATE PR
              </button>
            </div>

          </div>
        </div>
      )}

      {/* INPUT */}
      <div className="p-4 border-t bg-white flex gap-3">
        <input
          className="flex-1 border rounded-full px-4 py-2 text-sm"
          placeholder="Paste Jira story or ask for changes..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />

        <button onClick={handleSubmit} className="bg-red-600 text-white px-5 py-2 rounded-full">
          Send
        </button>

        <button onClick={handleViewJiraStories} className="bg-red-600 text-white px-4 py-2 rounded-full">
          View Jira Stories
        </button>
      </div>
    </div>
  );
}