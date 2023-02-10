import React, { FC, useEffect, useState, useRef, MutableRefObject } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import cx from 'classnames'

const ANSI_REGEX_RAW = /\x1b\[\d+?\m/g
const ANSI_REGEX_GROUP = /\x1b\[(\d+?)\m/g
const ANSI_COLOURS = {
  '30': '#18181b',
  '31': 'rgb(153 27 27)',
  '32': '#4d7c0f',
  '33': '#eab308',
  '34': '#1e40af',
  '35': '#6b21a8',
  '36': '#0284c7',
  '37': 'rgb(209, 213, 219)',
  '90': '#71717a',
  '91': '#f87171',
  '92': '#bef264',
  '93': '#fef08a',
  '94': '#93c5fd',
  '95': '#d8b4fe',
  '96': '#7dd3fc',
  '97': '#ffffff',
}

const TerminalScreen: FC<{
  text: string
  className?: string
  scrollOnChange?: boolean
}> = function TerminalScreen(props) {
  const className = cx(
    props.className,
    'flex-1',
    'p-4',
    'font-mono',
    'whitespace-pre-wrap',
    'text-gray-300',
    'overflow-y-auto'
  )
  const endRef = useRef(null)
  const splits = [...props.text.matchAll(ANSI_REGEX_GROUP)].map(
    (item) => item[1]
  )
  splits.unshift('0')
  const colourisation = props.text.split(ANSI_REGEX_RAW).map((item, idx) => {
    return (
      <span key={idx} style={{ color: ANSI_COLOURS[splits[idx]] }}>
        {item}
      </span>
    )
  })
  useEffect(() => {
    if (props.scrollOnChange) {
      endRef.current?.scrollIntoView({ behaviour: 'smooth' })
    }
  }, [props.text])
  return (
    <div className={className}>
      {colourisation}
      <div ref={endRef} />
    </div>
  )
}

const TerminalInput: FC<{
  value: string
  onSend?: (input: string) => void
  onChange?: (input: string) => void
  onSuggest?: (input: string) => void
  focusOnLoad?: boolean
  autocomplete?: string
  useHistory?: boolean
}> = function TerminalInput(props) {
  const [state, setState] = useState<{
    history: Array<string>
    historyIndex: number
  }>({
    history: [],
    historyIndex: -1,
  })
  const inRef = useRef<HTMLInputElement>()
  useEffect(() => {
    if (props.focusOnLoad) {
      inRef.current?.focus()
    }
  }, [])
  useEffect(() => {
    inRef.current?.setSelectionRange(props.value.length, props.value.length)
  }, [props.value])
  return (
    <div className='flex items-center bg-zinc-800 border-l border-zinc-900'>
      <div className='relative w-full'>
        <div className='absolute left-0 right-0 top-0 bottom-0 p-4 text-gray-300/40 font-mono overflow-hidden'>
          {props.autocomplete?.endsWith(':hidden') ? '' : props.autocomplete}
        </div>
        <input
          value={props.value}
          ref={inRef}
          className='w-full p-4 relative text-gray-300 bg-transparent outline-none font-mono z-10'
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              props.onSend?.call(null, props.value)
              if (
                props.useHistory &&
                props.value !== state.history[state.history.length - 1]
              ) {
                setState((state) => ({
                  ...state,
                  history: [...state.history, props.value],
                  historyIndex: -1,
                }))
              }
            } else if (e.key === 'Tab') {
              e.preventDefault()
              if (props.value?.length > 0) {
                props.onSuggest?.call(null, props.value)
              }
            } else if (e.key === 'ArrowUp' && state.history.length > 0) {
              e.preventDefault()
              let idx = Math.max(
                0,
                state.historyIndex === -1
                  ? state.history.length - 1
                  : state.historyIndex - 1
              )
              props.onChange?.call(null, state.history[idx])
              setState((state) => ({ ...state, historyIndex: idx }))
            } else if (e.key === 'ArrowDown' && state.history.length > 0) {
              e.preventDefault()
              let idx = Math.min(
                state.history.length - 1,
                state.historyIndex >= state.history.length
                  ? 0
                  : state.historyIndex + 1
              )
              props.onChange?.call(null, state.history[idx])
              setState((state) => ({ ...state, historyIndex: idx }))
            }
          }}
          onChange={(e) => {
            props.onChange?.call(null, e.target.value)
          }}
        />
      </div>
      <a
        className='p-4 text-zinc-700 hover:text-zinc-500 hover:cursor-pointer transition-colors'
        onClick={() => {
          props.onSend?.call(null, props.value)
          inRef.current?.focus()
        }}
      >
        <FontAwesomeIcon icon='paper-plane' />
      </a>
    </div>
  )
}

const Terminal: FC<{
  className?: string
  value: string
  screen?: { className?: string; text: string; scrollOnChange?: boolean }
  onSend?: (input: string) => void
  onChange?: (input: string) => void
  onSuggest?: (input: string) => void
  input?: {
    autocomplete?: string
    focusOnLoad: boolean
    ref?: MutableRefObject<HTMLInputElement>
  }
  useHistory?: boolean
}> & {
  Input: typeof TerminalInput
  Screen: typeof TerminalScreen
} = function Terminal({
  className,
  screen,
  input,
  onSend,
  onChange,
  onSuggest,
  value,
  useHistory,
}) {
  const calcClassName = cx('flex', 'flex-col', className)
  return (
    <div className={calcClassName}>
      <TerminalScreen {...screen} />
      <TerminalInput
        value={value}
        onSend={onSend}
        onChange={onChange}
        onSuggest={onSuggest}
        useHistory={useHistory}
        {...input}
      />
    </div>
  )
}

Terminal.Input = TerminalInput
Terminal.Screen = TerminalScreen

export default Terminal
