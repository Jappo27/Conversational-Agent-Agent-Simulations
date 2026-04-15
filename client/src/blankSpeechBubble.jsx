import { useState } from 'react';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { Skeleton } from 'primereact/skeleton';

export default function SkeletonSpeechBubble( {agentClass} ) { 
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
                <h5 className="m-0" style = {agentHeaderStyle}><Skeleton className="mb-2" style={{ width: '100%' }}/></h5>
                <Divider style={{width:'100%'}}/>
                <h5 className="m-0" style={{width:'100%'}}>
                    <Skeleton className="mb-2" width={`${Math.floor(Math.random() * (100 - 50 + 1)) + 50}%`}/>
                    <Skeleton className="mb-2" width={`${Math.floor(Math.random() * (100 - 50 + 1)) + 50}%`}/>
                    <Skeleton className="mb-2" width={`${Math.floor(Math.random() * (100 - 50 + 1)) + 50}%`}/>
                </h5>
            </Card>
        </div>
        </>     
  );
}
