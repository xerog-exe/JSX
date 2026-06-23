module.exports = {
  name: 'Emails',
  severity: 'low',
  run(content) {
    const re = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;
    const seen = new Set();
    const out = [];
    let m;
    while ((m = re.exec(content)) !== null) {
      const val = m[0];
      if (seen.has(val)) continue;
      seen.add(val);
      const idx = m.index;
      const context = content.substr(Math.max(0, idx - 40), Math.min(120, val.length + 80)).replace(/\n/g, ' ');
      out.push({ value: val, context });
    }
    return out;
  }
};
