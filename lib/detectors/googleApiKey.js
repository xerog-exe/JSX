module.exports = {
  name: 'Google API Keys',
  severity: 'high',
  run(content) {
    const re = /AIza[0-9A-Za-z\-_]{35}/g;
    const seen = new Set();
    const out = [];
    let m;
    while ((m = re.exec(content)) !== null) {
      const val = m[0];
      if (seen.has(val)) continue;
      seen.add(val);
      const idx = m.index;
      const context = content.substr(Math.max(0, idx - 40), Math.min(120, val.length + 80)).replace(/\n/g, ' ');
      out.push({ value: val, context, severity: 'high' });
    }
    return out;
  }
};
