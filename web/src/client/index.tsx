/* @refresh reload */
import './index.css'
import { Portal, render } from 'solid-js/web'
import { Router } from '@solidjs/router'
import { UserProvider } from './user'
import { Component, createSignal, lazy, Show } from 'solid-js'
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
  const [showCookieBanner, setShowCookieBanner] = createSignal<boolean>(
    localStorage.getItem('cookie-accept') === null
  )
  return (
    <UserProvider>
      <div class='flex-1'>
        <Router>{routes}</Router>
      </div>
      <Show when={showCookieBanner()}>
        <div class='p-4 bg-zinc-950 text-zinc-300 flex gap-4 pointer-events-auto z-10 align-middle'>
          <div class='flex-1 py-2'>
            This website uses essential cookies to manage sessions, it does not
            use third-party tracking cookies.
          </div>
          <button
            class='bg-zinc-800 px-16 py-2 hover:cursor-pointer hover:bg-zinc-700'
            onClick={() => {
              localStorage.setItem('cookie-accept', 'true')
              setShowCookieBanner(false)
            }}
          >
            Accept
          </button>
        </div>
      </Show>
    </UserProvider>
  )
}

render(() => <App />, root)
