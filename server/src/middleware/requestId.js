import crypto from 'crypto'
export default function requestId() {
  return (req, res, next) => {
    const id = crypto.randomUUID()
    req.id = id
    res.setHeader('X-Request-Id', id)
    next()
  }
}
