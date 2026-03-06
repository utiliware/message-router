import { Box, Stack } from "@mui/joy";
import Section from "../../../components/section";
import ResultsImage from "./ai-generated";
import ResultsMessage from "./payload";
import ResultsBedrock from "./bedrock-response";



export default function Results() {
    return (
        <Section
            title={"Results"}
            content={            
                <>
                    <Box sx={{
                        width: '100%',
                        height: '100%',
                    }}>
                        <Stack
                            direction="row"
                            spacing={2}
                            sx={{
                                justifyContent: "center",
                                alignItems: "center",
                                height: 'auto',
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