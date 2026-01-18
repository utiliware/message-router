import { Box } from "@mui/joy";
import { useResults } from "../../../../hooks/useResults";

export default function ResultsMessage() {
  const data = useResults()
//   const messages = data[0]
    
  const messages = [
    {
      id: 1,
      message: "Hola como estas",
      contact: [
        {
          id: 1,
          type: "phone",
          lada: "+123",
          number: "6645825224"
        },
        {
          id: 2,
          type: "email",
          email: "testssssssssssss",
          domains: "@gmail.com"
        },
        {
          id: 2,
          type: "email",
          email: "testssssssssssss",
          domains: "@gmail.com"
        },
        {
          id: 2,
          type: "email",
          email: "testssssssssssss",
          domains: "@gmail.com"
        },
      ],
    },
  ];

  return (
    <Box
      sx={{
        width: "100%",
        height: 300,
        borderRadius: 1,
        bgcolor: "primary.700",
        p: 2,
        overflowY: "auto",
      }}
    >
      {messages.map((msg) => (
        <Box
          key={msg.id}
          sx={{
            mb: 2,
            p: 2,
            borderRadius: 1,
            bgcolor: "background.surface",
          }}
        >
          <Box sx={{ fontWeight: "bold", mb: 1 }}>
            {msg.message}
          </Box>
          {msg.contact.map((c) => (
            <Box
              key={c.id}
              sx={{
                mb: 1,
                p: 1,
                borderRadius: 0.5,
                bgcolor: "neutral.softBg",
              }}
            >
              <Box sx={{ fontSize: "0.8rem", fontWeight: "bold", mb: 0.5 }}>
                {c.type}
              </Box>
              {c.type === "phone" ? (
                <>
                  <Box>{c.lada} {c.number}</Box>
                </>
              ): (
                <>
                  <Box>{c.email}{c.domains}</Box>
                </>
              )}
            </Box>
          ))}
        </Box>
      ))}
    </Box>
  );
}
