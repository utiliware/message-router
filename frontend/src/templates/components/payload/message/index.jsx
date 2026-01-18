import { Container,Divider, Input, Select, Option, Box, Stack, Button  } from "@mui/joy";
import { Grid, styled } from '@mui/joy'
import { useState } from "react";

const Item = styled(Box)(({ theme }) => ({
  backgroundColor: '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: (theme.vars ?? theme).palette.text.secondary,
  ...theme.applyStyles('dark', {
    backgroundColor: '#1A2027',
  }),
}));

export default function Message() {
    const [contact, setContact] = useState("phone")
    const [form, setForm] = useState({
        lada: "",
        number: "",
        email: "",
        domain: "@gmail.com",
        message: "",
    });
    const [contactStorage, setContactStorage] = useState([])

    const hasData = contactStorage.length > 0 && Object.keys(contactStorage[0]).length > 0;

    const handleContact = (e, value) => setContact(value);
    const handleDomain = (e, value) => setForm((prev) => ({ ...prev, domain: value }));

    const handleFormChange = (field) => (e) => {
        let value = e.target.value;
        if (field === "lada" || field === "number") {
            value = value.replace(/\D/g, ""); 
            value = field === "number" ? value.slice(0, 10) : value; 
        }
        setForm((prev) => ({
            ...prev,
            [field]: value,
        }));
    };


    const isValid = () => {
        if (contact === "phone" && (!form.lada || !form.number)) {
            return false;
        }
        if (contact === "email" && (!form.email || !form.domain)) {
            return false;
        }
        return true;
    };

    const handleAdd = () => {
        if (!isValid()) return;
        const contactArray = [];

        if (contact === "phone") {
            contactArray.push({
            id: Date.now(), // Es temporal
            type: 'phone',
            lada: form.lada,
            number: form.number,
            });
        }

        if (contact === "email") {
            contactArray.push({
            id: Date.now(), // Es temporal
            type: 'email',
            email: form.email,
            domains: form.domain,
            });
        }

        const newItem = {
            id: Date.now(), // Es temporal
            message: form.message,
            contact: contactArray,
        };

        setContactStorage((prev) => [...prev, newItem]);
        setForm({
            lada: "",
            number: "",
            email: "",
            domain: "@gmail.com",
            message: "",
        });
    };

    const handleDelete = (id) => {
        setContactStorage((prev) =>
            prev.filter((item) => item.id !== id)
        );
    };

    return (
        <Container>
            <Box>
                <Input
                    placeholder="Write your message..."
                    value={form.message}
                    onChange={handleFormChange("message")}
                    sx={{ width: "100%", mb: 2 }}
                />
                <Stack
                    direction="row"
                    spacing={2}
                    sx={{
                        justifyContent: "center",
                        alignItems: "center",
                    }}
                >
                    <Select
                        value={contact}
                        sx={{ width: "20%" }}
                        onChange={handleContact}
                    >
                        <Option value="phone">Phone</Option>
                        <Option value="email">Emails</Option>
                    </Select>
                    {contact === "phone" ? (
                    <>
                        <Input
                            placeholder="+123"
                            value={form.lada}
                            onChange={handleFormChange("lada")}
                            sx={{ width: "15%" }}
                        />
                        <Input
                            placeholder="Phone number"
                            value={form.number}
                            onChange={handleFormChange("number")}
                            sx={{ width: "65%" }}
                        />
                    </>
                    ) : (
                    <>
                        <Input
                            placeholder="Email"
                            value={form.email}
                            onChange={handleFormChange("email")}
                            sx={{ width: "50%" }}
                        />
                        <Select
                            value={form.domain}
                            sx={{ width: "30%" }}
                            onChange={handleDomain}
                        >
                            <Option value="@gmail.com">@gmail.com</Option>
                            <Option value="@hotmail.com">@hotmail.com</Option>
                            <Option value="@outlook.com">@outlook.com</Option>
                        </Select>
                    </>
                    )}
                    <Button 
                        sx={{
                            
                        }}
                        onClick={handleAdd}
                    >
                        +
                    </Button>
                </Stack>
                <Divider sx={{ my: 2 }} />
                {hasData && (
                    <Grid
                    container
                    spacing={2}
                    sx={{
                        mt: 2,
                        maxHeight: 200,
                        overflowY: "auto",
                        overflowX: "hidden",
                    }}
                    >
                    {contactStorage.map((item, index) => (
                        <Grid
                            container
                            spacing={2}
                            key={item.id ?? index}
                            sx={{ mb: 1, width: "100%", p: 1, alignItems: "center" }}
                        >
                        <Grid xs={2}>
                            <Item sx={{  
                                    boxShadow: 1,
                                    outline: "1px solid rgba(0,0,0,0.2)", 
                                    height: 40 
                                }}>
                            {item.contact.map((c) => c.type).join(", ")}
                            </Item>
                        </Grid>

                        <Grid xs={8.5}>
                            <Grid container sx={{ flexWrap: "nowrap", alignItems: "stretch", gap: 1 }}>
                            {item.contact.map((contactItem, i) => (
                                <Grid key={contactItem.id ?? i} sx={{ flexGrow: 1 }}>
                                <Item
                                    sx={{
                                    height: 40,
                                    boxShadow: 1,
                                    outline: "1px solid rgba(0,0,0,0.2)", 
                                    fontSize: "0.85rem",
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    }}
                                >
                                    {contactItem.lada
                                    ? `${contactItem.lada} ${contactItem.number}`
                                    : `${contactItem.email}${contactItem.domains}`}
                                </Item>
                                </Grid>
                            ))}
                            </Grid>
                        </Grid>

                        <Grid xs={1}>
                            <Button color="danger" onClick={() => handleDelete(item.id)}>
                            Del
                            </Button>
                        </Grid>
                        </Grid>
                    ))}
                    </Grid>
                )}
                <Button
                    sx={{
                        mt: 1,
                        width: '100%',
                        backgroundColor: "rgb(241,158,57)",
                        color: "rgb(0, 0, 0)",
                        fontWeight: "bold", 
                        "&:hover": {
                            backgroundColor: "rgb(187, 109, 32)"
                        }
                    }}>
                    Send
                </Button>
            </Box>
        </Container>
    )
}