const fs = require('fs');
const path = require('path');

function loadDetectors() {
  const dir = path.join(__dirname, 'detectors');
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.js'))
    .map(f => {
      try {
        return require(path.join(dir, f));
      } catch (err) {
        // ignore faulty detector
        return null;
      }
    })
    .filter(Boolean);
}

async function scan(content) {
  const detectors = loadDetectors();
  const grouped = {};
  const all = [];

  for (const d of detectors) {
    const name = d.name || (d.constructor && d.constructor.name) || 'detector';
    grouped[name] = [];
    try {
      const res = await Promise.resolve(d.run(content));
      if (!res || !Array.isArray(res)) continue;
      for (const r of res) {
        const item = Object.assign({}, r, { detector: name, severity: r.severity || d.severity || 'info' });
        grouped[name].push(item);
        all.push(item);
      }
    } catch (err) {
      // ignore detector errors
    }
  }

  return { grouped, all };
}

module.exports = { scan };
