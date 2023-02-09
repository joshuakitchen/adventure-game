import React, {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useEffect,
  useState,
} from 'react'

const WebSocketContext =
  createContext<
    [
      string,
      (handler: (data: { type: string; data: string }) => void) => void,
      (data: any) => void
    ]
  >(null)

export function useWebSocket() {
  return useContext(WebSocketContext)
}

const WebSocketConnector: FC<{ url: string } & PropsWithChildren> =
  function WebSocketConnector(props) {
    const [{ ws, handlers, queued, in_queue, retryAttempts }, setState] =
      useState<{
        ws: WebSocket
        handlers: Array<(data: any) => void>
        queued: Array<any>
        in_queue: Array<any>
        retryAttempts: number
      }>({
        ws: null,
        handlers: [],
        queued: [],
        in_queue: [],
        retryAttempts: 0,
      })
    useEffect(() => {
      if (ws === null) {
        const connect = function _connect() {
          const ws = new WebSocket(props.url)
          ws.onopen = () => {
            setState((state) => ({ ...state, ws }))
          }
          ws.onmessage = ({ data }) => {
            setState((state) => {
              state.handlers.forEach((item) => item(JSON.parse(data)))
              return { ...state, retryAttempts: 0 }
            })
          }
          ws.onclose = () => {
            setState((state) => ({
              ...state,
              ws: null,
              retryAttempts: state.retryAttempts + 1,
            }))
          }
        }
        if (retryAttempts === 0) {
          connect()
        } else {
          setTimeout(connect, Math.min(retryAttempts * 500, 15000))
        }
      }
      return () => {
        if (ws !== null) {
          ws.close()
          setState((state) => ({ ...state, ws: null }))
        }
      }
    }, [ws])
    useEffect(() => {
      if (ws) {
        ws.onmessage = ({ data }) => {
          if (handlers.length == 0) {
            setState((state) => ({
              ...state,
              in_queue: [...state.in_queue, JSON.parse(data)],
            }))
          } else {
            handlers.forEach((item) => item(JSON.parse(data)))
          }
        }
        setState((state) => {
          state.queued.forEach((item) => ws.send(JSON.stringify(item)))
          return { ...state, queued: [] }
        })
      }
    }, [ws, handlers])
    return (
      <WebSocketContext.Provider
        value={[
          ws === null
            ? 'closed'
            : ws.readyState === ws.OPEN
            ? 'open'
            : 'connecting',
          (handler) => {
            setState((state) => {
              if (state.in_queue.length > 0) {
                state.in_queue.forEach((item) => handler(item))
              }
              const handlers = [...state.handlers]
              handlers.push(handler)
              return { ...state, handlers, in_queue: [] }
            })
          },
          (data: string) => {
            if (ws) {
              ws.send(JSON.stringify(data))
            } else {
              setState((state) => {
                const queued = [...state.queued, data]
                return { ...state, queued }
              })
            }
          },
        ]}
      >
        {props.children}
      </WebSocketContext.Provider>
    )
  }

export default WebSocketConnector
