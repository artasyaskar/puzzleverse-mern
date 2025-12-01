// Fixed-window limiter keyed by IP+email that counts only failed login attempts.
const store = new Map(); // scopeKey -> { count, resetAt }

export function makeLoginRateLimiter({ windowMs = 60000, max = 5 } = {}) {
  return (req, res, next) => {
    const now = Date.now();
    const ip = req.ip || req.headers['x-forwarded-for'] || req.connection?.remoteAddress || 'unknown';
    const email = (req.body && typeof req.body.email === 'string') ? req.body.email.toLowerCase() : '';
    const scopeKey = `${ip}|${email}`;

    let entry = store.get(scopeKey);
    if (!entry || now >= entry.resetAt) {
      entry = { count: 0, resetAt: now + windowMs };
      store.set(scopeKey, entry);
    }

    req.rateLimitMax = max;
    req.getLoginFailures = () => entry.count;
    req.getRetryAfterSeconds = () => {
      const remainingMs = Math.max(0, (store.get(scopeKey)?.resetAt || 0) - Date.now());
      const secs = Math.ceil(remainingMs / 1000);
      return Math.max(1, secs || 0);
    };
    req.recordLoginFailure = () => {
      const now2 = Date.now();
      let ent = store.get(scopeKey);
      if (!ent || now2 >= ent.resetAt) {
        ent = { count: 0, resetAt: now2 + windowMs };
        store.set(scopeKey, ent);
      }
      ent.count += 1;
    };
    req.resetLoginFailures = () => {
      const ent = store.get(scopeKey);
      if (ent) ent.count = 0;
    };

    return next();
  };
}
