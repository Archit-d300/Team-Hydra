module.exports = {
  apps: [
    {
      name: 'drought-frontend',
      script: 'npx',
      args: 'vite --port 3000 --host 0.0.0.0',
      cwd: '/home/user/webapp',
      env: {
        NODE_ENV: 'development',
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
    },
  ],
}
