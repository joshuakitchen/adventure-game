import axios from 'axios'
import { FontAwesomeIcon } from 'solid-fontawesome'
import {
  children,
  Component,
  createEffect,
  createSignal,
  For,
  JSX,
  Match,
  onMount,
  ParentProps,
  Show,
  Switch,
} from 'solid-js'
import { createStore } from 'solid-js/store'
import { Portal } from 'solid-js/web'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { Table } from '../components'
import { cx } from '../util'

dayjs.extend(relativeTime)

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

const TabContent: Component<
  ParentProps<{ icon: string; title: string }> &
    JSX.HTMLAttributes<HTMLDivElement>
> = (props) => {
  return (
    <div data-icon={props.icon} data-title={props.title} {...props}>
      {props.children}
    </div>
  )
}

const Tab: Component<ParentProps<{}>> & {
  Content: typeof TabContent
} = (props) => {
  const [tabs, setTabs] = createSignal<
    Array<{ icon: string; title: string; element: Element }>
  >([])
  const [tab, setTab] = createSignal<number>(0)
  const c = children(() => props.children)
  createEffect(() => {
    const child = c()
    if (child instanceof Element) {
      setTabs([
        {
          icon: child.getAttribute('data-icon'),
          title: child.getAttribute('data-title'),
          element: child,
        },
      ])
    } else if (child instanceof Array) {
      setTabs(
        child.map((child: Element) => ({
          icon: child.getAttribute('data-icon'),
          title: child.getAttribute('data-title'),
          element: child,
        }))
      )
    }
  })
  return (
    <>
      <div class='flex'>
        <For each={tabs()}>
          {(child, idx) => (
            <a
              class={cx(
                'max-md:text-center p-4 flex-1 bg-zinc-800 md:first:rounded-tl-md md:last:rounded-tr-md hover:bg-zinc-700 cursor-pointer transition-colors',
                {
                  'bg-zinc-700': tab() === idx(),
                }
              )}
              onClick={() => setTab(idx())}
            >
              <FontAwesomeIcon icon={child.icon} className='pr-4' />
              <span class='max-md:hidden'>{child.title}</span>
            </a>
          )}
        </For>
      </div>
      <Show when={tabs()[tab()]}>{tabs()[tab()].element}</Show>
    </>
  )
}

Tab.Content = TabContent

const UserTab: Component<{
  onClose?: () => void
}> = (props) => {
  const [userData, setUserData] = createStore<{ users: Array<UserData> }>({
    users: [],
  })
  const [selectedUser, setSelectedUser] = createSignal<string>()

  onMount(() => {
    axios.get('/api/v1/users').then((response) => {
      setUserData('users', response.data.data)
    })
  })
  return (
    <>
      <Show when={selectedUser()}>
        <UserPage user_id={selectedUser()} />
      </Show>
      <Show when={!selectedUser()}>
        <div class='overflow-y-auto'>
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
        </div>
      </Show>
      <div class='flex-1 border-b border-b-zinc-800'></div>
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
    </>
  )
}

const ChatlogTab: Component<ParentProps<{ onClose?: () => void }>> = (
  props
) => {
  const [chatData, setChatData] = createStore<{ chat: Array<any> }>({
    chat: [],
  })

  onMount(() => {
    axios.get('/api/v1/chatlog').then((response) => {
      setChatData('chat', response.data.data)
    })
  })
  return (
    <>
      <div class='overflow-y-auto'>
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.Header class='w-80 max-lg:hidden'>Time</Table.Header>
              <Table.Header class='w-40'>User</Table.Header>
              <Table.Header>Message</Table.Header>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            <For each={chatData.chat}>
              {(chat) => (
                <Table.Row class='hover:bg-zinc-800 hover:cursor-pointer'>
                  <Table.Cell class='max-lg:hidden'>
                    {dayjs().to(chat.timestamp)}
                  </Table.Cell>
                  <Table.Cell>{chat.user.name}</Table.Cell>
                  <Table.Cell>{chat.message}</Table.Cell>
                </Table.Row>
              )}
            </For>
          </Table.Body>
        </Table>
      </div>
      <div class='flex-1 border-b border-b-zinc-800'></div>
      <div class='grid grid-cols-2 md:grid-cols-4 gap-8'>
        <button
          class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:2] md:[grid-column:4] hover:bg-zinc-700 transition-colors md:rounded-br'
          onClick={() => {
            props.onClose()
          }}
        >
          Close
        </button>
      </div>
    </>
  )
}

const AuditTab: Component<ParentProps<{ onClose?: () => void }>> = (props) => {
  const [auditData, setAuditData] = createStore<{ audit: Array<any> }>({
    audit: [],
  })

  onMount(() => {
    axios.get('/api/v1/audit').then((response) => {
      setAuditData('audit', response.data.data)
    })
  })
  return (
    <>
      <div class='overflow-y-auto'>
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.Header class='w-80 max-lg:hidden'>Time</Table.Header>
              <Table.Header class='w-40'>User</Table.Header>
              <Table.Header>Classification</Table.Header>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            <For each={auditData.audit}>
              {(chat) => (
                <Table.Row class='hover:bg-zinc-800 hover:cursor-pointer'>
                  <Table.Cell class='max-lg:hidden'>
                    {dayjs().to(chat.timestamp)}
                  </Table.Cell>
                  <Table.Cell>{chat.user.name}</Table.Cell>
                  <Table.Cell>{chat.classification}</Table.Cell>
                </Table.Row>
              )}
            </For>
          </Table.Body>
        </Table>
      </div>
      <div class='flex-1 border-b border-b-zinc-800'></div>
      <div class='grid grid-cols-2 md:grid-cols-4 gap-8'>
        <button
          class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:2] md:[grid-column:4] hover:bg-zinc-700 transition-colors md:rounded-br'
          onClick={() => {
            props.onClose()
          }}
        >
          Close
        </button>
      </div>
    </>
  )
}

export const AdminModal: Component<{
  visible?: boolean
  onClose?: () => void
}> = (props) => {
  return (
    <Show when={props.visible}>
      <Portal mount={document.getElementById('modal-container')}>
        <div class='fixed left-0 top-0 w-screen h-screen bg-black/60 font-mono pointer-events-auto z-1000'>
          <div class='fixed w-full h-full md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-3/4 md:h-3/4 flex flex-col text-gray-300 bg-zinc-900 md:shadow-md md:rounded-md'>
            <Tab>
              <Tab.Content
                class='flex flex-col flex-1'
                icon='users'
                title='Users'
              >
                <UserTab onClose={props.onClose} />
              </Tab.Content>
              <Tab.Content
                class='flex flex-col flex-1 overflow-y-hidden'
                icon='message'
                title='Chatlog'
              >
                <ChatlogTab onClose={props.onClose} />
              </Tab.Content>
              <Tab.Content
                class='flex flex-col flex-1 overflow-y-hidden'
                icon='info-circle'
                title='Audit'
              >
                <AuditTab onClose={props.onClose} />
              </Tab.Content>
            </Tab>
          </div>
        </div>
      </Portal>
    </Show>
  )
}

export default AdminModal
