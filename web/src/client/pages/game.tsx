import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import {
  FontAwesomeIcon,
  FontAwesomeIcon as Icon,
} from '@fortawesome/react-fontawesome'
import { Terminal } from '@components'
import { useUser } from '../user'
import axios from 'axios'
import WebSocketConnector, { useWebSocket } from '../websocket'

const GamePageInner = function GamePageInner() {
  const [user, setUser] = useUser()
  const [{ gameAutocomplete, gameText, chatText }, setState] = useState({
    gameText: '',
    gameAutocomplete: '',
    chatText: '',
  })
  const [addMessageHandler, sendMessage] = useWebSocket()
  useEffect(() => {
    addMessageHandler((message) => {
      if (message.type === 'error') {
        if (message.data === 'Incorrect email or password') {
          window.location.href = '/logout'
        }
        return
      } else if (message.type === 'game') {
        setState((state) => ({
          ...state,
          gameText: state.gameText + message.data,
        }))
      } else if (message.type === 'autocomplete') {
        setState((state) => ({ ...state, gameAutocomplete: message.data }))
      } else if (message.type === 'autocomplete:hidden') {
        setState((state) => ({
          ...state,
          gameAutocomplete: `${message.data}:hidden`,
        }))
      } else if (message.type == 'chat') {
        setState((state) => ({
          ...state,
          chatText: state.chatText + message.data,
        }))
      }
    })
    sendMessage({ type: 'ready' })
  }, [])
  return (
    <div className='mx-auto h-full flex flex-col md:flex-row text-gray-300'>
      <nav className='flex flex-row md:flex-col border-l border-zinc-800 bg-zinc-800'>
        <a className='p-4 transition-colors hover:bg-zinc-700' href='#'>
          <FontAwesomeIcon icon='terminal' fixedWidth />
        </a>
        <a className='p-4 transition-colors hover:bg-zinc-700' href='#'>
          <FontAwesomeIcon icon='comments' fixedWidth />
        </a>
        <a className='p-4 transition-colors hover:bg-zinc-700' href='#'>
          <FontAwesomeIcon icon='bug' fixedWidth />
        </a>
        <a
          className='p-4 transition-colors hover:bg-zinc-700 hover:cursor-pointer'
          onClick={(e) => {
            axios
              .get('/logout')
              .then(() => {
                setUser(null)
              })
              .catch((e) => {
                setUser(null)
              })
          }}
        >
          <FontAwesomeIcon icon='sign-out' fixedWidth />
        </a>
        <a className='mt-auto p-4 transition-colors hover:bg-zinc-700' href='#'>
          <FontAwesomeIcon icon='cog' fixedWidth />
        </a>
      </nav>
      <div className='flex-1 h-1 md:h-auto'>
        <Terminal
          className='h-full'
          screen={{ text: gameText, scrollOnChange: true }}
          input={{ autocomplete: gameAutocomplete, focusOnLoad: true }}
          onSend={(input) => {
            if (input.length > 0) {
              if (input.indexOf('clear') === 0 || input.indexOf('cls') === 0) {
                setState((state) => ({ ...state, gameText: '' }))
              } else {
                setState((state) => ({ ...state, gameAutocomplete: '' }))
                sendMessage({ type: 'game', data: input })
              }
            }
          }}
          onChange={(input) => {
            sendMessage({ type: 'autocomplete', data: input })
          }}
        />
      </div>
      <div className='w-96 flex-col border-l border-zinc-800 hidden lg:flex'>
        <div className='border-b border-zinc-800 flex-1'>
          <Terminal.Screen text={'\x1b[33mTest'} />
        </div>
        <Terminal
          className='flex-1'
          onSend={(message) => {
            sendMessage({ type: 'game', data: `say ${message}` })
          }}
          screen={{
            text: chatText,
          }}
        />
      </div>
    </div>
  )
}

const GamePage = function GamePage() {
  const [user, setUser] = useUser()
  const navigate = useNavigate()
  useEffect(() => {
    if (!user) {
      navigate('/login')
    }
  }, [user])
  if (!user) {
    return <div />
  }
  return (
    <WebSocketConnector
      url={`${document.location.protocol === 'https:' ? 'wss' : 'ws'}://${
        document.location.host
      }/play`}
    >
      <GamePageInner />
    </WebSocketConnector>
  )
}

export default GamePage
