import React, { FC } from 'react'
import { createPortal } from 'react-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const AdminModal: FC<{ visible?: boolean }> = function AdminModal({ visible }) {
  if (!visible) {
    return <></>
  }
  return createPortal(
    <div className='fixed w-screen h-screen bg-black/60 font-mono'>
      <div className='fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] h-1/2 flex flex-col text-gray-300 bg-zinc-900 shadow-md'>
        <div className='flex'>
          <a className='p-4 flex-1 bg-zinc-800'>
            <FontAwesomeIcon icon='users' className='pr-4' />
            Users
          </a>
          <a className='p-4 flex-1'>test</a>
          <a className='p-4 flex-1'>test</a>
          <a className='p-4 flex-1'>test</a>
          <a className='p-4 flex-1'>test</a>
        </div>
        <div className='p-4'>Other</div>
      </div>
    </div>,
    document.getElementById('modal-container')
  )
}

export default AdminModal
