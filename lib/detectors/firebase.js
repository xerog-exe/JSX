module.exports = {
  name: 'Firebase Config',
  severity: 'high',
  run(content) {
    const out = [];
    // Look for typical firebase config object or apiKey
    const apiKeyRe = /apiKey\s*[:=]\s*["'](AIza[0-9A-Za-z\-_]{35})["']/i;
    const cfgRe = /firebase(?:Config)?\s*[:=]\s*\{([\s\S]{0,800}?)};/i;

    const m1 = apiKeyRe.exec(content);
    if (m1) {
      out.push({ value: m1[1], context: content.substr(Math.max(0, m1.index - 40), 120).replace(/\n/g, ' '), severity: 'high' });
    }

    const m2 = cfgRe.exec(content);
    if (m2) {
      const snippet = m2[0].replace(/\n/g, ' ');
      out.push({ value: 'firebaseConfig', context: snippet, severity: 'high' });
    }

    return out;
  }
};
