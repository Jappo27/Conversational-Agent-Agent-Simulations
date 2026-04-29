import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from "primereact/inputtext";
import { Dialog } from 'primereact/dialog';
import { useState, useEffect } from 'react';

export default function Generate({ Profiles }) {

    const [isValid, setValid] = useState(Array(Profiles.length).fill(false));
    const [displayValid, setDisplayValid] = useState(false);
    const [errorText, setErrorText] = useState(null);

    const [convoNum, setConvoNum] = useState(0);
    const [turnNum, setTurnNum] = useState(0);

    useEffect(() => {
        const sendProfiles = async () => {
            try {
                const res = await fetch("http://localhost:5000/validJSONS", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ profiles: Profiles }),
                });

                const data = await res.json();
                setValid(data.data);
                setDisplayValid(data.data);
                setErrorText(data.status);

            } catch (err) {
                console.error("Error sending Profiles", err);
            }
        };

        if (Profiles && Profiles.length > 0) {
            sendProfiles();
        }
    }, [Profiles]);

    const handleSubmit = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/convoSetup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    profile1: Profiles[0],
                    profile2: Profiles[1],
                    convo: {
                        convoNum: Number(convoNum),
                        turnNum: Number(turnNum)
                    }
                })
            });

            const data = await res.json();
            console.log("Server response:", data);

        } catch (err) {
            console.error("Error submitting conversation setup:", err);
        }
    };

    if (!isValid) {
        return (
            <Dialog header="Invalid Format"
                className={'errorBanner'}
                visible={!isValid}
                style={{ width: '50vw' }}
                onHide={() => setValid(!isValid)}
            >
                {errorText}
            </Dialog>
        );
    }

    return (
        <>
            <div className="Row">
                <Card className="Card" title="Generate N Conversations" style={{ margin: "0 auto" }}>
                    <div className='Row'>
                        <InputText
                            keyfilter="int"
                            placeholder="Integers"
                            onChange={(e) => setConvoNum(e.target.value)}
                        />
                    </div>
                </Card>

                <Card className="Card" title="N turns" style={{ margin: "0 auto" }}>
                    <div className='Row'>
                        <InputText
                            keyfilter="int"
                            placeholder="Integers"
                            onChange={(e) => setTurnNum(e.target.value)}
                        />
                    </div>
                </Card>
            </div>

            <div className="island">
                <Card className='Card100' title="Generate" style={{ margin: "0 auto" }}>
                    <div className='Row'>
                        <Button
                            label="Submit"
                            onClick={handleSubmit}
                            disabled={!displayValid}
                        />
                    </div>
                </Card>
            </div>
        </>
    );
}
