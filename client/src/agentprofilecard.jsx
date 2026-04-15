import React, { useState, useRef } from 'react';
import { Card } from 'primereact/card';
import AutocompleteDrop from "./autocompletedropdown.jsx";
import { InputTextarea } from "primereact/inputtextarea";
import { InputSwitch } from "primereact/inputswitch";
import { Dropdown } from 'primereact/dropdown';
import { Slider } from "primereact/slider";
import { InputNumber } from 'primereact/inputnumber';
import { Button } from 'primereact/button';
import { InputText } from "primereact/inputtext";
import { FileUpload } from 'primereact/fileupload';
import { AutoComplete } from "primereact/autocomplete";

export default function AgentProfileSetup( {Profile} ) {
    /*Agents*/
    const models = [
    "qwen3-vl",
    "qwen3.5",
    "glm-4.7-flash",
    "qwen3-next",
    "nemotron-3-nano",
    "gpt-oss-safeguard",
    "qwen3",
    "gpt-oss",
    "magistral",
    "deepseek-v3.1",
    "deepseek-r1"
    ];
    const roles = ['system', 'user', 'assistant', 'tool'];
    const minOptions = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15];

    /*Agent */
    const [selectedModel, setSelectedModel] = useState(Profile.modelName);
    const [selectedRole, setSelectedRole] = useState(Profile.role);
    const [prompt, setPrompt] = useState(Profile.prompt);
    const [system, setSystem] = useState(Profile.system);
    const [suffix, setSuffix] = useState(Profile.suffix);
    const [rawChecked, setRawChecked] = useState(Profile.raw);
    const [streamChecked, setStreamChecked] = useState(Profile.stream);
    const [image, setImage] = useState(Profile.images);
    const [minutes, setMinutes] = useState(Profile.keepAlive);
    const [context, setContext] = useState(Profile.context);

    /*Options*/
    const [seed, setSeed] = useState(Profile.seed);
    const [temperature, setTemperature] = useState(Profile.temperature);
    const [topK, setTopK] = useState(Profile.topK);
    const [minP, setMinP] = useState(Profile.minP);
    const [maxP, setMaxP] = useState(Profile.maxP);
    const [stop, setStop] = useState(Profile.stop);
    const [numCTX, setNumCtx] = useState(Profile.numCTX);
    const [numPredict, setNumPredict] = useState(Profile.numPredict);

    /*Functions */

    const updateAll = ( {Profile} ) => {
        setSelectedModel(Profile.modelName)
        setSelectedRole(Profile.role)
        setPrompt(Profile.prompt)
        setSystem(Profile.system)
        setSuffix(Profile.suffix)
        setRawChecked(Profile.raw)
        setStreamChecked(Profile.stream)
        setMinutes(Profile.keepAlive)
        setContext(Profile.context)
        setSeed(Profile.seed)
        setTemperature(Profile.temperature)
        setTopK(Profile.topK)
        setMinP(Profile.minP)
        setMaxP(Profile.maxP)
        setStop(Profile.stop)
        setNumCtx(Profile.numCTX)
        setNumPredict(Profile.numPredict)
    }

    const downloadFile = ( {Profile} ) => {
        //https://stackoverflow.com/questions/55613438/reactwrite-to-json-file-or-export-download-no-server

        // create file in browser
        const fileName = "AgentProfile";
        const json = JSON.stringify(Profile, null, 4);
        const blob = new Blob([json], { type: "application/json" });
        const href = URL.createObjectURL(blob);
        
        // create "a" HTLM element with href to file
        const link = document.createElement("a");
        link.href = href;
        link.download = fileName + ".json";
        document.body.appendChild(link);
        link.click();

        // clean up "a" element & remove ObjectURL
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
    }

    console.clear() 
    /*
    There are no errors if i delete the errors 
    There is no war in ba sing se
    */
    return (
        <><div className="Row">
            <Card className="Card" title="Agent">
                <div className='Row'>
                    <h5 className="m-0">Model select:</h5>
                    <AutocompleteDrop
                        elements={models}
                        value={selectedModel}
                        onChange={(e) => {
                            setSelectedModel(e);
                            Profile.modelName = e;
                        }}
                        placeholder="Select Model"
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Role:</h5>
                    <AutocompleteDrop
                        elements={roles}
                        value={selectedRole}
                        onChange={(e) => {
                            setSelectedRole(e);
                            Profile.role = e;
                        }}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Prompt:</h5>
                    <InputTextarea
                        autoResize
                        value={prompt}
                        placeholder='Enter a prompt'
                        onChange={(e) => {
                            setPrompt(e.target.value);
                            Profile.prompt = e.target.value;
                        }}
                        style={{ width: '100%' }} />
                </div>
                <div className='Row'>
                    <h5 className="m-0">System:</h5>
                    <InputTextarea
                        autoResize
                        value={system}
                        placeholder='Enter a Persona'
                        onChange={(e) => {
                            setSystem(e.target.value);
                            Profile.system = e.target.value;
                        }}
                        style={{ width: '100%' }} />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Suffix:</h5>
                    <InputTextarea
                        autoResize
                        value={suffix}
                        onChange={(e) => {
                            setSuffix(e.target.value);
                            Profile.suffix = e.target.value;
                            
                        }}
                        style={{ width: '100%' }} />
                </div>
            </Card>
            <Card className="Card" title="Agent Extras">
                <div className='Row'>
                    <h5 className="m-0">Stream:</h5>
                    <InputSwitch
                        checked={streamChecked}
                        onChange={(e) => {
                            setStreamChecked(e.target.value);
                            Profile.stream = e.target.value;
                        }}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Raw:</h5>
                    <InputSwitch
                        checked={rawChecked}
                        onChange={(e) => {
                            setRawChecked(e.target.value);
                            Profile.raw = e.target.value;
                        }}
                        />
                </div>
                <div className='Row'>
                    <h5 className="m-0">KeepAlive:</h5>
                    <Dropdown
                        value={minutes}
                        onChange={(e) => {
                            setMinutes(e.value);
                            Profile.keepAlive = e.value;
                        }}
                        options={minOptions}
                        optionLabel="name"
                        placeholder="Select a duration"
                        className="w-full md:w-14rem"
                        checkmark={true}
                        highlightOnSelect={false} />
                </div>
                <div className='Row'>
                    <div className='Row'>
                        <h5 className="m-0">Image:</h5>
                        <h5 className="m-0" style={{justifyContent:"left"}}>{image}</h5>
                    </div>
                    <FileUpload 
                        mode="basic" 
                        name="imageUpload" 
                        url="http://127.0.0.1:5000/ImageUpload" 
                        accept="image/*" 
                        maxFileSize={1000000} 
                        auto
                        onUpload = {(e) => {
                            const imageLink = JSON.parse(e.xhr.responseText);
                            setImage( [imageLink['data']] );
                            Profile.images = [imageLink['data']]
                        }}  
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Context:</h5>
                    <InputTextarea
                        autoResize
                        value={context}
                        placeholder='Enter a Context'
                        onChange={(e) => {
                            setContext(e.target.value);
                            Profile.context = e.target.value;
                        }}
                        style={{ width: '100%' }} />
                </div>
            </Card>
        </div>
        <div className='Row'>
            <Card className="Card30" title="Options">
                <div className='Row'>
                    <h5 className="m-0">Temperature:</h5>
                    <InputNumber
                        value={temperature}
                        onValueChange={(e) => {
                            setTemperature(e.target.value);
                            Profile.temperature = e.target.value;
                        }}
                        minFractionDigits={2}
                        maxFractionDigits={3}
                        min={0}
                        max={2}
                        />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Top K:</h5>
                    <InputNumber
                        value={topK}
                        onValueChange={(e) => {
                            setTopK(e.value);
                            Profile.topK = e.value;
                        }}
                        minFractionDigits={2}
                        maxFractionDigits={3}
                        min={0}
                        max={100}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">P:</h5>
                    <InputNumber
                        value={minP}
                        default = {0}
                        onValueChange={(e) => {
                            setMinP(e.value);
                            Profile.minP = e.value;
                        }}
                        minFractionDigits={2}
                        maxFractionDigits={3}
                        min={0}
                        max={maxP}
                        />

                        <InputNumber
                        value={maxP}
                        default = {1}
                        onValueChange={(e) => {
                            setMaxP(e.value);
                            Profile.maxP = e.value;
                        }}
                        minFractionDigits={2}
                        maxFractionDigits={3}
                        min={minP}
                        max={1}
                        />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Seed:</h5>
                    <p className="m-0">{seed}</p>
                    <InputNumber
                        inputId="integeronly"
                        value={seed}
                        onValueChange={(e) => {
                            setSeed(e.value);
                            Profile.seed = e.value;
                        }}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Num Ctx:</h5>
                    <p className="m-0">{numCTX}</p>
                    <InputNumber 
                        inputId="integeronly" 
                        value={numCTX} 
                        onValueChange={(e) => {
                            setNumCtx(e.value);
                            Profile.numCTX = e.value;
                        }}
                        min ={0}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Num Predict:</h5>
                    <p className="m-0">{numPredict}</p>
                    <InputNumber 
                        inputId="integeronly" 
                        value={numPredict} 
                        onValueChange={(e) => {
                            setNumPredict(e.value);
                            Profile.numPredict = e.value;
                        }}
                        min = {0}
                    />
                </div>
                <div className='Row'>
                    <h5 className="m-0">Stop:</h5>
                    <InputTextarea
                        autoResize
                        value={stop}
                        placeholder='Enter a stop phrase'
                        onChange={(e) => {
                            setStop(e.target.value)
                            Profile.stop = e.target.value;
                        }}
                        style={{ width: '100%' }} />
                </div>
            </Card>
        </div>
            <div className='island'>
                <Card className='Card100'>
                    <div className='Row'>
                        <FileUpload
                        name="jsonFile"
                        mode="basic"
                        accept=".json"
                        maxFileSize={1000000}
                        url="http://127.0.0.1:5000/JSONParse"
                        auto
                        chooseLabel="Upload JSON"
                        onUpload={(e) => {
                            const jsonData = JSON.parse(e.xhr.responseText);
                            /*https://stackoverflow.com/questions/34448724/iterating-over-a-dictionary-in-javascript*/
                            Object.keys(jsonData['data']).forEach(function(key){
                                Profile[key] = jsonData['data'][key]
                                updateAll({ Profile })
                            });
                        }}  
                        />
                        <Button 
                            label="Export JSON" 
                            onClick={() => downloadFile( {Profile} ) }
                        />
                    </div>
                </Card>
            </div>
        </>
    );
}