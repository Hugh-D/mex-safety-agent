/* MEX Safety Agent — Session state manager */
const State = (() => {
  const KEYS = {
    PARSE_RESULT:   'mex_parse_result',
    REVIEW_PAYLOAD: 'mex_review_payload',
    REVIEW_RESULT:  'mex_review_result',
  };

  function get(key) {
    try {
      const raw = sessionStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }

  function set(key, val) {
    try { sessionStorage.setItem(key, JSON.stringify(val)); } catch(e) { console.warn('State.set failed', e); }
  }

  function remove(key) { sessionStorage.removeItem(key); }

  function clear() { Object.values(KEYS).forEach(k => sessionStorage.removeItem(k)); }

  return { KEYS, get, set, remove, clear };
})();
