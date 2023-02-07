'use strict'

const path = require('path')
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin')

module.exports = (args, argv) => ({
  entry: ['./src/client/index.tsx', './src/client/style/index.css'],
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader'
      },
      {
        test: /\.css$/i,
        include: path.resolve(__dirname, 'src', 'client', 'style'),
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    plugins: [new TsconfigPathsPlugin({
      configFile: './src/client/tsconfig.json'
    })]
  },
  output: {
    path: path.resolve(__dirname, 'build', 'static')
  }
})
