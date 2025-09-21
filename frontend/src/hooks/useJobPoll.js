
export function useJobPoll(apiBase, jobId, onUpdate) {
  let interval = null;
  async function tick() {
    try {
      const res = await fetch(`${apiBase}/jobs/${jobId}`);
      const json = await res.json();
      onUpdate(json);
      if (json.status === 'done' || json.status === 'error') {
        clear();
      }
    } catch (e) {
      console.error(e);
    }
  }
  function start() {
    if (interval) clearInterval(interval);
    interval = setInterval(tick, 1500);
    tick();
  }
  function clear() {
    if (interval) clearInterval(interval);
    interval = null;
  }
  return { start, clear };
}
