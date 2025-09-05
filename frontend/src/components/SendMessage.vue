<template>
  <div class="d-flex flex-column align-items-center justify-content-center min-vh-100 bg-light">
    <div class="w-100" style="max-width: 28rem;">
      <div class="card shadow-lg rounded-4 p-4">
        <h2 class="h4 fw-bold mb-4 text-center text-primary">Message Router</h2>
        
        <input
          v-model="message"
          type="text"
          placeholder="Write your message..."
          class="form-control mb-3"
        />

        <button
          @click="sendMessage"
          class="btn btn-primary w-100"
        >
          Send
        </button>

        <p v-if="response" class="mt-3 text-success fw-semibold">{{ response }}</p>
        <p v-if="error" class="mt-3 text-danger fw-semibold">{{ error }}</p>
      </div>
    </div>
  </div>
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
        const mensaje = this.message; // guardar antes de limpiar
        const res = await axios.post(
          process.env.VUE_APP_API_URL,
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
