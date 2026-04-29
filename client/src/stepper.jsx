
import React, { useRef, useState } from "react";
import { Stepper } from 'primereact/stepper';
import { StepperPanel } from 'primereact/stepperpanel';
import { Button } from 'primereact/button';
import AgentProfileSetup from "./agentprofilecard.jsx";
import Simulation from "./simulation.jsx";
import PromptInsert from "./promptInsert.jsx";
import VectorUpload1 from "./vectorupload1.jsx";
import VectorUpload2 from "./vectorupload2.jsx";
import Generate from "./generate.jsx";

export default function Menu( Items, Content ) {
    const stepperRef = useRef(null);

    //These should be personna not prompt
    const [prompt1, setPrompt1] = useState({});
    const [prompt2, setPrompt2] = useState({});

    const [p1, setP1] = useState("");
    const [p2, setP2] = useState("");

    const profile1 = {
            modelName: "",
            role: 'user',
            prompt: '',
            system: p1,
            suffix: '',
            raw: true,
            stream: false,
            keepAlive: 5,
            images: [],
            context: '',

            seed: 0,
            temperature: 1.0,
            topK: 50,
            minP: 0.0,
            maxP: 1.0,
            stop: '',
            numCTX: 0.0,
            numPredict: 0.0,
            
            format: []
    };
    const profile2 = {
            modelName: "",
            role: 'user',
            prompt: '',
            system: p2,
            suffix: '',
            raw: true,
            stream: false,
            keepAlive: 5,
            images: [],
            context: '',

            seed: 0,
            temperature: 1.0,
            topK: 50,
            minP: 0.0,
            maxP: 1.0,
            stop: '',
            numCTX: 0.0,
            numPredict: 0.0,
            
            format: []
    }
    
    const profiles = [profile1 , profile2];

    const genPrompt1 = async (prompt1) => {
        try {
            const file = new File(
                [JSON.stringify(prompt1)],
                "prompt.json",
                { type: "application/json" }
            );

            const formData = new FormData();
            formData.append("prompt", file);

            const response = await fetch("http://127.0.0.1:5000/promptBuild", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            console.log(data.data)
            if (data.status == "Success") {
                setP1(data.data);
            };

        } catch (error) {
            console.error("Error sending prompt:", error);
        }
    };

    const genPrompt2 = async (prompt2) => {
        try {
            const file = new File(
                [JSON.stringify(prompt2)],
                "prompt.json",
                { type: "application/json" }
            );

            const formData = new FormData();
            formData.append("prompt", file);

            const response = await fetch("http://127.0.0.1:5000/promptBuild", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (data.status == "Success") {
                setP2(data.data);
            };

        } catch (error) {
            console.error("Error sending prompt:", error);
        }
    };
    
    return (
    <div className="card flex justify-content-center">
        <Stepper ref={stepperRef} style={{ flexBasis: '50rem' }}>
            <StepperPanel className= "Container" header="Persona 1">
                <div className="flex flex-column h-12rem">
                    <PromptInsert className="Profile" prompt = {prompt1} setPrompt={setPrompt1} />
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => {stepperRef.current.nextCallback(); genPrompt1(prompt1);}} />
                </div>
            </StepperPanel>
            <StepperPanel className= "Container" header="Persona 2">
                <div className="flex flex-column h-12rem">
                    <PromptInsert className="Profile" prompt = {prompt2} setPrompt={setPrompt2} />
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => {stepperRef.current.nextCallback(); genPrompt2(prompt2);}} />
                </div>
            </StepperPanel>
            <StepperPanel className= "Container" header="Model 1">
                <div className="flex flex-column h-12rem">
                    <AgentProfileSetup className = "Profile" Profile = {profiles[0]}></AgentProfileSetup>
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => stepperRef.current.nextCallback()} />
                </div>
            </StepperPanel>
            <StepperPanel className= "Container" header="Model 2">
                <div className="flex flex-column h-12rem">
                    <AgentProfileSetup className = "Profile" Profile = {profiles[1]}></AgentProfileSetup>
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => stepperRef.current.nextCallback()} />
                </div>
            </StepperPanel>
            <StepperPanel className= "Container" header="Vector Storage 1">
                <div className="flex flex-column h-12rem">
                    <VectorUpload1 className = "Profile"/>
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => stepperRef.current.nextCallback()} />
                </div>
            </StepperPanel>
            <StepperPanel className= "Container" header="Vector Storage 2">
                <div className="flex flex-column h-12rem">
                    <VectorUpload2 className = "Profile"/>
                </div>
                <div className="flex pt-4 justify-content-start">
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => stepperRef.current.nextCallback()} />
                </div>
            </StepperPanel>
            {/*<StepperPanel className= "Container" header="Simulation">
                <div className="flex pt-4 justify-content-start">
                    <div className="flex flex-column h-12rem">
                        <Simulation
                            Profiles = {profiles}
                        />
                    </div>
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                    <Button className = "NButton" label="Next" icon="pi pi-arrow-right" iconPos="right" onClick={() => stepperRef.current.nextCallback()} />
                </div>
            </StepperPanel>*/}
            <StepperPanel className= "Container" header="Confirmation" >
                <div className="flex pt-4 justify-content-start">
                    <div className="flex flex-column h-12rem">
                        <Generate Profiles = {profiles} />
                    </div>
                    <Button className = "BButton" label="Back" severity="secondary" icon="pi pi-arrow-left" onClick={() => stepperRef.current.prevCallback()} />
                </div>
            </StepperPanel>
        </Stepper>
    </div>
    )
}
        