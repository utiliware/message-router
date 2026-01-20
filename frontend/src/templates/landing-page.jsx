import React, { useState } from "react";
import axios from "axios";

import Header from "./components/header";
import Title from "./components/title";
import Payload from "./components/payload";
import Results from "./components/results";
import Metrics from "./components/metrics";
import Footer from "./components/footer";

import {
  CssBaseline,
  Container
} from "@mui/joy";




export default function LandingPage() {
//   const [message, setMessage] = useState("");
//   const [count, setCount] = useState(""); // empieza vacío
//   const [status, setStatus] = useState(null);

//   const handleSend = async () => {
//     const finalCount = Number(count) || 1; // si está vacío, manda solo 1

//     try {
//       const payload =
//         finalCount > 1
//           ? {
//               messages: Array.from(
//                 { length: finalCount },
//                 (_, i) => `${message} #${i + 1}`
//               ),
//             }
//           : { message };

//       await axios.post(import.meta.env.VITE_API_BASE, payload, {
//         headers: { "Content-Type": "application/json" },
//       });

//       setStatus({
//         type: "success",
//         text:
//           finalCount > 1
//             ? `${finalCount} messages were sent successfully`
//             : "Message sent successfully",
//       });
//     } catch (err) {
//       setStatus({
//         type: "error",
//         text: "Error sending the message. Please try again.",
//       });
//     }
//   };

  return (
    <>
      <CssBaseline />
      <Container sx={{ mt: 2 }}>
        {/* <Header /> */}
        <Title />
        <Payload />
        <Results />
        <Metrics />
        {/* <Footer /> */}
      </Container>
    </>
  );
}
