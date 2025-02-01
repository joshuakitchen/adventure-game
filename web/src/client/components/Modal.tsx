import { Component, JSX, ParentProps, Show, splitProps } from 'solid-js'
import { Portal } from 'solid-js/web'
import { cx } from '../util'

export const Modal: Component<
  ParentProps<{
    open?: boolean
    trigger?: JSX.Element
  }> &
    JSX.HTMLAttributes<HTMLDivElement>
> = (props) => {
  const [local, other] = splitProps(props, [
    'open',
    'trigger',
    'class',
    'children',
  ])
  const cls = cx(
    'fixed',
    'w-full',
    'h-full',
    'flex',
    'flex-col',
    'text-gray-300',
    'bg-zinc-900',

    'md:left-1/2',
    'md:top-1/2',
    'md:-translate-x-1/2',
    'md:-translate-y-1/2',
    'md:w-3/4',
    'md:h-3/4',
    'md:shadow-md',
    'md:rounded-md',
    local.class
  )

  return (
    <>
      {local.trigger}
      <Show when={local.open}>
        <Portal mount={document.getElementById('modal-container')}>
          <div class='fixed left-0 top-0 w-screen h-screen bg-black/60 font-mono pointer-events-auto z-1000'>
            <div class={cls} {...other}>
              {local.children}
            </div>
          </div>
        </Portal>
      </Show>
    </>
  )
}

export default Modal
