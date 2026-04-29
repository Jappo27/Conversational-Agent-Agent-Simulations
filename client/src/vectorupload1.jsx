import { useRef } from 'react';
import { Card } from 'primereact/card';
import { FileUpload } from 'primereact/fileupload';
import { Messages } from 'primereact/messages';

export default function VectorUpload1() { 
    const msgs = useRef(null);

    const addMessagesSuccess = () => {
        msgs.current.show([
            { severity: 'success', summary: 'Success', detail: 'File Uploaded', sticky: true, closable: true }
        ]);
    };

    const addMessagesFailure = () => {
        msgs.current.show([
            { severity: 'error', summary: 'Error', detail: 'Error In Upload', sticky: true, closable: true }
        ]);
    };

    return (         
        <> 
        <div>
            <Messages ref={msgs} />
            <Card className="Card" title="Upload supporting RAG PDF's" style={{ margin: "0 auto" }}>
                <FileUpload
                    name="Pdf"
                    mode="basic"
                    maxFileSize={1000000}
                    url="http://127.0.0.1:5000/PDFCheck1"
                    auto
                    chooseLabel="Upload PDF"
                    onUpload={e => {
                        try {
                            const parsed = JSON.parse(e.xhr.responseText);
                            if (parsed.status == "Success") {
                                addMessagesSuccess()
                            } else {
                                addMessagesFailure()
                            }
                        } catch (err) {
                            addMessagesFailure()
                            console.error("Failed to parse PDF:", err);
                        }
                    }}
                    onError={e => {
                        try {
                            const parsed = JSON.parse(e.xhr.responseText);
                            addMessagesFailure(parsed.reason || "Upload failed");
                        } catch {
                            addMessagesFailure("Upload failed");
                        }
                    }}
                />
            </Card>
        </div>
        </>     
  );
}