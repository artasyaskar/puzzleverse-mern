import crypto from 'crypto'
export default function requestId() {
  return (req, res, next) => {
    const incoming = String(req.headers['x-request-id'] || '').trim()
    const id = incoming && incoming.length > 0 ? incoming : crypto.randomUUID()
    req.id = id
    res.setHeader('X-Request-Id', id)
    next()
  }
}
