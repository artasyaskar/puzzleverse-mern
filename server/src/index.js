import express from 'express'
import morgan from 'morgan'
import path from 'path'
import { fileURLToPath } from 'url'
import authRouter from './auth/routes.js'
import { requireAuth } from './auth/service.js'
import requestId from './middleware/requestId.js'
import logger from './middleware/logger.js'
import errorHandler from './middleware/errorHandler.js'
import { PORT, APP_NAME } from './config.js'
import cors from './middleware/cors.js'
import securityHeaders from './middleware/securityHeaders.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const app = express()

app.use(requestId())
app.use(logger())
app.use(morgan('dev'))
app.use(express.json())
app.use(cors())
app.use(securityHeaders())

app.get('/api/health', (req, res) => {
  res.setHeader('X-App-Name', APP_NAME)
  res.json({ status: 'ok' })
})

// Auth routes
app.use('/api/auth', authRouter)

// Protected current-user route
app.get('/api/me', requireAuth, (req, res) => {
  res.setHeader('Cache-Control', 'no-store')
  // res.json will set Content-Type: application/json automatically
  res.json({ id: req.user.id, email: req.user.email, createdAt: req.user.createdAt })
})

const clientDist = path.resolve(__dirname, '../../client/dist')
app.use(express.static(clientDist))
app.get('*', (req, res) => {
  res.sendFile(path.join(clientDist, 'index.html'))
})

app.use(errorHandler())

const port = PORT
app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`)
})
