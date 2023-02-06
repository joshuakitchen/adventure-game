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
    [(handler: (data: string) => void) => void, (data: string) => void]
  >(null)

export function useWebSocket() {
  return useContext(WebSocketContext)
}

const WebSocketConnector: FC<{ url: string } & PropsWithChildren> =
  function WebSocketConnector(props) {
    const [{ ws, handlers, queued }, setState] = useState<{
      ws: WebSocket
      handlers: Array<(data: any) => void>
      queued: Array<any>
    }>({
      ws: null,
      handlers: [],
      queued: [],
    })
    useEffect(() => {
      const ws = new WebSocket(props.url)
      ws.onopen = () => {
        setState((state) => ({ ...state, ws }))
      }
      ws.onmessage = ({ data }) => {
        handlers.forEach((item) => item(data))
      }
      return () => {
        ws.close()
        setState((state) => ({ ...state, ws: null }))
      }
    }, [])
    useEffect(() => {
      if (ws) {
        ws.onmessage = ({ data }) => {
          handlers.forEach((item) => item(data))
        }
        setState((state) => {
          state.queued.forEach((item) => ws.send(item))
          return { ...state, queued: [] }
        })
      }
    }, [ws, handlers])
    return (
      <WebSocketContext.Provider
        value={[
          (handler) => {
            setState((state) => {
              const handlers = [...state.handlers]
              handlers.push(handler)
              return { ...state, handlers }
            })
          },
          (data: string) => {
            if (ws) {
              ws.send(data)
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
