import { Component, createEffect, createSignal, onMount, Show } from 'solid-js'
import { FontAwesomeIcon } from 'solid-fontawesome'
import { useUser } from '../user'
import { useNavigate } from '@solidjs/router'
import axios from 'axios'
import { Terminal } from '../components/Terminal'
import { AdminModal } from '../modals/AdminModal'

export const GamePage: Component = () => {
  const navigate = useNavigate()
  const [user, setUser] = useUser()
  const [ws, setWs] = createSignal<WebSocket>()
  const [text, setText] = createSignal<string>('')
  const [suggestion, setSuggestion] = createSignal<string>('')
  const [input, setInput] = createSignal<string>('')
  const [chatText, setChatText] = createSignal<string>('')
  const [chatInput, setChatInput] = createSignal<string>('')
  const [ready, setReady] = createSignal(false)
  const [adminModal, setAdminModal] = createSignal(false)
  const [retries, setRetries] = createSignal(0)

  onMount(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${protocol}://${document.location.host}/play`)
    ws.onopen = () => {
      setWs(ws)
      setTimeout(() => {
        ws.send(JSON.stringify({ type: 'ready' }))
      }, 1000)
    }
    ws.onmessage = ({ data }) => {
      const message = JSON.parse(data)
      if (message.type == 'error') {
        setText((text) => text + '\x1b[31m' + message.data + '\x1b[0m\n')
      } else if (message.type == 'game') {
        if (!ready()) {
          setChatText(
            '\x1b[92mYou are connected to the global chat channel.\x1b[0m\n'
          )
          setReady(true)
        }
        setText((text) => text + message.data + '\n')
      } else if (message.type === 'suggestion') {
        if (!ready()) {
          setChatText(
            '\x1b[92mYou are connected to the global chat channel.\x1b[0m\n'
          )
          setReady(true)
        }
        setSuggestion(message.data)
      } else if (message.type === 'autocomplete') {
        if (message.data.length > 0) {
          setInput(message.data)
          setSuggestion('')
        }
      } else if (message.type === 'chat') {
        setChatText((text) => text + message.data + '\n')
      }
    }
    ws.onclose = () => {
      setWs(null)
    }
  })

  createEffect(() => {
    if (!user.id) {
      navigate('/login')
    }
  })

  return (
    <>
      <AdminModal
        visible={adminModal()}
        onClose={() => {
          setAdminModal(false)
        }}
      />
      <div class='mx-auto h-full flex flex-col md:flex-row text-gray-300'>
        <nav class='flex flex-row md:flex-col border-l border-zinc-800 bg-zinc-800'>
          <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
            <FontAwesomeIcon className='fa-fw' icon='terminal' />
          </a>
          <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
            <FontAwesomeIcon className='fa-fw' icon='comments' />
          </a>
          <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
            <FontAwesomeIcon className='fa-fw' icon='bug' />
          </a>
          <a
            class='p-4 transition-colors hover:bg-zinc-700 hover:cursor-pointer'
            onClick={(e) => {
              axios
                .get('/logout')
                .then(() => {
                  setUser(['email', 'id', 'is_admin'], null)
                  navigate('/login')
                })
                .catch((e) => {
                  setUser(null)
                })
            }}
          >
            <FontAwesomeIcon className='fa-fw' icon='sign-out' />
          </a>
          <Show when={user.is_admin}>
            <a
              class='mt-auto p-4 transition-colors hover:bg-zinc-700'
              href='#'
              onClick={(e) => {
                e.preventDefault()
                setAdminModal(true)
              }}
            >
              <FontAwesomeIcon className='fa-fw' icon='cog' />
            </a>
          </Show>
        </nav>
        <div class='flex-1 h-1 md:h-auto'>
          <Terminal
            screen={{ text: text(), scrollOnChange: true }}
            value={input()}
            autocomplete={suggestion()}
            onSend={(cmd: string) => {
              setText((text) => text + '> ' + cmd + '\n')
              ws().send(JSON.stringify({ type: 'game', data: cmd }))
              setInput('')
              setSuggestion('')
            }}
            onChange={(cmd: string) => {
              setInput(cmd)
              let sock = ws()
              if (sock) {
                sock.send(
                  JSON.stringify({ type: 'autocomplete_suggest', data: cmd })
                )
              }
            }}
            onSuggest={(cmd: string) => {
              let sock = ws()
              if (sock) {
                sock.send(
                  JSON.stringify({ type: 'autocomplete_get', data: cmd })
                )
              }
            }}
          />
        </div>
        <div class='w-96 flex-col border-l border-zinc-800 hidden lg:flex'>
          <Terminal
            screen={{ text: chatText(), scrollOnChange: true }}
            value={chatInput()}
            onSend={() => {
              ws().send(
                JSON.stringify({ type: 'game', data: `say ${chatInput()}` })
              )
              setChatInput('')
            }}
            onChange={(cmd: string) => {
              setChatInput(cmd)
            }}
          />
        </div>
      </div>
    </>
  )
}

export default GamePage
