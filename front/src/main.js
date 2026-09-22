import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/editorial.css'




const app = createApp(App)
app.use(router)
app.mount('#app')
import vue3GoogleLogin from 'vue3-google-login'

app.use(vue3GoogleLogin, {
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID
})