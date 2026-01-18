import { Container, Card, CardContent, Typography } from "@mui/joy";

export default function Section({ title, color = null ,content }) {
    return (
        // <Container>
            <Card sx={{
                margin: 2,
                backgroundColor: color
            }}>
                <Typography>
                    {title}
                </Typography>
                <CardContent 
                    sx={{
                        justifyContent: 'center',
                        alignText: 'center',
                        
                    }}
                    orientation="horizontal"
                >
                    {content}
                </CardContent>
            </Card>
        // </Container>
    )
}