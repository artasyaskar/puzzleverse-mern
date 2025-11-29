import express from 'express'
import { rateLimit } from '../middleware/rateLimit.js'
import { registerUser, loginUser, refreshAccess, revokeRefresh, requireAuth } from './service.js'

const router = express.Router()

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

router.post('/login', rateLimit({ windowMs: 60000, max: 5 }), async (req, res) => {
  try {
    const { email, password } = req.body || {}
    const result = await loginUser(String(email || ''), String(password || ''))
    return res.json(result)
  } catch (e) {
    const code = e.code || 401
    return res.status(code).json({ error: e.message || 'Invalid credentials' })
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
