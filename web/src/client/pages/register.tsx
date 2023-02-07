import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import axios from 'axios'
import { useUser } from '../user'

const RegisterPage = function RegisterPage() {
  const [state, setState] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  })
  const [user, setUser] = useUser()
  const navigate = useNavigate()
  useEffect(() => {
    if (user) {
      navigate('/')
    }
  }, [])
  return (
    <div className='mx-auto mt-4 w-[480px] flex flex-col'>
      <div className='p-4 text-gray-200 text-center border-b border-zinc-800 font-mono'>
        Register to become a Citizen
      </div>
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
        <input
          value={state.confirmPassword}
          onChange={(e) =>
            setState((state) => ({ ...state, confirmPassword: e.target.value }))
          }
          className='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Confirm Password'
          type='password'
          name='confirm-password'
        />
        <div className='flex gap-3'>
          <button
            className='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono'
            onClick={() => {
              navigate('/login')
            }}
          >
            Back to Login
          </button>
          <button
            disabled={
              !state.username ||
              !state.password ||
              !state.confirmPassword ||
              state.password !== state.confirmPassword
            }
            className='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono disabled:hover:cursor-not-allowed disabled:bg-zinc-900'
            onClick={() => {
              axios
                .post('/register', {
                  email: state.username,
                  password: state.password,
                })
                .then((res) => {
                  navigate('/login')
                })
                .catch((err) => {
                  console.log(err)
                })
            }}
          >
            Register
          </button>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
