import axios from "axios";

const BASE_URL = "http://localhost:8080";

// ---------- RULE APIs ----------
export const getRules = () => axios.get(`${BASE_URL}/rules`);
export const createRule = (data) => axios.post(`${BASE_URL}/rules`, data);
export const updateRule = (id, data) => axios.put(`${BASE_URL}/rules/${id}`, data);
export const deleteRule = (id) => axios.delete(`${BASE_URL}/rules/${id}`);

// ---------- OSARI APIs ----------
export const getOsari = () => axios.get(`${BASE_URL}/osari/`);
export const createOsari = (data) => axios.post(`${BASE_URL}/osari/`, data);
export const updateOsari = (id, data) => axios.put(`${BASE_URL}/osari/${id}`, data);

// ---------- CORE LINKING FUNCTION ----------
export const getRuleWithMappings = async () => {
  const [rulesRes, osariRes] = await Promise.all([
    getRules(),
    getOsari()
  ]);

  const rules = rulesRes.data;
  const mappings = osariRes.data;

  // 🔥 JOIN RULE + OSARI USING OID
  return rules.map(rule => ({
    ...rule,
    resolvedConditions: rule.conditions.map(c => {
      const mapping = mappings.find(m => m.objectId === c.oid);
      return {
        ...c,
        path: mapping?.path || null,
        entity: mapping?.entity || null
      };
    })
  }));
};