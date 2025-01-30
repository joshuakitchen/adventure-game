import {
  Component,
  createContext,
  ParentProps,
  useContext,
  type JSX,
} from 'solid-js'
import { createStore, SetStoreFunction } from 'solid-js/store'

export type UserData = { id: string; email: string; is_admin: boolean }
export type UserContextData = [UserData, SetStoreFunction<UserData>]

const UserContext = createContext<UserContextData>()

const getMetaTag = function getMetaTag(name: string): any {
  const tags = document.getElementsByTagName('meta')
  for (let i = 0; i < tags.length; i++) {
    if (tags[i].getAttribute('name') !== name) continue
    const data = JSON.parse(atob(tags[i].getAttribute('content')))
    tags[i].remove()
    return data
  }
  return null
}

export const UserProvider: Component<ParentProps<{}>> = (props: {
  children: JSX.Element
}) => {
  const [state, setState] = createStore<UserData>(getMetaTag('user'))

  return (
    <UserContext.Provider value={[state, setState]}>
      {props.children}
    </UserContext.Provider>
  )
}

export const useUser = (): UserContextData => {
  return useContext(UserContext)
}
