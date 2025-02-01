import { Modal, Table } from '@components'
import axios from 'axios'
import { FontAwesomeIcon } from 'solid-fontawesome'
import {
  Component,
  createEffect,
  createSignal,
  JSXElement,
  onMount,
  Show,
} from 'solid-js'

export const BugModal: Component<{
  trigger?: JSXElement
}> = (props) => {
  const [open, setOpen] = createSignal(false)
  const [trigger, setTrigger] = createSignal<HTMLElement | null>(
    props.trigger as HTMLElement
  )
  const [details, setDetails] = createSignal('')
  const [error, setError] = createSignal<string>()
  const [submitted, setSubmitted] = createSignal(false)
  const [submitDisabled, setSubmitDisabled] = createSignal(true)

  const openModal = () => {
    setOpen(true)
  }

  createEffect(() => {
    const trigger = props.trigger as HTMLElement
    if (trigger) {
      setTrigger((prev) => {
        if (prev) {
          prev.removeEventListener('click', openModal)
        }
        let clone = trigger.cloneNode(true) as HTMLElement
        clone.addEventListener('click', openModal)
        return clone
      })
    } else {
      setTrigger((prev) => {
        if (prev) {
          prev.removeEventListener('click', openModal)
        }
        return null
      })
    }
  })

  createEffect(() => {
    if (!open()) {
      setSubmitted(false)
    }
  })

  return (
    <>
      <Modal open={open()} trigger={trigger()}>
        <div class='p-4 text-gray-200 border-b border-zinc-800 font-mono'>
          <FontAwesomeIcon icon='bug' className='fa-fw pr-4' />
          Report a Bug
        </div>
        <div class='p-4 text-zinc-500'>
          Please give as much detail as possible to the bug or issue you've
          found in the textbox below.
        </div>
        <div class='px-4 pb-4 flex-1'>
          <textarea
            class='w-full h-full resize-none p-4 bg-zinc-800 outline-none font-mono'
            onInput={(e) => {
              setSubmitDisabled((e.target as HTMLTextAreaElement).value === '')
              setDetails((e.target as HTMLTextAreaElement).value)
            }}
          >
            {details()}
          </textarea>
        </div>
        <Show when={error()}>
          <div class='px-4 pb-4 text-red-500'>{error()}</div>
        </Show>
        <Show
          when={submitted()}
          fallback={<div class='px-4 pb-4 text-zinc-500'>&nbsp;</div>}
        >
          <div class='px-4 pb-4 text-zinc-200 text-right'>
            The bug report has been submitted, you can now close this modal.
          </div>
        </Show>
        <div class='grid grid-cols-2 md:grid-cols-4 gap-8'>
          <button
            class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:1] md:[grid-column:3] hover:bg-zinc-700 transition-colors md:rounded-br'
            onClick={() => {
              setOpen(false)
            }}
          >
            Close
          </button>
          <button
            class='p-4 bg-zinc-800 cursor-pointer [grid-row:1] [grid-column:2] md:[grid-column:4] hover:bg-zinc-700 transition-colors md:rounded-br disabled:hover:cursor-not-allowed disabled:bg-zinc-900'
            disabled={submitDisabled()}
            onClick={() => {
              if (submitDisabled()) return
              setSubmitDisabled(true)
              axios
                .post('/api/v1/bugreports', {
                  description: details(),
                })
                .then((res) => {
                  setSubmitted(true)
                })
                .catch((err) => {
                  setError('An error occurred while submitting the bug report.')
                })
            }}
          >
            Submit
          </button>
        </div>
      </Modal>
    </>
  )
}

export default BugModal
