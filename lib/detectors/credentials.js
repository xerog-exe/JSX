module.exports = {
  name: 'Hardcoded Credentials',
  severity: 'high',
  run(content) {
    const out = [];
    const re = /(?:password|passwd|pwd|secret|client_secret|api_secret)\s*[:=]\s*["']([^"']{4,200})["']/ig;
    let m;
    const seen = new Set();
    while ((m = re.exec(content)) !== null) {
      const val = m[1];
      if (seen.has(val)) continue;
      seen.add(val);
      const idx = m.index;
      const context = content.substr(Math.max(0, idx - 40), 120).replace(/\n/g, ' ');
      out.push({ value: val, context, severity: 'high' });
    }
    return out;
  }
};
