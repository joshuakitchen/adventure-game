import axios from 'axios'
import { FontAwesomeIcon } from 'solid-fontawesome'
import { Component, createEffect, For, Show } from 'solid-js'
import { createStore } from 'solid-js/store'
import { Portal } from 'solid-js/web'
import { Table } from '../components'

export const AdminModal: Component<{
  visible?: boolean
  onClose?: () => void
}> = (props) => {
  const [userData, setUserData] = createStore<{
    users: Array<{ id: string; email: string; name: string; is_admin: boolean }>
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
        <div class='fixed left-0 top-0 w-screen h-screen bg-black/60 font-mono pointer-events-auto z-1000'>
          <div class='fixed w-full h-full md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-3/4 md:h-3/4 flex flex-col text-gray-300 bg-zinc-900 md:shadow-md md:rounded-md'>
            <div class='flex'>
              <a class='p-4 flex-1 bg-zinc-800 md:rounded-tl-md hover:bg-zinc-700 cursor-pointer transition-colors'>
                <FontAwesomeIcon icon='users' className='pr-4' />
                Users
              </a>
              <a class='p-4 flex-1 bg-zinc-800 md:rounded-tr-md hover:bg-zinc-700 cursor-pointer transition-colors'>
                <FontAwesomeIcon icon='cog' className='pr-4' />
                Settings
              </a>
            </div>
            <div class='flex-1 overflow-y-auto border-b border-zinc-800'>
              <Table>
                <Table.Head>
                  <Table.Row>
                    <Table.Header class='md:w-[24rem]'>Email</Table.Header>
                    <Table.Header>Name</Table.Header>
                    <Table.Header class='w-40 hidden md:table-cell'>
                      Role
                    </Table.Header>
                  </Table.Row>
                </Table.Head>
                <Table.Body>
                  <For each={userData.users}>
                    {(user) => (
                      <Table.Row>
                        <Table.Cell>{user.email}</Table.Cell>
                        <Table.Cell>{user.name}</Table.Cell>
                        <Table.Cell class='hidden md:table-cell'>
                          {user.is_admin ? 'Admin' : 'User'}
                        </Table.Cell>
                      </Table.Row>
                    )}
                  </For>
                </Table.Body>
              </Table>
            </div>
            <div class='grid grid-cols-2 md:grid-cols-4 gap-8'>
              <button
                class='p-4 bg-zinc-800 cursor-pointer [grid-column:2] md:[grid-column:4] hover:bg-zinc-700 transition-colors md:rounded-br'
                onClick={() => {
                  props.onClose()
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </Portal>
    </Show>
  )
}

export default AdminModal
