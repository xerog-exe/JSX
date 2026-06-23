module.exports = {
  name: 'IP Addresses',
  severity: 'low',
  run(content) {
    const re = /\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3})\b/g;
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
