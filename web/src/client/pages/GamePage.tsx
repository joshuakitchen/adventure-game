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
  const [pingInterval, setPingInterval] = createSignal<number | null>(null)
  const [connectInterval, setConnectInterval] = createSignal<number | null>(
    null
  )
  const [readyInterval, setReadyInterval] = createSignal<number | null>(null)
  const [connecting, setConnecting] = createSignal(false)

  let chatDiv: HTMLDivElement
  function sendChatText(str: string) {
    if (!chatDiv) {
      return
    }
    if (getComputedStyle(chatDiv).display === 'none') {
      setText((text) => text + str)
    } else {
      setChatText((text) => text + str)
    }
  }

  const openWebSocket = () => {
    if (connecting()) {
      return
    }
    setConnecting(true)
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${protocol}://${document.location.host}/play`)
    setWs(ws)
    ws.onopen = () => {
      clearInterval(connectInterval())
      setConnectInterval(null)
      setConnecting(false)
      setReadyInterval(
        setInterval(() => {
          if (ws.readyState !== WebSocket.OPEN) {
            clearInterval(readyInterval())
            return
          }
          ws.send(JSON.stringify({ type: 'ready', data: '' }))
        }, 100)
      )
    }
    ws.onmessage = ({ data }) => {
      const message = JSON.parse(data)
      if (message.type == 'error') {
        setText((text) => text + '\x1b[31m' + message.data + '\x1b[0m\n')
        setWs(null)
        setReady(false)
        clearInterval(readyInterval())
        setReadyInterval(null)
      } else if (message.type == 'game') {
        setText((text) => text + message.data + '\n')
        if (!ready()) {
          clearInterval(readyInterval())
          setReadyInterval(null)
          sendChatText(
            '\x1b[92mYou are connected to the global chat channel.\x1b[0m\n'
          )
          setReady(true)
        }
      } else if (message.type === 'suggestion') {
        setSuggestion(message.data)
        if (!ready()) {
          clearInterval(readyInterval())
          setReadyInterval(null)
          sendChatText(
            '\x1b[92mYou are connected to the global chat channel.\x1b[0m\n'
          )
          setReady(true)
        }
      } else if (message.type === 'autocomplete') {
        clearInterval(readyInterval())
        setReadyInterval(null)
        if (message.data.length > 0) {
          setInput(message.data)
          setSuggestion('')
        }
      } else if (message.type === 'chat') {
        sendChatText(message.data)
      }
    }
    ws.onclose = () => {
      clearInterval(pingInterval())
      setPingInterval(null)
      setReady(false)
      clearInterval(readyInterval())
      setReadyInterval(null)
      setWs(null)
    }
  }

  createEffect(() => {
    const webSocket = ws()
    if (webSocket && ready()) {
      setPingInterval(
        setInterval(() => {
          if (ws() && ws().readyState !== WebSocket.OPEN) {
            setPingInterval(null)
            return
          }
          ws().send(JSON.stringify({ type: 'ping', data: '' }))
        }, 5000)
      )
    } else if (
      !webSocket ||
      (webSocket.readyState !== WebSocket.OPEN && !connecting())
    ) {
      setReady(false)
      if (connectInterval() === null) {
        setConnectInterval(
          setInterval(() => {
            openWebSocket()
          }, 1000 * Math.min(30, Math.pow(2, retries())))
        )
      }
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
          <div class='w-full' />
          <Show when={user.is_admin}>
            <a
              class='md:mt-auto p-4 transition-colors hover:bg-zinc-700'
              href='#'
              onClick={(e) => {
                e.preventDefault()
                setAdminModal(true)
              }}
            >
              <FontAwesomeIcon className='fa-fw' icon='cog' />
            </a>
          </Show>
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
        </nav>
        <div class='flex-1 h-1 md:h-auto'>
          <Terminal
            hasAutocomplete={true}
            screen={{ text: text(), scrollOnChange: true }}
            value={input()}
            autocomplete={suggestion()}
            onSend={(cmd: string, mode: number) => {
              if (cmd.startsWith('>') || mode === 1) {
                if (cmd.startsWith('>')) {
                  cmd = cmd.substring(1)
                }
                ws().send(
                  JSON.stringify({
                    type: 'game',
                    data: `say ${cmd}`,
                  })
                )
                setInput('')
                setSuggestion('')
                return
              }
              setText((text) => text + '> ' + cmd + '\n')
              ws().send(JSON.stringify({ type: 'game', data: cmd }))
              setInput('')
              setSuggestion('')
            }}
            onChange={(cmd: string, mode: number) => {
              setInput(cmd)
              if (mode === 0) {
                let sock = ws()
                if (sock) {
                  sock.send(
                    JSON.stringify({ type: 'autocomplete_suggest', data: cmd })
                  )
                }
              }
            }}
            onSuggest={(cmd: string, mode: number) => {
              if (mode === 0) {
                let sock = ws()
                if (sock) {
                  sock.send(
                    JSON.stringify({ type: 'autocomplete_get', data: cmd })
                  )
                }
              }
            }}
            modes={[{ icon: 'gamepad' }, { icon: 'comment' }]}
          />
        </div>
        <div
          class='w-96 flex-col border-l border-zinc-800 hidden lg:flex'
          ref={chatDiv}
        >
          <Terminal
            hasAutocomplete={false}
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
