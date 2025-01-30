import { Component, createEffect, createSignal, For } from 'solid-js'
import { cx } from '../util'
import { Properties } from 'solid-js/web'
import { FontAwesomeIcon } from 'solid-fontawesome'

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

export const TerminalScreen: Component<{
  text: string
  class?: string
  scrollOnChange?: boolean
}> = (props) => {
  const cls = cx(
    props.class,
    'flex-1',
    'p-4',
    'font-mono',
    'whitespace-pre-wrap',
    'text-gray-300',
    'overflow-y-auto'
  )
  let endRef: HTMLDivElement
  createEffect(() => {
    props.text
    if (props.scrollOnChange) {
      endRef.scrollIntoView({ behavior: 'smooth' })
    }
  })
  return (
    <div class={cls}>
      <For each={props.text.split(ANSI_REGEX_RAW)}>
        {(item, idx) => {
          const splits = [...props.text.matchAll(ANSI_REGEX_GROUP)].map(
            (item) => item[1]
          )
          splits.unshift('0')
          return (
            <span style={{ color: ANSI_COLOURS[splits[idx()]] }}>{item}</span>
          )
        }}
      </For>
      <div ref={endRef}></div>
    </div>
  )
}

export const TerminalInput: Component<{
  value?: string
  autocomplete?: string
  onSend?: (input: string) => void
  onChange?: (input: string) => void
}> = (props) => {
  let inRef: HTMLInputElement
  return (
    <div class='flex items-center bg-zinc-800 border-l border-zinc-900'>
      <div class='relative w-full'>
        <div class='absolute left-0 right-0 top-0 bottom-0 p-4 text-gray-300/40 font-mono overflow-hidden'>
          {props.autocomplete?.endsWith(':hidden') ? '' : props.autocomplete}
        </div>
        <input
          value={props.value}
          ref={inRef}
          class='w-full p-4 relative text-gray-300 bg-transparent outline-none font-mono z-10'
          autocapitalize='off'
          autocomplete='off'
          autocorrect='off'
          onKeyDown={(e) => {
            if (e.key === 'Enter' && props.onSend) {
              props.onSend.call(null, inRef.value)
            } else {
              let val = inRef.value
              if (props.onChange) {
                props.onChange.call(null, val)
              }
            }
          }}
          onInput={(e) => {
            props.onChange?.call(null, e.target.value)
          }}
        />
      </div>
      <a
        class='p-4 text-zinc-700 hover:text-zinc-500 hover:cursor-pointer transition-colors'
        onClick={() => {
          props.onSend?.call(null, inRef.value)
          if (inRef) {
            inRef.focus()
          }
        }}
      >
        <FontAwesomeIcon icon='paper-plane' />
      </a>
    </div>
  )
}

export const Terminal: Component<{
  screen: {
    text: string
  }
  value: string
  autocomplete?: string
  onSend?: (input: string) => void
  onChange?: (input: string) => void
  ref?: HTMLInputElement
}> = (props) => {
  return (
    <div class='flex flex-col h-full'>
      <TerminalScreen {...props.screen} />
      <TerminalInput
        value={props.value}
        autocomplete={props.autocomplete}
        onSend={props.onSend}
        onChange={props.onChange}
      />
    </div>
  )
}

export default Terminal
