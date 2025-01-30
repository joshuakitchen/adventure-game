import { Component, ParentProps } from 'solid-js'
import { cx } from '../util'

export const TableHeader: Component<ParentProps<{ class?: string }>> = (
  props
) => {
  const cls = cx(
    props.class,
    'p-4',
    'font-normal',
    'text-zinc-500',
    'border-b',
    'border-zinc-800'
  )
  return <th class={cls}>{props.children}</th>
}

export const TableCell: Component<ParentProps<{ class?: string }>> = (
  props
) => {
  const cls = cx(props.class, 'px-4', 'py-2', 'border-b', 'border-b-zinc-800')
  return <td class={cls}>{props.children}</td>
}

export const TableRow: Component<ParentProps<{ class?: string }>> = (props) => {
  const cls = cx(props.class)
  return <tr class={cls}>{props.children}</tr>
}

export const TableBody: Component<ParentProps<{ class?: string }>> = (
  props
) => {
  const cls = cx(props.class)
  return <tbody class={cls}>{props.children}</tbody>
}

export const TableHead: Component<ParentProps<{ class?: string }>> = (
  props
) => {
  const cls = cx(props.class, 'text-left')
  return <thead class={cls}>{props.children}</thead>
}

export const Table: Component<ParentProps<{ class?: string }>> & {
  Head: typeof TableHead
  Body: typeof TableBody
  Row: typeof TableRow
  Cell: typeof TableCell
  Header: typeof TableHeader
} = (props) => {
  const cls = cx(props.class, 'min-w-full')
  return <table class={cls}>{props.children}</table>
}

Table.Head = TableHead
Table.Body = TableBody
Table.Row = TableRow
Table.Cell = TableCell
Table.Header = TableHeader

export default Table
