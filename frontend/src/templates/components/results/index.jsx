import { Box, Stack } from "@mui/joy";
import Section from "../../../components/section";
import ResultsImage from "./ai-generated";
import ResultsMessage from "./payload";
import ResultsBedrock from "../../../components/results/bedrock-response";



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
                    <Stack
                        direction="row"
                        spacing={2}
                        sx={{
                            justifyContent: "center",
                            alignItems: "stretch",
                            mt: 2,
                        }}
                    >
                        <ResultsBedrock/>
                    </Stack>
                    </Box>
                </>
            }
        />
    )
}