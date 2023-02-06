import express from 'express'
import expressWs from 'express-ws'
import nunjucks from 'nunjucks'
import bodyParser from 'body-parser'
import axios from 'axios'
import qs from 'querystring'
import cookieParser from 'cookie-parser'
import WebSocket from 'ws'
import { getStaticPath } from './util'

const API_URI = process.env.API_URL || 'http://localhost:8081'
const WS_URI = process.env.WS_URL || 'ws://localhost:8081/play'

const appBase = express()
const { app } = expressWs(appBase)
nunjucks.configure('templates', {
  express: app,
})

app.use(cookieParser())
app.use('/static', express.static(getStaticPath()))

app.post('/login', bodyParser.json(), function _onLogin(req, res, next) {
  axios
    .post(
      `${API_URI}/token`,
      qs.stringify({
        ...req.body,
        client_id: '4752871f-71c5-4940-8c1e-bee3be614c63',
        client_secret:
          '0f2321742fc62e3390e9b1d2161be5665652a1c9e1bb781f012edf8a3f1176721e257a4866703cce',
      })
    )
    .then((httpRes) => {
      res.cookie('session', httpRes.data)
      res.json({
        id: httpRes.data.user_id,
        email: httpRes.data.email,
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

app.ws('/play', function _onPlay(ws, req) {
  try {
    const proxy = new WebSocket(WS_URI, {
      headers: {
        Authorization: `Bearer ${req.cookies['session'].access_token}`,
      },
    })
    ws.on('error', () => {
      proxy.close()
    })
    proxy.on('error', () => {
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
      })
    )
  }
  res.render('index.html', params)
})

app.listen(8080, function _onListen() {
  console.log(`application has started on [${this.address().port}]`)
})
