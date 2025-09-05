<template>
  <main class="container">
    <div class="main-container">
      <div class="message">
        <SendMessage/>
      </div>
      <div class="message_multiple">
        <SendMultipleMessages/>
      </div>
    </div>
    <div class="dashboard">
      <Dashboard/>
    </div>
  </main>
</template>

<script>
// import CreateItem from './components/CreateItem'
// import GetItems from './components/GetItems'
// import GetItemById from './components/GetItemById'
import SendMessage from './components/SendMessage.vue';
import Dashboard from './components/Dashboard.vue';
// import ConcurrencyChart from './components/ConcurrencyChart.vue';
import SendMultipleMessages from './components/SendMultipleMessages.vue';

export default {
  name: 'App',
  components: {
    // GetItems,
    // CreateItem,
    // GetItemById,
    SendMessage,
    SendMultipleMessages,
    Dashboard,
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

#logo {
  display: flex;
  width: 15%;
  flex-direction: column;
  justify-content: center;
  margin: auto;
}

.main-container {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.message,
.message_multiple {
  flex: 1 1 300px;
}

.dashboard {
  margin-top: 2rem;
  width: 100%;
}

.form-section {
  display: block;
  margin: 2%;
  justify-content: left;
}

.error {
  color: red;
}

div {
  margin: 1%;
}
input {
  margin: 1%;
}
label {
  margin: 1%;
}

</style>
