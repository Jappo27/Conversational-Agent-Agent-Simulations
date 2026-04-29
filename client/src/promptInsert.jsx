import React, { useState, useEffect } from "react";
import { Card } from "primereact/card";
import { InputTextarea } from "primereact/inputtextarea";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { FileUpload } from "primereact/fileupload";
import AutocompleteDrop from "./autocompletedropdown.jsx";

export default function PromptInsert({ prompt, setPrompt }) {
    //I have misnamed this - This is the personna set up
    //CBT and fix
    const [format, setFormat] = useState(prompt);
    const [showDialog, setShowDialog] = useState(false);

    const createField = (fieldType, options = null) => {
        const id = Date.now();
        return {
            id,
            data: {
                name: "",
                value: "",
                fieldType,
                options
            }
        };
    };

    const addField = (fieldType, options = null) => {
        const { id, data } = createField(fieldType, options);
        setFormat(prev => ({
            ...prev,
            [id]: data
        }));
        setShowDialog(false);
    };

    const updateField = (id, updates) => {
        setFormat(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                ...updates
            }
        }));
    };

    const removeField = id => {
        setFormat(prev => {
            const copy = { ...prev };
            delete copy[id];
            return copy;
        });
    };

    useEffect(() => {
        setPrompt(format);
    }, [format]);

    const downloadFile = ( {format} ) => {
        //https://stackoverflow.com/questions/55613438/reactwrite-to-json-file-or-export-download-no-server

        // create file in browser
        const fileName = "Persona";
        const json = JSON.stringify(format, null, 4);
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


    return (
        <><Card className="Card" style={{ margin: "0 auto" }}>
            <div className="Row">
                <Button label="Add Field" onClick={() => setShowDialog(true)} />
            </div>

            <Dialog
                header="Insert Field"
                visible={showDialog}
                style={{ width: "50vw" }}
                onHide={() => setShowDialog(false)}
            >
                <div className="Row">
                    <Button
                        label="Add Text Field"
                        onClick={() => addField("Text")}
                        className="mb-2"
                    />

                    <FileUpload
                        name="file"
                        mode="basic"
                        accept=".txt"
                        maxFileSize={1000000}
                        url="http://127.0.0.1:5000/TXTParse"
                        auto
                        chooseLabel="Upload Text File"
                        onUpload={e => {
                            try {
                                const parsed = JSON.parse(e.xhr.responseText);
                                addField("Drop", parsed.data);
                            } catch (err) {
                                console.error("Failed to parse JSON:", err);
                            }
                        }}
                    />

                    <Button
                        label="Add Bool Field"
                        onClick={() =>
                            addField("Drop", ["Yes", "No", "Did not state"])
                        }
                    />
                </div>
            </Dialog>

            <div>
                {Object.entries(format).map(([id, field]) => (
                    <div className="Row" key={id}>
                        <Button
                            label="Delete Field"
                            onClick={() => removeField(id)}
                            style={{ width: "20%" }}
                        />

                        <div className="Row" style={{ width: "100%" }}>
                            <InputTextarea
                                autoResize
                                value={field.name}
                                placeholder="Field name"
                                onChange={e => updateField(id, { name: e.target.value })}
                                style={{ width: "30%" }}
                            />

                            {field.fieldType === "Text" && (
                                <InputTextarea
                                    autoResize
                                    value={field.value}
                                    placeholder="Field value"
                                    onChange={e => updateField(id, { value: e.target.value })}
                                    style={{ minWidth: "70%" }}
                                />
                            )}

                            {field.fieldType === "Drop" && (
                                <AutocompleteDrop
                                    autoResize
                                    elements={field.options}
                                    value={field.value}
                                    onChange={val => updateField(id, { value: val })}
                                    style={{ minWidth: "50%" }}
                                />
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </Card>
        <div className='island'>
            <Card className='Card100'>
                <div className='Row'>
                    <FileUpload
                        name="jsonFile"
                        mode="basic"
                        accept=".json"
                        maxFileSize={1000000}
                        url="http://127.0.0.1:5000/JSONTXTParse"
                        auto
                        chooseLabel="Upload JSON"
                        onUpload={(e) => {
                            try {
                                const jsonData = JSON.parse(e.xhr.responseText);
                                setFormat(jsonData["data"])
                            }
                            catch (err) {
                                console.log(error)
                            };
                            /*https://stackoverflow.com/questions/34448724/iterating-over-a-dictionary-in-javascript*/
                            }}  
                    />
                    <Button 
                        label="Export JSON" 
                        onClick={() => downloadFile( {format} ) }
                    />
                </div>
            </Card>
        </div>
        </>
    );
}