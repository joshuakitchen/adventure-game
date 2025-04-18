import { Component, createEffect, Show } from 'solid-js'
import { createStore } from 'solid-js/store'
import { useNavigate } from '@solidjs/router'
import axios from 'axios'
import { useUser } from '../user'
import { Button } from '@components'

const LoginPage: Component = () => {
  const navigate = useNavigate()
  const [store, setStore] = createStore({
    email: '',
    password: '',
    error: null,
  })
  const [user, setUser] = useUser()

  createEffect(() => {
    if (!!user.id) {
      navigate('/')
    }
  })
  return (
    <div class='mx-auto pt-4 md:w-[480px] flex flex-col'>
      <div class='p-4 text-gray-200 text-center border-b border-zinc-800 font-mono'>
        Welcome to Nymirith
      </div>
      <Show when={store.error}>
        <div class='px-4 pt-4 font-mono'>
          <div class='p-4 text-gray-200 bg-red-800'>{store.error}</div>
        </div>
      </Show>
      <div class='p-4 flex flex-col gap-3 text-gray-200'>
        <input
          class='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Email Address'
          name='email'
          autocomplete='email'
          autocapitalize='off'
          value={store.email}
          onChange={(e) => setStore('email', e.currentTarget.value)}
        />
        <input
          class='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Password'
          type='password'
          name='password'
          autocomplete='password'
          autocapitalize='off'
          value={store.password}
          onChange={(e) => setStore('password', e.currentTarget.value)}
        />
        <div class='flex gap-3'>
          <button
            class='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono hover:cursor-pointer'
            onClick={(e) => {
              axios
                .post('/login', {
                  username: store.email,
                  password: store.password,
                })
                .then((res) => {
                  setUser({ ...res.data, is_guest: false })
                  navigate('/')
                })
                .catch((err) => {
                  const { response } = err
                  if (response) {
                    setStore('error', response.data.detail)
                  }
                })
            }}
          >
            Login
          </button>
          <button
            class='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono hover:cursor-pointer'
            onClick={() => {
              navigate('/register')
            }}
          >
            Register
          </button>
        </div>
        <Button
          onClick={() => {
            // Get existing guest credentials from localStorage or generate new ones
            const guestId = localStorage.getItem('guestId') || null
            const guestKey = localStorage.getItem('guestKey') || null

            axios
              .post('/guest', {
                guestId,
                guestKey,
              })
              .then((res) => {
                // Save guest credentials to localStorage
                localStorage.setItem('guestId', res.data.email)
                localStorage.setItem('guestKey', guestKey || res.data.id) // Use existing key or ID as new key

                // Update user state and navigate to home
                setUser({ ...res.data, is_guest: true })
                navigate('/')
              })
              .catch((err) => {
                const { response } = err
                if (response) {
                  setStore(
                    'error',
                    response.data.detail || 'Failed to login as guest'
                  )
                }
              })
          }}
        >
          Play as Guest
        </Button>
      </div>
    </div>
  )
}

export default LoginPage
