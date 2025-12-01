import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import crypto from 'crypto'

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret'
const ACCESS_TTL_SEC = 5 * 60 // 5 minutes
const MAX_REFRESH_TOKENS = 5 // per-user cap

// In-memory stores
const users = [] // { id, email, emailLower, passwordHash, createdAt }
const refreshTokens = new Map() // token -> { userId, createdAt }
const userTokenQueue = new Map() // userId -> [tokens in issue order]

function nowISO() {
  return new Date().toISOString()
}

function validateEmail(email) {
  return /.+@.+\..+/.test(email)
}

function validatePassword(pw) {
  if (typeof pw !== 'string' || pw.length < 8) return false
  const hasLetter = /[A-Za-z]/.test(pw)
  const hasNumber = /\d/.test(pw)
  return hasLetter && hasNumber
}

export function findUserByEmailLower(emailLower) {
  return users.find(u => u.emailLower === emailLower)
}

export async function registerUser(email, password) {
  if (!validateEmail(email)) {
    const err = new Error('Invalid email format')
    err.code = 400
    throw err
  }
  if (!validatePassword(password)) {
    const err = new Error('Password must be at least 8 characters and include letters and numbers')
    err.code = 400
    throw err
  }
  const emailLower = email.toLowerCase()
  if (findUserByEmailLower(emailLower)) {
    const err = new Error('Email already registered')
    err.code = 400
    throw err
  }
  const id = crypto.randomUUID()
  const passwordHash = await bcrypt.hash(password, 10)
  const user = { id, email, emailLower, passwordHash, createdAt: nowISO() }
  users.push(user)
  return { id: user.id, email: user.email }
}

function signAccessToken(user) {
  const payload = { sub: user.id, email: user.email }
  return jwt.sign(payload, JWT_SECRET, { algorithm: 'HS256', expiresIn: ACCESS_TTL_SEC })
}

function issueRefreshToken(userId) {
  const token = crypto.randomBytes(32).toString('hex')
  refreshTokens.set(token, { userId, createdAt: Date.now() })
  const queue = userTokenQueue.get(userId) || []
  queue.push(token)
  while (queue.length > MAX_REFRESH_TOKENS) {
    const oldest = queue.shift()
    if (oldest) refreshTokens.delete(oldest)
  }
  userTokenQueue.set(userId, queue)
  return token
}

export async function loginUser(email, password) {
  const user = findUserByEmailLower(String(email || '').toLowerCase())
  if (!user) {
    const err = new Error('Invalid credentials')
    err.code = 401
    throw err
  }
  const ok = await bcrypt.compare(password, user.passwordHash)
  if (!ok) {
    const err = new Error('Invalid credentials')
    err.code = 401
    throw err
  }
  const accessToken = signAccessToken(user)
  const refreshToken = issueRefreshToken(user.id)
  return { accessToken, refreshToken, user: { id: user.id, email: user.email } }
}

export function verifyAccessToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET)
  } catch (e) {
    const err = new Error('Invalid or expired token')
    err.code = 401
    throw err
  }
}

export function refreshAccess(oldRefreshToken) {
  const entry = refreshTokens.get(oldRefreshToken)
  if (!entry) {
    const err = new Error('Invalid refresh token')
    err.code = 401
    throw err
  }
  // rotate: invalidate old, issue new
  refreshTokens.delete(oldRefreshToken)
  const q = userTokenQueue.get(entry.userId)
  if (q) {
    const idx = q.indexOf(oldRefreshToken)
    if (idx !== -1) q.splice(idx, 1)
    userTokenQueue.set(entry.userId, q)
  }
  const user = users.find(u => u.id === entry.userId)
  if (!user) {
    const err = new Error('User not found')
    err.code = 401
    throw err
  }
  const accessToken = signAccessToken(user)
  const refreshToken = issueRefreshToken(user.id)
  return { accessToken, refreshToken, userId: user.id }
}

export function revokeRefresh(refreshToken) {
  const entry = refreshTokens.get(refreshToken)
  refreshTokens.delete(refreshToken)
  if (entry) {
    const q = userTokenQueue.get(entry.userId)
    if (q) {
      const idx = q.indexOf(refreshToken)
      if (idx !== -1) q.splice(idx, 1)
      userTokenQueue.set(entry.userId, q)
    }
  }
}

export function getOutstandingRefreshCount(userId) {
  const q = userTokenQueue.get(userId) || []
  return q.length
}

export function requireAuth(req, res, next) {
  const hdr = req.headers['authorization'] || ''
  const [scheme, token] = hdr.split(' ')
  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header' })
  }
  try {
    const payload = verifyAccessToken(token)
    req.user = { id: payload.sub, email: payload.email }
    return next()
  } catch (e) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }
}
