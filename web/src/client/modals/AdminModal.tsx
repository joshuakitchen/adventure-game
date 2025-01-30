import axios from 'axios'
import { FontAwesomeIcon } from 'solid-fontawesome'
import { Component, createEffect, For, Show } from 'solid-js'
import { createStore } from 'solid-js/store'
import { Portal } from 'solid-js/web'

export const AdminModal: Component<{
  visible?: boolean
  onClose?: () => void
}> = (props) => {
  const [userData, setUserData] = createStore<{
    users: Array<{ id: string; email: string; is_admin: boolean }>
  }>({ users: [] })

  createEffect(() => {
    if (!props.visible) return
    axios.get('/api/v1/users').then((response) => {
      setUserData('users', response.data.data)
    })
  })

  return (
    <Show when={props.visible}>
      <Portal mount={document.getElementById('modal-container')}>
        <div class='fixed w-screen h-screen bg-black/60 font-mono'>
          <div class='fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] h-1/2 flex flex-col text-gray-300 bg-zinc-900 shadow-md'>
            <div class='flex'>
              <a class='p-4 flex-1 bg-zinc-800'>
                <FontAwesomeIcon icon='users' className='pr-4' />
                Users
              </a>
            </div>
            <div class='flex-1'>
              <table class='w-full'>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th class='w-1/6'>Admin</th>
                  </tr>
                </thead>
                <tbody>
                  <For each={userData.users}>
                    {(user) => (
                      <tr>
                        <td>{user.email}</td>
                        <td>{user.is_admin ? 'Admin' : 'User'}</td>
                      </tr>
                    )}
                  </For>
                </tbody>
              </table>
            </div>
            <button
              class='p-4 bg-zinc-800'
              onClick={() => {
                props.onClose()
              }}
            >
              Close
            </button>
          </div>
        </div>
      </Portal>
    </Show>
  )
}

export default AdminModal
