<template>
  <main class="container flow">
    <form class="card contrast" @submit.prevent="sendMessage">
      <h2>One Message</h2>

      <label>
        Message
        <input v-model="message" type="text" placeholder="Write your message..." required />
      </label>

      <button type="submit">Send</button>

      <p v-if="response" class="success">{{ response }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </main>
</template>

<script>
import axios from "axios";

export default {
  name: "MessageSender",
  data() {
    return {
      message: "",
      response: null,
      error: null,
    };
  },
  methods: {
    async sendMessage() {
      this.response = null;
      this.error = null;
      try {
        const mensaje = this.message;
        const res = await axios.post(
          import.meta.env.VITE_API_URL,
          { message: this.message }
        );
        this.response = `Message: "${mensaje}" - State: ${res.data.status}`;
        this.message = "";
      } catch (err) {
        this.error = "Something unexpected happened during the process.";
        console.log(err);
      }
    },
  },
};
</script>

<style>

.card.contrast {
  max-width: 28rem;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
}

.success {
  color: green;
  font-weight: 600;
}

.error {
  color: red;
  font-weight: 600;
}
</style>



