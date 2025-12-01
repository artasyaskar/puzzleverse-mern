export default function errorHandler() {
  return (err, req, res, next) => {
    const status = err.status || err.code || 500
    const message = err.message || 'Internal Server Error'
    try {
      res.status(status).json({ error: message, requestId: req.id })
    } catch {
      res.status(500).end()
    }
  }
}
