import { Container, Divider, Input, Select, Option, Box, Stack, Button, Typography, Chip } from "@mui/joy";
import { Grid, styled } from '@mui/joy';
import { useState, useCallback } from "react";
import { useApi } from "../../../../endpoint/api-base";
import { useIdx } from "../../../../context";
import { useWebSocket } from "../../../../hooks/useWebSocket";

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
    const [counter, setCounter] = useState(1)
    const { setIdx, setMessageIA, setWsImageUrl } = useIdx();
    const { sendConfirmationAndMessage, sendMessageToApi } = useApi();
    const [wsResults, setWsResults] = useState([]);

    const handleWsMessage = useCallback((data) => {
        setWsResults((prev) => [...prev.slice(-19), { ...data, id: Date.now() }]);
        if (data.source === "cache" || data.source === "bedrock") {
            setMessageIA(data.prompt);
        }
        if (data.source === "image") {
            setWsImageUrl(data.imageUrl || null);
        }
    }, [setMessageIA, setWsImageUrl]);

    const { isConnected, error: wsError } = useWebSocket(handleWsMessage);

    const [contact, setContact] = useState("email");
    const [form, setForm] = useState({
        lada: "",
        number: "",
        email: "",
        domain: "@gmail.com",
        message: "",
    });
    const [contactStorage, setContactStorage] = useState([]);
    const [ids] = useState(1);
    const [messageTo, setMessageTo] = useState("");
    const [messageToApi, setMessageToApi] = useState("");
    const [apiSendLoading, setApiSendLoading] = useState(false);
    const [apiSendFeedback, setApiSendFeedback] = useState(null);

    const hasData = contactStorage.length > 0 && Object.keys(contactStorage[0]).length > 0;

    // const handleIdx = (e) => {
    //     setIds(e.target.value);
    // };

    const handleMessage = (e) => {
        setMessageTo(e.target.value);
    };

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
        if (contact === "email" && (!form.email || !form.domain)) {
            return false;
        }
        return true;
    };

    const handleAdd = async () => {
        if (!isValid() || !ids) return;

        const contactArray = [];

        if (contact === "email") {
            try {
                const sendConfirmationResp = await sendConfirmationAndMessage({
                    id: ids, 
                    method: 'valid',
                    type: 'email',
                    email: form.email,
                    domains: form.domain,
                });
                
                console.log(sendConfirmationResp);
                
                contactArray.push({
                    id: ids, 
                    type: 'email',
                    email: form.email,
                    domains: form.domain,
                });
            } catch (error) {
                console.log(error);
                return;
            }
        }

        const newItem = {
            id: ids,
            method: "send",
            message: messageTo,
            contact: contactArray,
        };

        setContactStorage((prev) => [...prev, newItem]);
        setForm({
            lada: "",
            number: "",
            email: "",
            domain: "@gmail.com",
            message: messageTo,
        });
    };

    const handleDelete = (id) => {
        setContactStorage((prev) => prev.filter((item) => item.id !== id));
    };

    const sendMessage = async () => {
        if (!contactStorage.length || !ids) return;
        const payload = {
            "method": "send",
            "id": ids,
            "message": messageTo
        };        
        try {
            const sendMessageResp = await sendConfirmationAndMessage(payload);
            console.log(sendMessageResp);
            setIdx(1+counter);
            setCounter(1+counter)
        } catch (error) {
            console.log(error);
        }
        setMessageIA(messageTo);
        setContactStorage([])
    };

    const handleSendToApi = async () => {
        if (!messageToApi.trim()) return;
        setApiSendFeedback(null);
        setApiSendLoading(true);
        try {
            await sendMessageToApi(messageToApi.trim());
            setApiSendFeedback({ type: "success", text: "Message send to API correctly." });
            setMessageToApi("");
        } catch (error) {
            console.error(error);
            setApiSendFeedback({ type: "error", text: error?.response?.data?.message || "Error sending to API." });
        } finally {
            setApiSendLoading(false);
        }
    };

    return (
        <Container>
            <Box>
                {/* <Input
                    placeholder="Write id..."
                    value={ids}
                    onChange={handleIdx}
                    sx={{ width: "20%", mb: 2 }}
                /> */}
                <Input
                    placeholder="Write your message..."
                    value={messageTo}
                    onChange={handleMessage}
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
                    <Button onClick={handleAdd}>
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
                    }}
                    onClick={sendMessage}
                >
                    Send to Email
                </Button>
                <Divider sx={{ my: 2 }} />
                <Box component="span" sx={{ fontSize: "0.9rem", fontWeight: 600, display: "block", mb: 1 }}>
                    Send to console API
                </Box>
                <Input
                    placeholder="Write your message…"
                    value={messageToApi}
                    onChange={(e) => setMessageToApi(e.target.value)}
                    sx={{ width: "100%", mb: 1 }}
                    disabled={apiSendLoading}
                />
                {apiSendFeedback && (
                    <Box
                        sx={{
                            mb: 1,
                            fontSize: "0.85rem",
                            color: apiSendFeedback.type === "success" ? "success.600" : "danger.600",
                        }}
                    >
                        {apiSendFeedback.text}
                    </Box>
                )}
                <Button
                    onClick={handleSendToApi}
                    disabled={!messageToApi.trim() || apiSendLoading}
                    loading={apiSendLoading}
                    sx={{ width: "100%" }}
                >
                    Send to console API
                </Button>
                <Divider sx={{ my: 2 }} />
                <Box component="span" sx={{ fontSize: "0.9rem", fontWeight: 600, display: "block", mb: 1 }}>
                    Live results (WebSocket)
                </Box>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <Chip color={isConnected ? "success" : "neutral"} variant="soft" size="sm">
                        {isConnected ? "Connected" : "Disconnected"}
                    </Chip>
                    {wsError && (
                        <Typography level="body3" color="danger">{wsError}</Typography>
                    )}
                </Stack>
                {wsResults.length > 0 && (
                    <Stack spacing={1} sx={{ maxHeight: 280, overflowY: "auto" }}>
                        {wsResults.map((r) => (
                            <Box
                                key={r.id}
                                sx={{
                                    p: 1.5,
                                    borderRadius: "sm",
                                    bgcolor: "background.level1",
                                    border: "1px solid",
                                    borderColor: "neutral.outlinedBorder",
                                }}
                            >
                                {r.source === "image" ? (
                                    <>
                                        <Typography level="body3" fontWeight="600">Image ready</Typography>
                                        <Typography level="body4" sx={{ wordBreak: "break-all" }}>{r.response}</Typography>
                                        {r.prompt && <Typography level="body4" color="neutral">Prompt: {r.prompt}</Typography>}
                                    </>
                                ) : (
                                    <>
                                        <Typography level="body3" fontWeight="600">IA ({r.source || "response"})</Typography>
                                        {r.prompt && <Typography level="body4" color="neutral">{r.prompt}</Typography>}
                                        <Typography level="body4">{r.response}</Typography>
                                    </>
                                )}
                            </Box>
                        ))}
                    </Stack>
                )}
            </Box>
        </Container>
    );
}

