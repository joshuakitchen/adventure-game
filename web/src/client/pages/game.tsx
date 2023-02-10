import React, { FC, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import {
  FontAwesomeIcon,
  FontAwesomeIcon as Icon,
} from '@fortawesome/react-fontawesome'
import { Terminal } from '@components'
import { useUser } from '../user'
import axios from 'axios'
import WebSocketConnector, { useWebSocket } from '../websocket'
import { AdminModal } from '@modals'

const GamePageInner = function GamePageInner() {
  const [user, setUser] = useUser()
  const [
    {
      gameAutocomplete,
      gameText,
      gameInput,
      chatText,
      chatInput,
      isReady,
      readyAttempts,
      timeout,
    },
    setState,
  ] = useState({
    gameText: '',
    gameInput: '',
    gameAutocomplete: '',
    chatText: '',
    chatInput: '',
    isReady: false,
    readyAttempts: 0,
    timeout: null,
  })
  const [socketState, addMessageHandler, sendMessage] = useWebSocket()
  useEffect(() => {
    addMessageHandler((message) => {
      if (message.type === 'error') {
        if (message.data === 'Incorrect email or password') {
          window.location.href = '/logout'
        } else {
          setState((state) => ({
            ...state,
            gameText: state.gameText + '\x1b[31m' + message.data + '\x1b[0m\n',
          }))
        }
        return
      } else if (message.type === 'game') {
        setState((state) => ({
          ...state,
          gameText: state.gameText + message.data,
          chatText: !state.isReady
            ? '\x1b[92mYou are connected to the global chat channel.\x1b[0m\n'
            : state.chatText,
          isReady: true,
          readyAttempts: 0,
        }))
      } else if (message.type === 'suggestion') {
        setState((state) => ({ ...state, gameAutocomplete: message.data }))
      } else if (message.type === 'autocomplete') {
        if (message.data.length > 0) {
          setState((state) => ({
            ...state,
            gameInput: message.data,
            gameAutocomplete: '',
          }))
        }
      } else if (message.type == 'chat') {
        setState((state) => ({
          ...state,
          chatText: state.chatText + message.data,
        }))
      }
    })
  }, [])
  useEffect(() => {
    if (socketState === 'open' && !isReady) {
      if (readyAttempts === 0) {
        sendMessage({ type: 'ready' })
      }
    } else if (socketState === 'closed') {
      setState((state) => ({ ...state, isReady: false }))
    }
  }, [socketState, isReady])
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
          value={gameInput}
          className='h-full'
          screen={{ text: gameText, scrollOnChange: true }}
          input={{
            autocomplete: gameAutocomplete,
            focusOnLoad: true,
          }}
          onSend={(input) => {
            if (input.length > 0) {
              if (input.indexOf('clear') === 0 || input.indexOf('cls') === 0) {
                setState((state) => ({
                  ...state,
                  gameAutocomplete: '',
                  gameText: '',
                  gameInput: '',
                }))
              } else {
                setState((state) => ({
                  ...state,
                  gameText: state.gameText + '> ' + input + '\n',
                  gameAutocomplete: '',
                  gameInput: '',
                }))
                sendMessage({ type: 'game', data: input })
              }
            }
          }}
          onChange={(input) => {
            setState((state) => ({ ...state, gameInput: input }))
            sendMessage({ type: 'autocomplete_suggest', data: input })
          }}
          onSuggest={(input) => {
            sendMessage({ type: 'autocomplete_get', data: input })
          }}
          useHistory
        />
      </div>
      <div className='w-96 flex-col border-l border-zinc-800 hidden lg:flex'>
        <div className='border-b border-zinc-800 flex-1'>
          <Terminal.Screen text={'\x1b[33mTest'} />
        </div>
        <Terminal
          value={chatInput}
          className='flex-1'
          onChange={(text) => {
            setState((state) => ({ ...state, chatInput: text }))
          }}
          onSend={(message) => {
            sendMessage({ type: 'game', data: `say ${message}` })
            setState((state) => ({ ...state, chatInput: '' }))
          }}
          screen={{
            text: chatText,
          }}
        />
      </div>
    </div>
  )
}

const GamePage: FC<{}> = function GamePage() {
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
      <AdminModal />
      <GamePageInner />
    </WebSocketConnector>
  )
}

export default GamePage
