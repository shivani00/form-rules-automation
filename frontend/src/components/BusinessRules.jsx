import React, { useState, useEffect } from "react";
import axios from "axios";

const STATES = [
  { stateCd: "MI", stateName: "Michigan" },
  { stateCd: "RI", stateName: "Rhode Island" },
  { stateCd: "NY", stateName: "New York" },
  { stateCd: "CA", stateName: "California" },
  { stateCd: "TX", stateName: "Texas" }
];

const defaultForm = {
  ruleType: "",
  workstream: "",
  businessUnit: "",
  rollupGroups: "",
  subGroups: "",
  productType: "",
  states: [],
  stateType: "",
  transactions: "",
  user: "",
  effectiveIRID: "",
  implementation: "",
  effectiveDate: "",
  expirationIRID: "",
  implementationDate: "",
  expirationDate: "",
  conditions: [{ attributeName: "", oid: "", value: "" }],
  thenActions: [{ action: "", value: "" }],
  form: {
    objectName: "",
    formTitle: "",
    formShortName: "",
    formType: "",
    workstream: "",
    printHandlingTypeCode: "",
    reprintOnChange: "",
    policyTab: "",
    pullListIndicator: "",
    singleTermForm: "",
    toBeRationalizedDate: "",
    rationalizedDate: "",
    rationalizationPriority: "",
    fillInAttribute: "",
    notes: "",
    expired: "",
    requestor: "",
    requestDate: ""
  }
};

