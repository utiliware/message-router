import { Box, Typography } from "@mui/joy";

import Section from "../../components/section";

export default function Title() {
    return (
        <Section
            color={'rgb(23,29,37)'}
            content={
                <>
                    <Box
                        sx={{
                            display: 'flex',
                            justifyContent: 'center',
                            alignText: 'center',
                            alignSelf: 'center'
                        }}
                    >
                        <Typography 
                            sx={{
                                color: '#ffffff',
                                fontSize: 24
                            }}
                            variant="h1"
                        >
                            {"AWS Message-Router"}
                        </Typography>
                    </Box>
                </>
            }
        />
    )
}