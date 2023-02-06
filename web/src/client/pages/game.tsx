import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { FontAwesomeIcon as Icon } from '@fortawesome/react-fontawesome'
import { useUser } from '../user'
import WebSocketConnector, { useWebSocket } from '../websocket'

const GamePageInner = function GamePageInner() {
  const [state, setState] = useState({ terminal: '', input: '' })
  const [addMessageHandler, sendMessage] = useWebSocket()
  const inputRef = useRef(null)
  const endRef = useRef(null)
  useEffect(() => {
    addMessageHandler((message) => {
      setState((state) => ({ ...state, terminal: state.terminal + message }))
    })
    sendMessage('ready')
    inputRef.current?.focus()
  }, [])
  useEffect(() => {
    endRef.current?.scrollIntoView({ behaviour: 'smooth' })
  }, [state.terminal])
  return (
    <div className='mx-auto mt-4 p-4 w-[960px] bg-zinc-800 rounded-xl flex flex-col gap-3'>
      <div className='p-4 h-[640px] bg-zinc-900 text-gray-300 rounded-xl whitespace-pre-wrap font-mono overflow-auto'>
        {state.terminal}
        <div ref={endRef} />
      </div>
      <div className='p-4 bg-zinc-900 rounded-xl flex gap-3 items-center'>
        <input
          ref={inputRef}
          value={state.input}
          className='w-full bg-zinc-900 text-gray-300 outline-none font-mono'
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              setState((state) => {
                if (state.input === 'clear') {
                  return { ...state, input: '', terminal: '' }
                }
                sendMessage(state.input)
                return {
                  ...state,
                  input: '',
                  terminal: state.terminal + '> ' + state.input + '\n',
                }
              })
            } else if (e.key === 'Escape') {
              setState((state) => ({ ...state, input: '' }))
            }
          }}
          onChange={(e) => {
            setState((state) => {
              return { ...state, input: e.target.value }
            })
          }}
        />
        <Icon
          className='text-zinc-700 hover:text-zinc-400'
          icon='paper-plane'
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
  }, [])
  return (
    <WebSocketConnector url={`ws://${document.location.host}/play`}>
      <GamePageInner />
    </WebSocketConnector>
  )
}

export default GamePage
