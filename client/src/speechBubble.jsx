import { useState } from 'react';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';

export default function SpeechBubble( {agentClass, agentName, text} ) { 
    let agentHeaderStyle;

    if (agentClass === "agent1Bubble") {
        agentHeaderStyle = {width:'100%'};
    } else {
        agentHeaderStyle = {textAlign:'right', width:'100%'};
    }
    
    return (         
        <> 
        <div className="conversation">
            <Card className={agentClass}>
                <h5 className="m-0" style = {agentHeaderStyle}>{agentName}</h5>
                <Divider style={{width:'100%'}}/>
                <h5 className="m-0" style={{width:'100%'}}>{text}</h5>
            </Card>
        </div>
        </>     
  );
}
