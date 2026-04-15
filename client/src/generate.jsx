import { Card } from 'primereact/card';
import { Messages } from 'primereact/messages';
import { Button } from 'primereact/button';
import { InputText } from "primereact/inputtext";
import { useState } from 'react';
import { useEffect } from 'react';
import { Dialog } from 'primereact/dialog';


export default function Generate( {Profiles} ) { 
    const [isValid, setValid] = useState(Array(Profiles.length).fill(false));
    const [displayValid, setDisplayValid] = useState(false);
    const [errorText, setErrorText] = useState(null);

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
                    console.log("Profiles valid")
                } else{
                    console.log("Profiles not valid")
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
        
    if (!displayValid) {
            return (        
                <> 
                <div className="Row">
                    <Card className="Card" title="Generate N Conversations" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <InputText keyfilter="int" placeholder="Integers" />
                        </div>
                    </Card>
                    <Card className="Card" title="N turns" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <InputText keyfilter="int" placeholder="Integers" />
                        </div>
                    </Card>
                </div>
                <div className="island">
                    <Card className='Card100' title="Generate" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <Button label="Submit" disabled/>
                        </div>
                    </Card>
                </div>
                </>     
        );
    }
    else {
        return (        
                <> 
                <div className="Row">
                    <Card className="Card" title="Generate N Conversations" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <InputText keyfilter="int" placeholder="Integers"/>
                        </div>
                    </Card>
                    <Card className="Card" title="N turns" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <InputText keyfilter="int" placeholder="Integers"/>
                        </div>
                    </Card>
                </div>
                <div className="island">
                    <Card className='Card100' title="Generate" style={{ margin: "0 auto" }}>
                        <div className='Row'>
                            <Button label="Submit"/>
                        </div>
                    </Card>
                </div>
                </>     
        );
    }
}