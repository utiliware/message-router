import Section from "../../../components/section";
import Message from "./message";
import { Box } from "@mui/joy";


export default function Payload() {
    return (
        <Section
            title={"Payload"}
            content={            
                <>
                    <Box sx={{
                        width: '100%'
                    }}>
                        <Message />
                    </Box>
                </>
            }
        />
    )
}