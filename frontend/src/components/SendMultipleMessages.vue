<template>
  <main class="container flow">
    <section class="card contrast padded">
      <h2>Multiple messages</h2>

        <input v-model="message" type="text" placeholder="Write your message..." />
        <br>
        <input v-model.number="quantity" type="number" min="1" />

      <button @click="sendMessages">Send</button>
    </section>
  </main>
</template>

<script>
import axios from "axios";

export default {
  name: "MessageSender",
  data() {
    return {
      message: "",
      quantity: 1,
      response: null,
      error: null,
    };
  },
  methods: {
    async sendMessages() {
      this.response = null;
      this.error = null;

      try {
        for (let i = 1; i <= this.quantity; i++) {
          const finalMessage = `${this.message} ${i}`;
          console.log(`Sending: ${finalMessage}`);

          const res = await axios.post(
            import.meta.env.VITE_API_URL,
            { message: finalMessage }
          );

          console.log(`Response ${i}:`, res.data);
        }

        this.response = `Sent ${this.quantity} messages successfully.`;
        this.message = "";
        this.quantity = 1;
      } catch (err) {
        this.error = "Something unexpected happened during the process.";
        console.error(err);
      }
    },
  },
};
</script>

<style>
/* Extra spacing for PicoCSS card */
.card.contrast {
  max-width: 28rem;
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
}

/* Success and error messages */
.success {
  color: green;
  font-weight: 600;
}

.error {
  color: red;
  font-weight: 600;
}
</style>
