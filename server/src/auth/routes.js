import express from 'express'
import { makeLoginRateLimiter } from '../middleware/rateLimit.js'
import { registerUser, loginUser, refreshAccess, revokeRefresh, requireAuth } from './service.js'

const router = express.Router()
const loginLimiter = makeLoginRateLimiter({ windowMs: 60000, max: 5 })

router.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body || {}
    const user = await registerUser(String(email || ''), String(password || ''))
    return res.status(201).json(user)
  } catch (e) {
    const code = e.code || 400
    return res.status(code).json({ error: e.message || 'Invalid request' })
  }
})

router.post('/login', loginLimiter, async (req, res) => {
  try {
    const { email, password } = req.body || {}
    const result = await loginUser(String(email || ''), String(password || ''))
    if (req.resetLoginFailures) req.resetLoginFailures()
    return res.json(result)
  } catch (e) {
    if (req.recordLoginFailure) req.recordLoginFailure()
    const fails = req.getLoginFailures ? req.getLoginFailures() : 0
    const isRateLimited = fails >= (req.rateLimitMax || 5)
    const code = isRateLimited ? 429 : (e.code || 401)
    const message = isRateLimited
      ? 'Too many login attempts. Please try again later.'
      : (e.message || 'Invalid credentials')
    return res.status(code).json({ error: message })
  }
})

router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body || {}
    const result = refreshAccess(String(refreshToken || ''))
    return res.json(result)
  } catch (e) {
    const code = e.code || 401
    return res.status(code).json({ error: e.message || 'Invalid refresh token' })
  }
})

router.post('/logout', async (req, res) => {
  const { refreshToken } = req.body || {}
  revokeRefresh(String(refreshToken || ''))
  return res.status(200).json({ ok: true })
})

router.get('/me', requireAuth, (req, res) => {
  return res.json({ id: req.user.id, email: req.user.email })
})

export default router
