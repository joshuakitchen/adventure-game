import { Component, createEffect, createSignal, For, Show } from 'solid-js'
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
  onSend?: (input: string, mode: number) => void
  onChange?: (input: string, mode: number) => void
  onSuggest?: (input: string, mode: number) => void
  hasAutocomplete?: boolean
  modes?: Array<{ icon?: string }>
}> = (props) => {
  const [mode, setMode] = createSignal<number>(0)
  let inRef: HTMLInputElement
  return (
    <div class='flex items-center bg-zinc-800 border-l border-zinc-900'>
      <For each={props.modes}>
        {(item, idx) => (
          <a
            class={cx(
              'block lg:hidden p-4 text-zinc-700 hover:text-zinc-500 hover:cursor-pointer transition-colors',
              {
                hidden: mode() !== idx(),
              }
            )}
            onClick={() => {
              setMode((mode() + 1) % props.modes.length)
            }}
          >
            <FontAwesomeIcon icon={item.icon} />
          </a>
        )}
      </For>
      <div class='relative flex flex-1'>
        <div class='absolute flex left-0 right-0 top-0 bottom-0 p-4 text-gray-300/40 font-mono overflow-hidden'>
          {props.autocomplete?.endsWith(':hidden') ? '' : props.autocomplete}
        </div>
        <input
          value={props.value}
          ref={inRef}
          class='flex-1 p-4 relative text-gray-300 bg-transparent outline-none font-mono z-10'
          autocapitalize='off'
          autocomplete='off'
          autocorrect='off'
          onKeyDown={(e) => {
            if (e.key === 'Enter' && props.onSend && inRef.value !== '') {
              props.onSend.call(null, inRef.value, mode())
            } else if (e.key === 'Tab' && props.onSuggest) {
              e.preventDefault()
              props.onSuggest.call(null, inRef.value, mode())
            } else {
              let val = inRef.value
              if (props.onChange) {
                props.onChange.call(null, val, mode())
              }
            }
          }}
          onInput={(e) => {
            props.onChange?.call(null, e.target.value, mode())
          }}
        />
      </div>
      <Show when={props.hasAutocomplete === true}>
        <a
          class='block lg:hidden p-4 text-zinc-700 hover:text-zinc-500 hover:cursor-pointer transition-colors'
          onClick={(e) => {
            e.preventDefault()
            if (inRef.value === '') {
              return
            }
            props.onSuggest?.call(null, inRef.value, mode())
            if (inRef) {
              inRef.focus()
            }
          }}
        >
          <FontAwesomeIcon icon='chevron-right' />
        </a>
      </Show>
      <a
        class='p-4 text-zinc-700 hover:text-zinc-500 hover:cursor-pointer transition-colors'
        onClick={() => {
          if (inRef.value === '') {
            return
          }
          props.onSend?.call(null, inRef.value, mode())
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
    scrollOnChange?: boolean
  }
  value: string
  autocomplete?: string
  hasAutocomplete?: boolean
  onSend?: (input: string, mode: number) => void
  onChange?: (input: string, mode: number) => void
  onSuggest?: (input: string, mode: number) => void
  modes?: Array<{ icon?: string }>
}> = (props) => {
  return (
    <div class='flex flex-col h-full'>
      <TerminalScreen {...props.screen} />
      <TerminalInput
        value={props.value}
        autocomplete={props.autocomplete}
        hasAutocomplete={props.hasAutocomplete}
        onSend={props.onSend}
        onChange={props.onChange}
        onSuggest={props.onSuggest}
        modes={props.modes}
      />
    </div>
  )
}

export default Terminal
