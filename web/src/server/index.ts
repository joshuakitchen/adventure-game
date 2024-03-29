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
import { getStaticPath } from './util'

const API_URI = process.env.API_URL || 'http://localhost:8081'
const WS_URI = process.env.WS_URL || 'ws://localhost:8081/play'
const CLIENT_ID = process.env.CLIENT_ID
const CLIENT_SECRET = process.env.CLIENT_SECRET

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

app.use(morgan('combined'))
app.use(cookieParser())
app.use('/static', express.static(getStaticPath()))

app.post('/login', bodyParser.json(), function _onLogin(req, res, next) {
  axios
    .post(
      `${API_URI}/token`,
      qs.stringify({
        ...req.body,
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
      })
    )
    .then((httpRes) => {
      res.cookie('session', {
        ...httpRes.data,
      })
      res.json({
        id: httpRes.data.user_id,
        email: httpRes.data.email,
        is_admin: httpRes.data.is_admin,
      })
    })
    .catch((err) => {
      const { response } = err
      if (!response) {
        return next(err)
      }
      res.status(response.status).json(response.data)
    })
})

app.post('/register', bodyParser.json(), function _onRegister(req, res, next) {
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
})

app.get('/logout', function _onSignOut(req, res) {
  res.clearCookie('session')
  res.redirect('/login')
})

app.ws('/play', function _onPlay(ws, req, next) {
  console.log(
    `${req.ip} - - [${clfDate(new Date())}] "WS ${req.path} HTTP/${
      req.httpVersion
    }" 101 - "${req.protocol === 'http' ? 'ws' : 'wss'}://${req.get(
      'host'
    )}" "${req.get('user-agent')}"`
  )
  winston.info(`[${req.ip}] incoming websocket connected`)
  try {
    winston.info(`[${req.ip}] connecting to outgoing socket ${WS_URI}`)
    const proxy = new WebSocket(WS_URI, {
      headers: {
        Authorization: `Bearer ${req.cookies['session'].access_token}`,
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
      try {
        ws.close()
      } catch (err) {}
    }
    ws.onclose = () => {
      try {
        proxy.close()
      } catch (err) {}
    }
  } catch (err) {}
})

app.get('/*', function _onGet(req, res) {
  const params = {}
  if (req.cookies.session) {
    params['userdata'] = btoa(
      JSON.stringify({
        id: req.cookies.session.user_id,
        email: req.cookies.session.email,
        is_admin: req.cookies.session.is_admin,
      })
    )
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
