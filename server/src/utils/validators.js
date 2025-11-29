export function isNonEmptyString(v) {
  return typeof v === 'string' && v.trim().length > 0
}

export function isEmail(v) {
  if (typeof v !== 'string') return false
  return /.+@.+\..+/.test(v)
}

export function hasLettersAndNumbers(v) {
  if (typeof v !== 'string') return false
  return /[A-Za-z]/.test(v) && /\d/.test(v)
}

export function minLength(v, n) {
  return typeof v === 'string' && v.length >= n
}

export function validatePassword(pw) {
  return minLength(pw, 8) && hasLettersAndNumbers(pw)
}

export function collectErrors(obj) {
  return Object.entries(obj)
    .filter(([_, ok]) => !ok)
    .map(([k]) => k)
}

export function validateRegistration({ email, password }) {
  const checks = {
    email: isEmail(email),
    passwordPolicy: validatePassword(password)
  }
  const invalid = collectErrors(checks)
  return { ok: invalid.length === 0, invalid }
}
