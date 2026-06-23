module.exports = {
  name: 'Authorization Tokens',
  severity: 'high',
  run(content) {
    const out = [];
    const bearerRe = /Bearer\s+([A-Za-z0-9\-_.=\/]+)/g;
    const authRe = /authorization\s*["']?\s*[:=]\s*["']([^"']{8,200})["']/i;
    let m;
    const seen = new Set();
    while ((m = bearerRe.exec(content)) !== null) {
      const val = m[0];
      if (seen.has(val)) continue;
      seen.add(val);
      const idx = m.index;
      const context = content.substr(Math.max(0, idx - 40), 120).replace(/\n/g, ' ');
      out.push({ value: val, context, severity: 'high' });
    }

    const m2 = authRe.exec(content);
    if (m2 && !seen.has(m2[0])) {
      out.push({ value: m2[1], context: content.substr(Math.max(0, m2.index - 40), 120).replace(/\n/g, ' '), severity: 'high' });
    }

    return out;
  }
};
