import { useState, useEffect } from "react";
import axios from "axios";
import { Copy, Edit3 } from "lucide-react";

const defaultMapping = {
  objectId: "",
  objectName: "",
  pathType: "",
  auto: false,
  cmp: false,
  umb: false,
  wc: false,
  context: "",
  effectiveVersion: "",
  expiryVersion: "",
  entity: "",
  attribute: "",
  path: "",
  pathNotes: "",
  lastUpdated: "",
  stereotype: false
};

export default function OsariMapping() {
  const [mappings, setMappings] = useState([]);
  const [form, setForm] = useState(defaultMapping);
  const [showDrawer, setShowDrawer] = useState(false);
  const [editId, setEditId] = useState(null);

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("");

  useEffect(() => {
    fetchMappings();
  }, []);

  const fetchMappings = async () => {
    const res = await axios.get("http://localhost:8080/osari/");
    setMappings(res.data);
  };

  const handleSave = async () => {
    if (!form.objectId || !form.objectName) {
      return alert("Object ID & Name required");
    }

    if (editId) {
      await axios.put(`http://localhost:8080/osari/${editId}`, form);
    } else {
      await axios.post("http://localhost:8080/osari/", form);
    }

    setShowDrawer(false);
    setForm(defaultMapping);
    setEditId(null);
    fetchMappings();
  };

  const handleEdit = (m) => {
    setForm(m);
    setEditId(m.id);
    setShowDrawer(true);
  };

  // 🔥 FILTER LOGIC
  const filteredMappings = mappings.filter((m) => {
    const s = search.toLowerCase();

    const workstreams = [];
    if (m.wc) workstreams.push("wc");
    if (m.auto) workstreams.push("auto");

    const matchesSearch =
      (m.objectId || "").toLowerCase().includes(s) ||
      (m.objectName || "").toLowerCase().includes(s) ||
      (m.attribute || "").toLowerCase().includes(s) ||
      (m.entity || "").toLowerCase().includes(s) ||
      workstreams.join(" ").includes(s);

    const matchesFilter =
      !filter ||
      (filter === "wc" && m.wc) ||
      (filter === "auto" && m.auto);

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-4">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold text-gray-800">
          OSARI Mappings
        </h2>

        <button
          className="btn"
          onClick={() => {
            setForm(defaultMapping);
            setEditId(null);
            setShowDrawer(true);
          }}
        >
          + Add Mapping
        </button>
      </div>

      {/* 🔥 SEARCH + FILTER */}
      <div className="bg-white p-4 rounded-3xl border border-gray-200 shadow-sm flex flex-col gap-4 md:flex-row md:items-center">
        <div className="flex-1 min-w-0">
          <input
            className="input w-full border-gray-300 shadow-sm"
            placeholder="Search by OID, attribute name, or workstream..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex gap-3 flex-wrap items-center">
          <select
            className="input w-[180px] border-gray-300 shadow-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">All Workstreams</option>
            <option value="wc">WC</option>
            <option value="auto">Auto</option>
          </select>
        </div>
      </div>

      {/* TABLE */}
      <div className="bg-white rounded-2xl shadow border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-[1800px] w-full text-sm border-collapse">

            <thead className="bg-red-600 text-white">
              <tr>
                <th className="p-2 text-left align-top whitespace-nowrap">Object ID</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Name</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Path Type</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Auto</th>
                <th className="p-2 text-left align-top whitespace-nowrap">CMP</th>
                <th className="p-2 text-left align-top whitespace-nowrap">UMB</th>
                <th className="p-2 text-left align-top whitespace-nowrap">WC</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Context</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Entity</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Attribute</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Effective Version</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Expiry Version</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Path Notes</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Last Updated</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Stereotype</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Path</th>
                <th className="p-2 text-left align-top whitespace-nowrap">Actions</th>
              </tr>
            </thead>

            <tbody>
              {filteredMappings.map((m) => (
                <tr key={m.id} className="border-b hover:bg-gray-50 align-top whitespace-nowrap">
                  <td className="p-2 align-top whitespace-nowrap">{m.objectId}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.objectName}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.pathType}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.auto ? "Y" : "N"}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.cmp ? "Y" : "N"}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.umb ? "Y" : "N"}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.wc ? "Y" : "N"}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.context}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.entity}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.attribute}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.effectiveVersion}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.expiryVersion}</td>
                  <td className="p-2 align-top max-w-[250px] truncate whitespace-nowrap">{m.pathNotes}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.lastUpdated}</td>
                  <td className="p-2 align-top whitespace-nowrap">{m.stereotype ? "Y" : "N"}</td>
                  <td className="p-2 align-top max-w-[300px] truncate whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="truncate">{m.path}</span>
                      <button
                        className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200"
                        onClick={() => {
                          navigator.clipboard.writeText(m.path);
                          alert("Copied!");
                        }}
                        aria-label="Copy path"
                      >
                        <Copy className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </td>
                  <td className="p-2 align-top whitespace-nowrap">
                    <button
                      className="p-2 rounded-lg bg-red-50 text-red-600 hover:bg-red-100"
                      onClick={() => handleEdit(m)}
                      aria-label="Edit mapping"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>

          </table>
        </div>

        {/* FORM MODAL */}
        {showDrawer && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">

            <div className="w-full max-w-[900px] bg-white rounded-2xl p-6 shadow-xl max-h-[85vh] overflow-y-auto">

              <h3 className="text-lg font-semibold mb-4">
                {editId ? "Edit Mapping" : "Add Mapping"}
              </h3>

              <div className="space-y-2">
                {Object.entries(defaultMapping).map(([key]) => {
                  if (["auto", "cmp", "umb", "wc", "stereotype"].includes(key)) {
                    return (
                      <label key={key} className="flex items-center gap-2 mb-2">
                        <input
                          type="checkbox"
                          checked={form[key]}
                          onChange={(e) =>
                            setForm({ ...form, [key]: e.target.checked })
                          }
                        />
                        {key.toUpperCase()}
                      </label>
                    );
                  }

                  if (key === "path" || key === "pathNotes") {
                    return (
                      <textarea
                        key={key}
                        className="input mb-2"
                        placeholder={key}
                        value={form[key] || ""}
                        onChange={(e) =>
                          setForm({ ...form, [key]: e.target.value })
                        }
                      />
                    );
                  }

                  if (key === "lastUpdated") {
                    return (
                      <input
                        key={key}
                        type="datetime-local"
                        className="input mb-2"
                        value={form[key] || ""}
                        onChange={(e) =>
                          setForm({ ...form, [key]: e.target.value })
                        }
                      />
                    );
                  }

                  return (
                    <input
                      key={key}
                      className="input mb-2"
                      placeholder={key}
                      value={form[key] || ""}
                      onChange={(e) =>
                        setForm({ ...form, [key]: e.target.value })
                      }
                    />
                  );
                })}
              </div>

              <div className="flex justify-end space-x-3 mb-2">
                <button className="btn bg-green-600" onClick={handleSave}>
                  Save
                </button>
                <button
                  className="btn bg-gray-400"
                  onClick={() => setShowDrawer(false)}
                >
                  Cancel
                </button>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}