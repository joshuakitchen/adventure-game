import axios from 'axios'
import { FontAwesomeIcon } from 'solid-fontawesome'
import {
  Component,
  createEffect,
  createSignal,
  For,
  onMount,
  Show,
} from 'solid-js'
import { createStore } from 'solid-js/store'
import { Portal } from 'solid-js/web'
import { Table } from '../components'

type UserData = {
  id: string
  email: string
  name: string
  location: string
  is_admin: boolean
}

type ExtendedUserData = UserData & {
  additional_data: any
  state: string
}

const UserPage: Component<{ user_id: string }> = (props) => {
  const [userData, setUserData] = createSignal<ExtendedUserData>(null)
  const [additionalData, setAdditionalData] = createSignal<string>(null)

  onMount(() => {
    axios.get(`/api/v1/users/${props.user_id}`).then((response) => {
      let data = response.data
      data.additional_data = JSON.parse(data.additional_data)
      setAdditionalData(JSON.stringify(data.additional_data, null, 4))
      setUserData(data)
    })
  })

  createEffect(() => {
    console.log(userData())
  })

  return (
    <Table>
      <Table.Head>
        <Table.Row>
          <Table.Header>Property</Table.Header>
          <Table.Header>Value</Table.Header>
        </Table.Row>
      </Table.Head>
      <Table.Body>
        <Table.Row>
          <Table.Cell>ID</Table.Cell>
          <Table.Cell>{userData()?.id}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>Email</Table.Cell>
          <Table.Cell>{userData()?.email}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>Name</Table.Cell>
          <Table.Cell>{userData()?.name}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>Role</Table.Cell>
          <Table.Cell>{userData()?.is_admin ? 'Admin' : 'User'}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>Location</Table.Cell>
          <Table.Cell>{userData()?.location}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>State</Table.Cell>
          <Table.Cell>{userData()?.state}</Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell>Additional Data</Table.Cell>
          <Table.Cell>
            <textarea
              class='w-full h-32 bg-zinc-800 text-gray-300 p-2 rounded-md resize-none'
              onInput={(e) => {
                setAdditionalData(e.currentTarget.value)
                try {
                  userData().additional_data = JSON.parse(e.currentTarget.value)
                } catch (err) {}
              }}
            >
              {additionalData()}
            </textarea>
          </Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell colspan={2}>
            <div class='flex gap-4'>
              <div class='flex-1'></div>
              <button
                class='p-4 min-w-44 bg-zinc-800 hover:bg-zinc-700 transition-colors cursor-pointer'
                onClick={(e) => {
                  e.preventDefault()
                  axios
                    .put(`/api/v1/users/${userData()?.id}`, {
                      additional_data: JSON.stringify(
                        userData()?.additional_data
                      ),
                    })
                    .then((response) => {
                      let data = response.data
                      data.additional_data = JSON.parse(data.additional_data)
                      setUserData(data)
                    })
                }}
              >
                Save
              </button>
            </div>
          </Table.Cell>
        </Table.Row>
      </Table.Body>
    </Table>
  )
}

export const AdminModal: Component<{
  visible?: boolean
  onClose?: () => void
}> = (props) => {
  const [userData, setUserData] = createStore<{ users: Array<UserData> }>({
    users: [],
  })
  const [selectedUser, setSelectedUser] = createSignal<string>()

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
              <Show when={selectedUser()}>
                <UserPage user_id={selectedUser()} />
              </Show>
              <Show when={!selectedUser()}>
                <Table>
                  <Table.Head>
                    <Table.Row>
                      <Table.Header class='md:w-[24rem]'>Email</Table.Header>
                      <Table.Header>Name</Table.Header>
                      <Table.Header class='w-40'>Location</Table.Header>
                      <Table.Header class='w-40 hidden md:table-cell'>
                        Role
                      </Table.Header>
                    </Table.Row>
                  </Table.Head>
                  <Table.Body>
                    <For each={userData.users}>
                      {(user) => (
                        <Table.Row
                          class='hover:bg-zinc-800 hover:cursor-pointer'
                          onDblClick={() => {
                            setSelectedUser(user.id)
                          }}
                        >
                          <Table.Cell>{user.email}</Table.Cell>
                          <Table.Cell>{user.name}</Table.Cell>
                          <Table.Cell>{user.location}</Table.Cell>
                          <Table.Cell class='hidden md:table-cell'>
                            {user.is_admin ? 'Admin' : 'User'}
                          </Table.Cell>
                        </Table.Row>
                      )}
                    </For>
                  </Table.Body>
                </Table>
              </Show>
            </div>
            <div class='grid grid-cols-2 md:grid-cols-4 gap-8'>
              <Show when={selectedUser()}>
                <button
                  class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:1] md:[grid-column:3] hover:bg-zinc-700 transition-colors md:rounded-br'
                  onClick={() => {
                    setSelectedUser(undefined)
                  }}
                >
                  Back
                </button>
              </Show>
              <button
                class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:2] md:[grid-column:4] hover:bg-zinc-700 transition-colors md:rounded-br'
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
