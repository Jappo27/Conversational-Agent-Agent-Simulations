import { useState } from 'react';
import SpeechBubble from './speechBubble.jsx';
import { Dialog } from 'primereact/dialog';
import { useEffect } from 'react';
import SkeletonSpeechBubble from './blankSpeechBubble.jsx'

export default function Simulation( {Profiles} ) {     
    const [isValid, setValid] = useState(Array(Profiles.length).fill(false));
    const [displayValid, setDisplayValid] = useState(false);
    const [errorText, setErrorText] = useState(null);
    const [conversation, setConversation] = useState([]);
    const [agentClasses, setCurrentAgentClass]= useState(["agent1Bubble", "agent2Bubble"]);
    const [turn, setTurn]= useState(0);


    const addConversation = (modelClass, modelName, response) => {
        const newResponse = {
            modelClass: modelClass,
            modelName: modelName,
            response: response
        }
        setConversation(conversation => [...conversation, newResponse]);
    };

    useEffect(() => {
        console.log(conversation);
    }, [conversation]);


    const simulateConversation = async () => {
        //http://howto.philippkeller.com/2023/10/14/How-to-stream-chatGPT-from-Flask-to-react-simpler-method/
        console.log("Simulation Started")
        const res = await fetch("http://localhost:5000/conversation", {
	        method: 'POST',
	        headers: {
	            'Content-Type': 'application/json'
	        },
	        credentials: 'include',
            body: JSON.stringify({ profiles: Profiles })})
        setConversation([]);
        const reader = res.body.getReader()
	    const decoder = new TextDecoder('utf-8')
	    while (true) {
            const { value } = await reader.read()
            let data = JSON.parse(decoder.decode(value))
            console.log(data);
            addConversation(data.data.modelClass, data.data.modelName, data.data.text)
            setTurn(prevTurn => (prevTurn + 1) % agentClasses.length);
        }
    };

    useEffect(() => {
        const sendProfiles = async () => {
            try {
            const res = await fetch("http://localhost:5000/validJSONS", {
                method: "POST",
                headers: {"Content-Type": "application/json",},
                body: JSON.stringify({ profiles: Profiles }),
            });

            const data = await res.json();
            setValid(data.data);
            setDisplayValid(data.data);
            setErrorText(data.status);
            if (data.data) {
                simulateConversation();
            } else{
                console.log("Simulation not Started")
            }
            } catch (err) {
                console.error("Error sending Profiles", err);
            }};

        if (Profiles && Profiles.length > 0) {
            sendProfiles();
        }        
    }, [Profiles]);
    
    if (!isValid) {
        return (
            <> 
            <Dialog header="Invalid Format"  className={'errorBanner'} visible={!isValid} style={{ width: '50vw' }} 
            onHide={() => {
                if (isValid) return; 
                setValid(!isValid);
            }}>{errorText} </Dialog>
            </> 
            );
    } 
    if (displayValid) {
        return (
            <>
            <div>
                {conversation.map(convo => (
                <SpeechBubble 
                agentClass = {convo.modelClass} 
                agentName = {convo.modelName} 
                text = {convo.response}
                />
                ))}
                <SkeletonSpeechBubble
                    agentClass={agentClasses[turn]}
                />
            </div>
            </>
        );
    }
}
