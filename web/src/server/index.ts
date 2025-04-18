import express from 'express'
import expressWs from 'express-ws'
import nunjucks from 'nunjucks'
import bodyParser from 'body-parser'
import axios from 'axios'
import morgan from 'morgan'
import qs from 'querystring'
import cookieParser from 'cookie-parser'
import WebSocket from 'ws'
import winston from 'winston'
import clfDate from 'clf-date'
import { getStaticPath } from './util.js'
import _jwt, { Jwt } from 'jsonwebtoken'

const API_URI = process.env.API_URL || 'http://localhost:8081'
const WS_URI = process.env.WS_URL || 'ws://localhost:8081/play'
const CLIENT_ID = process.env.CLIENT_ID
const CLIENT_SECRET = process.env.CLIENT_SECRET
const COOKIE_SECRET = process.env.COOKIE_SECRET

const jwt = {
  sign: (
    data: string | Buffer | object,
    secret: _jwt.Secret | _jwt.PrivateKey
  ) => {
    return new Promise<string | undefined>((resolve, reject) => {
      _jwt.sign(data, secret, (err, token) => {
        if (err) {
          return reject(err)
        }
        resolve(token)
      })
    })
  },
  verify: (token: string, secret: _jwt.Secret | _jwt.PublicKey) => {
    return new Promise<string | _jwt.JwtPayload>((resolve, reject) => {
      _jwt.verify(token, secret, (err, decoded) => {
        if (err) {
          return reject(err)
        }
        resolve(decoded)
      })
    })
  },
  decode: _jwt.decode,
}

async function main() {
  const appBase = express()
  const { app } = expressWs(appBase)
  nunjucks.configure('templates', {
    express: app,
  })

  winston.configure({
    level: 'info',
    transports: [new winston.transports.Console()],
    format: winston.format.combine(winston.format.simple()),
  })

  if (process.env.NODE_ENV === 'development') {
    const { createServer: createViteServer } = require('vite')
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'custom',
    })

    app.use(vite.middlewares)
  }

  app.use(morgan('combined'))
  app.use(cookieParser())
  app.use('/static', express.static(getStaticPath()))
  if (process.env.NODE_ENV !== 'development') {
    app.use('/assets', express.static('assets'))
  }

  app.post(
    '/login',
    bodyParser.json(),
    async function _onLogin(req, res, next) {
      try {
        const httpRes = await axios.post(
          `${API_URI}/token`,
          qs.stringify({
            ...req.body,
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
          })
        )
        const signed = await jwt.sign(
          JSON.stringify(httpRes.data),
          COOKIE_SECRET
        )

        res.cookie('session', signed)
        res.json({
          id: httpRes.data.user_id,
          email: httpRes.data.email,
          is_admin: httpRes.data.is_admin,
        })
      } catch (err) {
        const { response } = err
        if (!response) {
          return next(err)
        }
        res.status(response.status).json(response.data)
      }
    }
  )

  app.post(
    '/register',
    bodyParser.json(),
    function _onRegister(req, res, next) {
      axios
        .post(`${API_URI}/register`, {
          ...req.body,
        })
        .then(() => {
          res.json({
            success: true,
          })
        })
        .catch((err) => {
          const { response } = err
          if (!response) {
            return next(err)
          }
          res.status(response.status).json(response.data)
        })
    }
  )

  app.post(
    '/guest',
    bodyParser.json(),
    async function _onGuest(req, res, next) {
      try {
        const data = req.body.guestId || undefined
        const httpRes = await axios.post(`${API_URI}/guest`, data)

        console.log(data)
      } catch (err) {
        const { response } = err
        if (!response) {
          return next(err)
        }
        res.status(response.status).json(response.data)
      }
    }
  )

  app.get('/logout', function _onSignOut(req, res) {
    res.clearCookie('session')
    res.redirect('/login')
  })

  app.ws('/play', async function _onPlay(ws, req, next) {
    console.log(
      `${req.ip} - - [${clfDate(new Date())}] "WS ${req.url} HTTP/${
        req.httpVersion
      }" 101 - "${req.protocol === 'http' ? 'ws' : 'wss'}://${req.get(
        'host'
      )}" "${req.get('user-agent')}"`
    )
    winston.info(`[${req.ip}] incoming websocket connected`)
    let sessionData
    try {
      sessionData = await jwt.verify(req.cookies['session'], COOKIE_SECRET)
    } catch (err) {
      return next(err)
    }
    if (!sessionData) {
      return ws.close()
    }
    let queryParams = req.query as any
    try {
      winston.info(`[${req.ip}] connecting to outgoing socket ${WS_URI}`)
      const proxy = new WebSocket(`${WS_URI}?${qs.stringify(queryParams)}`, {
        headers: {
          Authorization: `Bearer ${sessionData.access_token}`,
        },
      })
      proxy.on('open', () => {
        winston.info(`[${req.ip}] outgoing websocket connected`)
      })
      ws.on('error', (e) => {
        winston.info(`[${req.ip}] error on incoming socket: ${e}`)
        proxy.close()
      })
      proxy.on('error', (e) => {
        winston.info(`[${req.ip}] error on outgoing socket: ${e}`)
        ws.close()
      })
      ws.onmessage = ({ data }) => {
        try {
          proxy.send(data)
        } catch (err) {}
      }
      proxy.onmessage = ({ data }) => {
        try {
          ws.send(data)
        } catch (err) {}
      }
      proxy.onclose = () => {
        winston.info(`[${req.ip}] outgoing websocket disconnected`)
        try {
          ws.close()
        } catch (err) {}
      }
      ws.onclose = () => {
        winston.info(`[${req.ip}] incoming websocket disconnected`)
        try {
          proxy.close()
        } catch (err) {}
      }
    } catch (err) {}
  })

  app.all('/api/*', bodyParser.json(), async function _onApi(req, res) {
    let headers = {}
    if (req.cookies['session']) {
      try {
        const sessionData = (await jwt.verify(
          req.cookies['session'],
          COOKIE_SECRET
        )) as _jwt.JwtPayload
        headers['Authorization'] = `Bearer ${sessionData.access_token}`
      } catch (err) {}
    }
    if (!!req.headers['content-type']) {
      headers['Content-Type'] = req.headers['content-type']
    }
    try {
      const httpRes = await axios({
        method: req.method.toLowerCase(),
        url: `${API_URI}${req.url}`,
        data: req.body,
        headers: headers,
      })
      res.status(httpRes.status).json(httpRes.data)
    } catch (err) {
      const { response } = err
      if (!response) {
        res.status(500).json({
          message: 'Internal Server Error',
        })
        return
      }
      res.status(response.status).json(response.data)
    }
  })

  app.get('/*', async function _onGet(req, res) {
    const params = {}
    if (req.cookies.session) {
      try {
        const sessionData = (await jwt.verify(
          req.cookies.session,
          COOKIE_SECRET
        )) as _jwt.JwtPayload
        params['userdata'] = btoa(
          JSON.stringify({
            id: sessionData.user_id,
            email: sessionData.email,
            is_admin: sessionData.is_admin,
          })
        )
      } catch (err) {}
    }
    res.render('index.html', params)
  })

  app.listen(8080, function _onListen() {
    winston.info(
      `application has started on [${
        this.address().port
      }] connected to [${API_URI}]`
    )
  })
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
