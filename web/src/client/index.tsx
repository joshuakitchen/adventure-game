/* @refresh reload */
import './index.css'
import { render } from 'solid-js/web'
import { Router } from '@solidjs/router'
import { UserProvider } from './user'
import { Component, lazy } from 'solid-js'
import { library } from '@fortawesome/fontawesome-svg-core'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'

library.add(far, fas)

const root = document.getElementById('root')

if (!root) {
  throw new Error('No root element found')
}

const routes = [
  {
    path: '/',
    component: lazy(() => import('./pages/GamePage')),
  },
  {
    path: '/login',
    component: lazy(() => import('./pages/LoginPage')),
  },
  {
    path: '/register',
    component: lazy(() => import('./pages/RegisterPage')),
  },
]

const App: Component = () => {
  return (
    <UserProvider>
      <Router>{routes}</Router>
    </UserProvider>
  )
}

render(() => <App />, root)
