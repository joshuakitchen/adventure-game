import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import axios from 'axios'
import { useUser } from '../user'

const LoginPage = function LoginPage() {
  const [state, setState] = useState({ username: '', password: '' })
  const [user, setUser] = useUser()
  const navigate = useNavigate()
  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [])
  return (
    <div className='mx-auto mt-4 w-[480px] flex flex-col gap-3'>
      <div className='p-4 text-gray-200 bg-zinc-800 rounded-xl text-center'>
        Welcome to the World of Alvara
      </div>
      <div className='p-4 flex flex-col gap-3 text-gray-200 bg-zinc-800 rounded-xl'>
        <input
          value={state.username}
          onChange={(e) =>
            setState((state) => ({ ...state, username: e.target.value }))
          }
          className='p-2 bg-zinc-900 rounded-xl outline-none'
          placeholder='Email Address'
        />
        <input
          value={state.password}
          onChange={(e) =>
            setState((state) => ({ ...state, password: e.target.value }))
          }
          className='p-2 bg-zinc-900 rounded-xl outline-none'
          placeholder='Password'
          type='password'
        />
        <div className='flex gap-3'>
          <button
            className='w-full py-2 bg-zinc-900 hover:bg-zinc-900/50 ease-in-out transition-all rounded-xl'
            onClick={() => {
              axios
                .post('/login', state)
                .then((res) => {
                  setUser(res.data)
                  navigate('/')
                })
                .catch((err) => {
                  console.log(err)
                })
            }}
          >
            Login
          </button>
          <button className='w-full py-2 bg-zinc-900 hover:bg-zinc-900/50 ease-in-out transition-all rounded-xl'>
            Register
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
