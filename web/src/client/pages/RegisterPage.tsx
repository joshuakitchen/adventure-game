import { useNavigate } from '@solidjs/router'
import axios from 'axios'
import { Component, createSignal, Show } from 'solid-js'

const RegisterPage: Component<{}> = () => {
  const navigate = useNavigate()
  const [error, setError] = createSignal<string | null>(null)
  const [email, setEmail] = createSignal('')
  const [password, setPassword] = createSignal('')
  const [confirmPassword, setConfirmPassword] = createSignal('')

  return (
    <div class='mx-auto mt-4 md:w-[480px] flex flex-col'>
      <div class='p-4 text-gray-200 text-center border-b border-zinc-800 font-mono'>
        Register to become a Citizen
      </div>
      <Show when={error()}>
        <div class='px-4 pt-4 font-mono'>
          <div class='p-4 text-gray-200 bg-red-800'>{error()}</div>
        </div>
      </Show>
      <div class='p-4 flex flex-col gap-3 text-gray-200'>
        <input
          class='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Email Address'
          name='email'
          autocomplete='email'
          value={email()}
          onInput={(e) => setEmail(e.currentTarget.value)}
        />
        <input
          class='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Password'
          type='password'
          name='password'
          autocomplete='password'
          value={password()}
          onInput={(e) => setPassword(e.currentTarget.value)}
        />
        <input
          class='p-4 bg-zinc-800 outline-none font-mono'
          placeholder='Confirm Password'
          type='password'
          name='confirm-password'
          value={confirmPassword()}
          onInput={(e) => setConfirmPassword(e.currentTarget.value)}
        />
        <div class='flex gap-3'>
          <button
            class='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono'
            onClick={() => {
              navigate('/login')
            }}
          >
            Back to Login
          </button>
          <button
            disabled={
              !email() ||
              !password() ||
              !confirmPassword() ||
              password() !== confirmPassword()
            }
            class='w-full py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono disabled:hover:cursor-not-allowed disabled:bg-zinc-900'
            onClick={() => {
              axios
                .post('/register', {
                  email: email(),
                  password: password(),
                })
                .then((res) => {
                  navigate('/login')
                })
                .catch((err) => {
                  const { response } = err
                  if (response) {
                    setError(response.data.detail)
                  }
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
