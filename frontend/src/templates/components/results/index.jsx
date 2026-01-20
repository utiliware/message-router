import { Box, Stack } from "@mui/joy";
import Section from "../../../components/section";
import ResultsImage from "./ai-generated";
import ResultsMessage from "./payload";



export default function Results() {
    return (
        <Section
            title={"Results"}
            content={            
                <>
                    <Box sx={{
                        width: '100%'
                    }}>
                    <Stack
                        direction="row"
                        spacing={2}
                        sx={{
                            justifyContent: "center",
                            alignItems: "center",
                        }}
                    >
                        {/* <ResultsMessage/> */}
                        <ResultsImage/>
                    </Stack>
                    </Box>
                </>
            }
        />
    )
}