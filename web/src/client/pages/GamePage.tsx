import {
  Component,
  createEffect,
  createSignal,
  onCleanup,
  onMount,
  Show,
} from 'solid-js'
import { FontAwesomeIcon } from 'solid-fontawesome'
import { useUser } from '../user'
import { useNavigate } from '@solidjs/router'
import axios from 'axios'
import { Terminal } from '../components/Terminal'
import { AdminModal, BugModal } from '../modals'

const PING_INTERVAL = 300

export const GamePage: Component = () => {
  const navigate = useNavigate()
  const [user, setUser] = useUser()
  const [text, setText] = createSignal<string>('')
  const [suggestion, setSuggestion] = createSignal<string>('')
  const [input, setInput] = createSignal<string>('')
  const [chatText, setChatText] = createSignal<string>('')
  const [chatInput, setChatInput] = createSignal<string>('')
  const [adminModal, setAdminModal] = createSignal(false)

  const [ws, setWs] = createSignal<WebSocket>()
  const [retries, setRetries] = createSignal(0)
  const [pingInterval, setPingInterval] = createSignal<number | null>(null)
  const [connectInterval, setConnectInterval] = createSignal<number | null>(
    null
  )
  const [connecting, setConnecting] = createSignal(false)
  const [pingSent, setPingSent] = createSignal(false)
  const [missedPongs, setMissedPongs] = createSignal(0)
  const [retryConnect, setRetryConnect] = createSignal(true)
  const [sessionId, setSessionId] = createSignal(crypto.randomUUID())
  const [settings, setSettings] = createSignal<any>({})

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

  const pingSocket = () => {
    let sock = ws()
    const prevPingAwaiting = pingSent()
    if (sock) {
      if (prevPingAwaiting) {
        setMissedPongs((missedPongs) => missedPongs + 1)
        if (missedPongs() > 3) {
          sock.close()
          setWs(null)
          return
        }
      }
      sock.send(JSON.stringify({ type: 'ping', data: '' }))
      setPingSent(true)
    }
  }

  const openWebSocket = () => {
    if (connecting()) {
      return
    }
    clearInterval(pingInterval())
    setPingInterval(null)
    setPingSent(false)
    setConnecting(true)
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(
      `${protocol}://${document.location.host}/play?session=${sessionId()}`
    )
    setWs(ws)
    ws.onopen = () => {
      clearInterval(connectInterval())
      setConnectInterval(null)
      setConnecting(false)
      setPingInterval(setInterval(pingSocket, PING_INTERVAL))
    }
    ws.onmessage = ({ data }) => {
      const message = JSON.parse(data)
      if (message.type == 'error') {
        setText((text) => text + '\x1b[31m' + message.data + '\x1b[0m\n')
        ws.close()
        setWs(null)

        // Only check retry flag for normal errors
        if (typeof message.retry !== 'undefined') {
          setRetryConnect(message.retry)
        }
      } else if (message.type == 'critical_error') {
        setText((text) => text + '\x1b[31m' + message.data + '\x1b[0m\n')
        ws.close()
        setWs(null)

        // Critical errors never retry
        setRetryConnect(false)

        // Redirect to login if it's an authentication error
        if (message.data === 'You must be logged in to play.') {
          navigate('/login')
        }
      } else if (message.type == 'game') {
        setText((text) => text + message.data + '\n')
      } else if (message.type === 'suggestion') {
        setSuggestion(message.data)
      } else if (message.type === 'autocomplete') {
        if (message.data.length > 0) {
          setInput(message.data)
          setSuggestion('')
        }
      } else if (message.type === 'chat') {
        sendChatText(message.data)
      } else if (message.type === 'pong') {
        setPingSent(false)
      } else if (message.type === 'setting') {
        const { setting, value } = message
        setSettings((settings) => ({ ...settings, [setting]: value }))
      }
    }
    ws.onclose = () => {
      setConnecting(false)
      clearInterval(pingInterval())
      setPingInterval(null)
      setPingSent(false)
      setWs(null)

      // Retry connection
      if (retryConnect()) {
        if (connectInterval() === null) {
          openWebSocket()
          setConnectInterval(setInterval(openWebSocket, 1000))
        }
      }
    }
    ws.onerror = () => {
      setConnecting(false)
      clearInterval(pingInterval())
      setPingInterval(null)
      setPingSent(false)
      setWs(null)
      if (retryConnect()) {
        if (connectInterval() === null) {
          openWebSocket()
          setConnectInterval(setInterval(openWebSocket, 1000))
        }
      }
    }
  }

  createEffect(() => {
    if (!user.id) {
      navigate('/login')
    }
  })

  onMount(() => {
    console.log(`sessionId: ${sessionId()}`)
    openWebSocket()
    setConnectInterval(setInterval(openWebSocket, 1000))
  })

  onCleanup(() => {
    clearInterval(pingInterval())
    clearInterval(connectInterval())
    if (ws()) {
      setRetryConnect(false)
      ws().close()
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
      <div class='mx-auto h-screen flex flex-col md:flex-row text-gray-300 overflow-y-hidden'>
        <nav class='flex flex-row md:flex-col border-l border-zinc-800 bg-zinc-800'>
          <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
            <FontAwesomeIcon className='fa-fw' icon='comments' />
          </a>
          <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
            <FontAwesomeIcon className='fa-fw' icon='circle-info' />
          </a>
          <BugModal
            trigger={
              <a class='p-4 transition-colors hover:bg-zinc-700' href='#'>
                <FontAwesomeIcon
                  className='fa-fw text-xl text-gray-300'
                  icon='bug'
                />
              </a>
            }
          />
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
            screen={{
              text: text(),
              scrollOnChange: true,
              scrollType: settings()?.scroll,
            }}
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
              if (cmd === 'clear') {
                setText('')
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
