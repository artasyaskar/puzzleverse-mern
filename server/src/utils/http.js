export function json(res, status, body) {
  res.status(status).json(body)
}
export function ok(res, body) { json(res, 200, body) }
export function created(res, body) { json(res, 201, body) }
export function badRequest(res, message = 'Bad Request') { json(res, 400, { error: message }) }
export function unauthorized(res, message = 'Unauthorized') { json(res, 401, { error: message }) }
export function tooMany(res, message = 'Too Many Requests') { json(res, 429, { error: message }) }
