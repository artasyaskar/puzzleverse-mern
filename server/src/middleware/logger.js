export default function logger() {
  return async (req, res, next) => {
    const start = Date.now()
    const id = req.id || '-'
    const { method, url } = req
    res.on('finish', () => {
      const ms = Date.now() - start
      const status = res.statusCode
      // minimal structured log line without external deps
      process.stdout.write(`${id} ${method} ${url} ${status} ${ms}ms\n`)
    })
    next()
  }
}
