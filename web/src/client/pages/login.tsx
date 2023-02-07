import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import axios from 'axios'
import { useUser } from '../user'

const LoginPage = function LoginPage() {
  const [state, setState] = useState({
    username: '',
    password: '',
    error: null,
  })
  const [user, setUser] = useUser()
  const navigate = useNavigate()
  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [])
  const errorPane = !state.error ? null : (
    <div className='px-4 pt-4 font-mono'>
      <div className='p-4 text-gray-200 bg-red-800'>{state.error}</div>
    </div>
  )
  return (
    <div className='mx-auto mt-4 w-[480px] flex flex-col'>
      <div className='p-4 text-gray-200 text-center border-b border-zinc-800 font-mono'>
        Welcome to Nymirith
      </div>
      {errorPane}
      <div className='p-4 flex flex-col gap-3 text-gray-200'>
        <input
          value={state.username}
          onChange={(e) =>
            setState((state) => ({ ...state, username: e.target.value }))
          }
          className='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Email Address'
          name='email'
          autoComplete='email'
        />
        <input
          value={state.password}
          onChange={(e) =>
            setState((state) => ({ ...state, password: e.target.value }))
          }
          className='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Password'
          type='password'
          name='password'
          autoComplete='password'
        />
        <div className='flex gap-3'>
          <button
            className='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono'
            onClick={() => {
              axios
                .post('/login', state)
                .then((res) => {
                  setUser(res.data)
                  navigate('/')
                })
                .catch((err) => {
                  const { response } = err
                  if (response) {
                    setState((state) => ({
                      ...state,
                      error: response.data.detail,
                    }))
                  }
                })
            }}
          >
            Login
          </button>
          <button
            className='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono'
            onClick={() => {
              navigate('/register')
            }}
          >
            Register
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
