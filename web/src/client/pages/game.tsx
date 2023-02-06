import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { FontAwesomeIcon as Icon } from '@fortawesome/react-fontawesome'
import { useUser } from '../user'
import WebSocketConnector, { useWebSocket } from '../websocket'

const ANSI_REGEX_RAW = /\x1b\[\d+?\m/g
const ANSI_REGEX_GROUP = /\x1b\[(\d+?)\m/g
const ANSI_COLOURS = {
  '33': '#15803d',
  '37': 'rgb(209, 213, 219)',
}

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

  const splits = [...state.terminal.matchAll(ANSI_REGEX_GROUP)].map(
    (item) => item[1]
  )
  splits.unshift('0')
  const colourisation = state.terminal
    .split(ANSI_REGEX_RAW)
    .map((item, idx) => {
      return (
        <span key={idx} style={{ color: ANSI_COLOURS[splits[idx]] }}>
          {item}
        </span>
      )
    })
  return (
    <div className='mx-autp h-full lg:p-4'>
      <div className='mx-auto h-full lg:p-4 lg:w-[960px] bg-zinc-800 lg:rounded-xl flex flex-col lg:gap-3'>
        <div className='p-4 lg:h-[640px] bg-zinc-900 text-gray-300 lg:rounded-xl whitespace-pre-wrap font-mono overflow-auto flex-1'>
          {colourisation}
          <div ref={endRef} />
        </div>
        <div className='bg-zinc-800 lg:bg-zinc-900 lg:rounded-xl flex items-center'>
          <input
            ref={inputRef}
            value={state.input}
            className='w-full p-4 bg-zinc-800 lg:bg-zinc-900 text-gray-300 outline-none font-mono lg:rounded-xl'
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
          <a className='p-4 text-zinc-700 hover:text-zinc-400 hover:cursor-pointer'>
            <Icon icon='paper-plane' />
          </a>
        </div>
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
