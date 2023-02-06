import path from 'path'
import fs from 'fs'

export function getStaticPath() {
  if (fs.existsSync(path.resolve(process.cwd(), 'build', 'static'))) {
    return path.resolve(process.cwd(), 'build', 'static')
  }
  return path.resolve(process.cwd(), 'static')
}
