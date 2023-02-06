import React, {
  createContext,
  FC,
  PropsWithChildren,
  useContext,
  useState,
} from 'react'

export type UserData = {}
export type UserContextData = [UserData, (UserData) => void]

const UserContext = createContext<UserContextData>(null)

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

export const UserProvider: FC<PropsWithChildren> = function UserProvider(
  props
) {
  const [state, setState] = useState<UserData>(getMetaTag('user'))
  return (
    <UserContext.Provider value={[state, setState]}>
      {props.children}
    </UserContext.Provider>
  )
}

export const useUser = function useUser(): UserContextData {
  return useContext(UserContext)
}
