import { Component, JSX, ParentProps, splitProps } from 'solid-js'
import { cx } from '../util'

export const Button: Component<
  ParentProps<{}> & JSX.HTMLAttributes<HTMLButtonElement>
> = function Button(props) {
  const [local, others] = splitProps(props, ['class'])
  const cls = cx(
    'py-2 bg-zinc-800 hover:bg-zinc-700 ease-in-out transition-all font-mono hover:cursor-pointer',
    local.class
  )
  return <button class={cls} {...others} />
}

export default Button