export default function BusinessRules() {
  const [rules, setRules] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(defaultForm);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [editIndex, setEditIndex] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const res = await axios.get("http://localhost:8080/rules");
      setRules(res.data);
    } catch {
      setRules([]);
    }
  };

  const handleEdit = (rule, index) => {

    const merged = {
      ...defaultForm,
      ...rule,

      states: rule.states || [],

      conditions: rule.conditions?.length
        ? rule.conditions
        : [{ attributeName: "", oid: "", value: "" }],

      thenActions: rule.thenActions?.length
        ? rule.thenActions
        : [{ action: "", value: "" }],

      form: {
        ...defaultForm.form,
        ...(rule.form || {})
      }
    };

    setForm(merged);
    setEditIndex(index);
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.ruleType) return alert("Rule Type required");
    for (let c of form.conditions) {
      if (!c.oid) return alert("OID required");
    }

    if (editIndex !== null) {
      await axios.put(`http://localhost:8080/rules/${form.id}`, form);
    } else {
      await axios.post("http://localhost:8080/rules", form);
    }
    fetchRules();
    setShowModal(false);
    setForm(defaultForm);
    setEditIndex(null);
  };

  // ---------- STATE ----------
  const addState = (e) => {
    const val = e.target.value;
    if (!val) return;
    const selected = STATES.find(s => s.stateCd === val);

    if (!form.states.find(s => s.stateCd === val)) {
      setForm({ ...form, states: [...form.states, selected] });
    }
  };

  const removeState = (code) => {
    setForm({
      ...form,
      states: form.states.filter(s => s.stateCd !== code)
    });
  };

  const [filters, setFilters] = useState({
    search: "",
    workstream: "",
    formType: ""
  });

  const filteredRules = rules.filter(r => {
    const search = filters.search.toLowerCase();

    const matchesSearch =
      r.ruleType?.toLowerCase().includes(search) ||
      r.form?.objectName?.toLowerCase().includes(search);

    const matchesWorkstream =
      !filters.workstream ||
      r.workstream?.toLowerCase() === filters.workstream.toLowerCase();

    const matchesFormType =
      !filters.formType ||
      r.form?.formType?.toLowerCase() === filters.formType.toLowerCase();

    return matchesSearch && matchesWorkstream && matchesFormType;
  });

  // ---------- CONDITIONS ----------
  const addCondition = () => {
    setForm({
      ...form,
      conditions: [...form.conditions, { attributeName: "", oid: "", value: "" }]
    });
  };

  const removeCondition = (i) => {
    setForm({
      ...form,
      conditions: form.conditions.filter((_, idx) => idx !== i)
    });
  };

  // ---------- THEN ----------
  const addThen = () => {
    setForm({
      ...form,
      thenActions: [...form.thenActions, { action: "", value: "" }]
    });
  };

  const removeThen = (i) => {
    setForm({
      ...form,
      thenActions: form.thenActions.filter((_, idx) => idx !== i)
    });
  };

  return (
    <div className="card">

      <div className="flex justify-between mb-4">
        <h2 className="text-xl text-red-600 font-bold">Business Rules</h2>
        <button className="btn" onClick={() => setShowModal(true)}>+ Add Rule</button>
      </div>

      {rules.length === 0 && (
        <div className="text-center text-gray-500">No rules to display</div>
      )}

      <div className="bg-gray-50 p-4 rounded-xl border mb-4">
        <div className="grid grid-cols-3 gap-3">

          {/* SEARCH */}
          <input
            className="input"
            placeholder="Search by Rule or Form Number..."
            value={filters.search}
            onChange={(e) =>
              setFilters({ ...filters, search: e.target.value })
            }
          />

          {/* WORKSTREAM */}
          <select
            className="input"
            onChange={(e) =>
              setFilters({ ...filters, workstream: e.target.value })
            }
          >
            <option value="">All Workstreams</option>
            <option value="wc">WC</option>
            <option value="auto">Auto</option>
          </select>

          {/* FORM TYPE */}
          <select
            className="input"
            value={filters.formType}
            onChange={(e) =>
              setFilters({ ...filters, formType: e.target.value })
            }
          >
            <option value="">All Form Types</option>
            <option value="text">Text</option>
            <option value="fillin">Fill-In</option>
          </select>

        </div>
      </div>

      <div className="overflow-x-auto">

        <table className="w-full text-sm border rounded-xl overflow-hidden">

          {/* HEADER */}
          <thead className="bg-red-600 text-white">
            <tr>
              <th className="p-3 text-left">Rule Type</th>
              <th className="p-3 text-left">Form Number</th>
              <th className="p-3 text-left">Form Title</th>
              <th className="p-3 text-left">Short Name</th>
              <th className="p-3 text-left">Form Type</th>
              <th className="p-3 text-left">Workstream</th>
              <th className="p-3 text-left">Business Unit</th>
            </tr>
          </thead>

          {/* BODY */}
          <tbody>

            {filteredRules.map((r, i) => (
              <React.Fragment key={i}>

                {/* COLLAPSED ROW */}
                <tr
                  className="border-b cursor-pointer hover:bg-red-50"
                  onClick={() => setExpandedIndex(expandedIndex === i ? null : i)}
                >
                  <td className="p-3 font-semibold text-red-600">{r.ruleType}</td>
                  <td className="p-3">{r.form?.objectName}</td>
                  <td className="p-3">{r.form?.formTitle}</td>
                  <td className="p-3">{r.form?.formShortName}</td>
                  <td className="p-3">{r.form?.formType || "-"}</td>
                  <td className="p-3">{r.workstream}</td>
                  <td className="p-3">{r.businessUnit}</td>
                </tr>

                {/* EXPANDED ROW */}
                {expandedIndex === i && (
                  <tr>
                    <td colSpan="7" className="p-4 bg-gray-50">

                      <div className="space-y-5 text-sm">

                        {/* 🔗 JIRA */}
                        {r.jira_url && (
                          <div>
                            🔗 <a href={r.jira_url} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                              View Jira Story
                            </a>
                          </div>
                        )}

                        {/* 📌 RULE DETAILS */}
                        <div>
                          <div className="font-semibold mb-2 text-gray-700">Rule Details</div>
                          <div className="grid grid-cols-3 gap-3 bg-white p-3 rounded border">
                            <div><b>Workstream:</b> {r.workstream}</div>
                            <div><b>Business Unit:</b> {r.businessUnit}</div>
                            <div><b>Product Type:</b> {r.productType}</div>
                            <div><b>User:</b> {r.user}</div>
                            <div><b>State Type:</b> {r.stateType}</div>
                            <div><b>Rollup Groups:</b> {r.rollupGroups}</div>
                            <div><b>Sub Groups:</b> {r.subGroups}</div>
                          </div>
                        </div>

                        {/* 📍 STATES */}
                        <div>
                          <div className="font-semibold mb-1 text-gray-700">States</div>
                          <div className="bg-white p-3 rounded border">
                            {r.states?.map(s => `${s.stateCd} (${s.stateName})`).join(", ")}
                          </div>
                        </div>

                        {/* 🔁 TRANSACTIONS */}
                        <div>
                          <div className="font-semibold mb-1 text-gray-700">Transactions</div>
                          <div className="bg-white p-3 rounded border">
                            {r.transactions}
                          </div>
                        </div>

                        {/* 📅 DATES */}
                        <div>
                          <div className="font-semibold mb-2 text-gray-700">Dates</div>
                          <div className="grid grid-cols-3 gap-3 bg-white p-3 rounded border">
                            <div><b>Effective IRID:</b> {r.effectiveIRID}</div>
                            <div><b>Effective Date:</b> {r.effectiveDate}</div>
                            <div><b>Implementation:</b> {r.implementation}</div>
                            <div><b>Expiration IRID:</b> {r.expirationIRID}</div>
                            <div><b>Expiration Date:</b> {r.expirationDate}</div>
                            <div><b>Implementation Date:</b> {r.implementationDate}</div>
                          </div>
                        </div>

                        {/* 🔍 CONDITIONS */}
                        <div>
                          <div className="font-semibold mb-1 text-gray-700">Conditions</div>
                          <div className="space-y-1">
                            {r.conditions?.map((c, idx) => (
                              <div key={idx} className="bg-white p-2 border rounded">
                                {c.attributeName} ({c.oid}) = {c.value}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* ⚡ ACTIONS */}
                        <div>
                          <div className="font-semibold mb-1 text-gray-700">Actions</div>
                          <div className="space-y-1">
                            {r.thenActions?.map((t, idx) => (
                              <div key={idx} className="bg-white p-2 border rounded">
                                {t.action} → {t.value}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* 📄 FORM DETAILS */}
                        <div>
                          <div className="font-semibold mb-2 text-gray-700">Form Details</div>
                          <div className="grid grid-cols-3 gap-3 bg-white p-3 rounded border">

                            <div><b>Form Number:</b> {r.form?.objectName}</div>
                            <div><b>Title:</b> {r.form?.formTitle}</div>
                            <div><b>Short Name:</b> {r.form?.formShortName}</div>

                            <div><b>Form Type:</b> {r.form?.formType}</div>
                            <div><b>Print Handling:</b> {r.form?.printHandlingTypeCode}</div>
                            <div><b>Reprint:</b> {r.form?.reprintOnChange}</div>

                            <div><b>Policy Tab:</b> {r.form?.policyTab}</div>
                            <div><b>Pull List:</b> {r.form?.pullListIndicator}</div>
                            <div><b>Single Term:</b> {r.form?.singleTermForm}</div>

                            <div><b>Rationalize Date:</b> {r.form?.toBeRationalizedDate}</div>
                            <div><b>Rationalized:</b> {r.form?.rationalizedDate}</div>
                            <div><b>Priority:</b> {r.form?.rationalizationPriority}</div>

                            <div><b>Fill Attribute:</b> {r.form?.fillInAttribute}</div>
                            <div><b>Notes:</b> {r.form?.notes}</div>
                            <div><b>Expired:</b> {r.form?.expired}</div>

                            <div><b>Requestor:</b> {r.form?.requestor}</div>
                            <div><b>Request Date:</b> {r.form?.requestDate}</div>

                          </div>
                        </div>

                        <button className="btn mt-2" onClick={() => handleEdit(r, i)}>
                          Edit Rule
                        </button>

                      </div>

                    </td>
                  </tr>
                )}

              </React.Fragment>
            ))}

          </tbody>
        </table>
      </div>

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center">
          <div className="bg-white p-6 rounded-xl w-[1000px] max-h-[90vh] overflow-auto">

            <table className="w-full border text-sm">

              <tbody>

                <tr>
                  <td>Rule Type</td>
                  <td><input className="input" value={form.ruleType} onChange={e => setForm({ ...form, ruleType: e.target.value })} /></td>
                </tr>

                <tr><td colSpan="2" className="bg-gray-100 font-bold">For</td></tr>

                <tr>
                  <td>Workstream</td>
                  <td>
                    <select
                      className="input"
                      value={form.workstream}
                      onChange={e => setForm({ ...form, workstream: e.target.value })}
                    >
                      <option value="">Select Workstream</option>
                      <option value="wc">WC</option>
                      <option value="auto">Auto</option>
                    </select>
                  </td>
                </tr>
                <tr><td>Business Unit</td><td><input className="input" value={form.businessUnit} onChange={e => setForm({ ...form, businessUnit: e.target.value })} /></td></tr>
                <tr><td>Rollup Groups</td><td><input className="input" value={form.rollupGroups} onChange={e => setForm({ ...form, rollupGroups: e.target.value })} /></td></tr>
                <tr><td>Sub Groups</td><td><input className="input" value={form.subGroups} onChange={e => setForm({ ...form, subGroups: e.target.value })} /></td></tr>
                <tr><td>Product Type</td><td><input className="input" value={form.productType} onChange={e => setForm({ ...form, productType: e.target.value })} /></td></tr>

                {/* STATES */}
                <tr>
                  <td>States</td>
                  <td>
                    <select className="input" value={form.states.map(s => s.stateCd).join(',')} onChange={addState}>
                      <option value="">Select</option>
                      {STATES.map(s => (
                        <option key={s.stateCd} value={s.stateCd}>
                          {s.stateCd} - {s.stateName}
                        </option>
                      ))}
                    </select>

                    <div className="mt-2 flex gap-2 flex-wrap">
                      {form.states.map(s => (
                        <span key={s.stateCd} className="bg-red-100 px-2 py-1 rounded flex items-center gap-2">
                          {s.stateCd}
                          <button onClick={() => removeState(s.stateCd)}>x</button>
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>

                <tr><td>State Type</td><td><input className="input" value={form.stateType} onChange={e => setForm({ ...form, stateType: e.target.value })} /></td></tr>
                <tr><td>Transaction</td><td><input className="input" value={form.transactions} onChange={e => setForm({ ...form, transactions: e.target.value })} /></td></tr>
                <tr><td>User</td><td><input className="input" value={form.user} onChange={e => setForm({ ...form, user: e.target.value })} /></td></tr>

                {/* DATES */}
                <tr><td colSpan="2" className="bg-gray-100 font-bold">Dates</td></tr>

                <tr><td>Effective IRID</td><td><input className="input" value={form.effectiveIRID} onChange={e => setForm({ ...form, effectiveIRID: e.target.value })} /></td></tr>
                <tr><td>Implementation</td><td><input type="date" className="input" value={form.implementation} onChange={e => setForm({ ...form, implementation: e.target.value })} /></td></tr>
                <tr><td>Effective Date</td><td><input type="date" className="input" value={form.effectiveDate} onChange={e => setForm({ ...form, effectiveDate: e.target.value })} /></td></tr>
                <tr><td>Expiration IRID</td><td><input className="input" value={form.expirationIRID} onChange={e => setForm({ ...form, expirationIRID: e.target.value })} /></td></tr>
                <tr><td>Implementation Date</td><td><input type="date" className="input" value={form.implementationDate} onChange={e => setForm({ ...form, implementationDate: e.target.value })} /></td></tr>
                <tr><td>Expiration Date</td><td><input type="date" className="input" value={form.expirationDate} onChange={e => setForm({ ...form, expirationDate: e.target.value })} /></td></tr>

                {/* IF */}
                <tr>
                  <td colSpan="2" className="bg-gray-100 font-bold">
                    Conditions
                  </td>
                </tr>
                {form.conditions.map((c, i) => (
                  <tr key={i}>
                    <td colSpan="2">
                      <div className="grid grid-cols-[2fr_1fr_2fr_auto] gap-2 items-center">

                        <input
                          className="input"
                          placeholder="Attribute"
                          value={form.conditions[i]?.attributeName || ''}
                          onChange={e => {
                            const copy = [...form.conditions];
                            copy[i].attributeName = e.target.value;
                            setForm({ ...form, conditions: copy });
                          }}
                        />

                        <input
                          className="input"
                          placeholder="OID"
                          value={form.conditions[i]?.oid || ''}
                          onChange={e => {
                            const copy = [...form.conditions];
                            copy[i].oid = e.target.value;
                            setForm({ ...form, conditions: copy });
                          }}
                        />

                        <input
                          className="input"
                          placeholder="Value"
                          value={form.conditions[i]?.value || ''}
                          onChange={e => {
                            const copy = [...form.conditions];
                            copy[i].value = e.target.value;
                            setForm({ ...form, conditions: copy });
                          }}
                        />

                        <button
                          className="text-red-500 text-sm"
                          onClick={() => removeCondition(i)}
                        >
                          Remove
                        </button>

                      </div>
                    </td>
                  </tr>
                ))}
                <tr>
                  <td colSpan="2">
                    <button className="btn mt-2" onClick={addCondition}>
                      + Add Condition
                    </button>
                  </td>
                </tr>

                {/* THEN */}
                <tr>
                  <td colSpan="2" className="bg-gray-100 font-bold">
                    Actions
                  </td>
                </tr>
                {form.thenActions.map((t, i) => (
                  <tr key={i}>
                    <td colSpan="2">
                      <div className="grid grid-cols-[2fr_2fr_auto] gap-2 items-center">

                        <input
                          className="input"
                          placeholder="Action"
                          value={form.thenActions[i]?.action || ''}
                          onChange={e => {
                            const copy = [...form.thenActions];
                            copy[i].action = e.target.value;
                            setForm({ ...form, thenActions: copy });
                          }}
                        />

                        <input
                          className="input"
                          placeholder="Value"
                          value={form.thenActions[i]?.value || ''}
                          onChange={e => {
                            const copy = [...form.thenActions];
                            copy[i].value = e.target.value;
                            setForm({ ...form, thenActions: copy });
                          }}
                        />

                        <button
                          className="text-red-500 text-sm"
                          onClick={() => removeThen(i)}
                        >
                          Remove
                        </button>

                      </div>
                    </td>
                  </tr>
                ))}
                <tr>
                  <td colSpan="2">
                    <button className="btn mt-2" onClick={addThen}>
                      + Add Action
                    </button>
                  </td>
                </tr>

                {/* FORM */}
                <tr><td colSpan="2" className="bg-gray-100 font-bold">Form</td></tr>

                <tr><td>Form Name</td><td><input className="input" value={form.form.objectName} onChange={e => setForm({ ...form, form: { ...form.form, objectName: e.target.value } })} /></td></tr>
                <tr><td>Form Title</td><td><input className="input" value={form.form.formTitle} onChange={e => setForm({ ...form, form: { ...form.form, formTitle: e.target.value } })} /></td></tr>
                <tr><td>Form Short Name</td><td><input className="input" value={form.form.formShortName} onChange={e => setForm({ ...form, form: { ...form.form, formShortName: e.target.value } })} /></td></tr>
                <tr><td>Form Type</td><td><input className="input" value={form.form.formType} onChange={e => setForm({ ...form, form: { ...form.form, formType: e.target.value } })} /></td></tr>

                <tr>
                  <td>PrintHandling Type Code</td>
                  <td>
                    <input
                      className="input"
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, printHandlingTypeCode: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Reprint on Change</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.reprintOnChange}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, reprintOnChange: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Policy Tab</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.policyTab}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, policyTab: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Pull list Indicator</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.pullListIndicator}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, pullListIndicator: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Single Term Form</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.singleTermForm}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, singleTermForm: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>To be Rationalized Date</td>
                  <td>
                    <input
                      type="date"
                      className="input"
                      value={form.form.toBeRationalizedDate}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, toBeRationalizedDate: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Rationalized Date</td>
                  <td>
                    <input
                      type="date"
                      className="input"
                      value={form.form.rationalizedDate}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, rationalizedDate: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Rationalization Priority</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.rationalizationPriority}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, rationalizationPriority: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Fill-in Attribute</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.fillInAttribute}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, fillInAttribute: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Notes</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.notes}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, notes: e.target.value }
                      })}
                    />
                  </td>
                </tr>

                <tr>
                  <td>Expired</td>
                  <td>
                    <input
                      className="input"
                      value={form.form.expired}
                      onChange={e => setForm({
                        ...form,
                        form: { ...form.form, expired: e.target.value }
                      })}
                    />
                  </td>
                </tr>
                <tr><td>Requestor</td><td><input className="input" value={form.form.requestor} onChange={e => setForm({ ...form, form: { ...form.form, requestor: e.target.value } })} /></td></tr>
                <tr><td>Request Date</td><td><input type="date" className="input" value={form.form.requestDate} onChange={e => setForm({ ...form, form: { ...form.form, requestDate: e.target.value } })} /></td></tr>

              </tbody>
            </table>

            <div className="flex gap-2 mt-4">
              <button className="btn" onClick={handleSave}>Save</button>
              <button className="btn" onClick={() => setShowModal(false)}>Cancel</button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}