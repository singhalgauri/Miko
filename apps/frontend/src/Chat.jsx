import { useState, useRef, useEffect } from "react";
import Icon from "./icon";
import { askAgent, MOCK } from "./agent";

const starters = [
  "When is the fee payment due?",
  "Write a test for the date parser",
  "Check my urgent emails",
  "Delete my old photos",
];

const greeting = {
  id: 0,
  role: "agent",
  text: "Hi! I am your Sovereign Agent. Ask me about your files, emails or code. You can also attach documents and I will read them.",
};

export default function Chat() {
  const [messages, setMessages] = useState([greeting]);
  const [input, setInput] = useState("");
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const lastFiles = useRef([]);
  const idRef = useRef(1);
  const endRef = useRef(null);
  const fileInput = useRef(null);

  useEffect(() => {
    endRef.current && endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  function addFiles(list) {
    const picked = Array.from(list);
    setFiles((prev) => [...prev, ...picked]);
  }

  async function send(textArg) {
    const text = (textArg !== undefined ? textArg : input).trim();
    if ((!text && files.length === 0) || busy) return;
    const names = files.map((f) => f.name);
    if (names.length) lastFiles.current = names;
    setMessages((m) => [...m, { id: idRef.current++, role: "user", text, files: names }]);
    setInput("");
    setFiles([]);
    setBusy(true);
    const reply = await askAgent(text, names, lastFiles.current);
    setMessages((m) => [...m, { id: idRef.current++, role: "agent", ...reply }]);
    setBusy(false);
  }

  function decide(id, answer) {
    setMessages((m) => [
      ...m.map((x) => (x.id === id ? { ...x, approval: { ...x.approval, state: answer } } : x)),
      {
        id: idRef.current++,
        role: "agent",
        text: answer === "approved" ? "Done. I saved it and added it to the activity log. You can undo it any time." : "Okay, I did not save anything.",
      },
    ]);
  }

  const showStarters = messages.length === 1;

  return (
    <div
      className="chat"
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }}
    >
      <div className="msgs">
        {messages.map((m) =>
          m.role === "user" ? (
            <div className="msg user" key={m.id}>
              <div className="bubble">
                {m.files && m.files.length > 0 && (
                  <div className="attached" style={{ marginBottom: m.text ? 6 : 0 }}>
                    {m.files.map((f) => (
                      <span className="file-chip on-user" key={f}><Icon name="file" size={12} /> {f}</span>
                    ))}
                  </div>
                )}
                {m.text}
              </div>
            </div>
          ) : (
            <div className="msg agent" key={m.id}>
              <div className="av"><Icon name="spark" size={15} /></div>
              <div className="agent-body">
                {m.steps && (
                  <div className="steps">
                    {m.steps.map((s, i) => (
                      <div className="step" key={s.node} style={{ animationDelay: i * 0.25 + "s" }}>
                        <span className="tick"><Icon name="check" size={13} /></span>
                        <code>{s.node}</code> {s.label}
                      </div>
                    ))}
                  </div>
                )}
                <div className="bubble">{m.text}</div>

                {m.code && (
                  <div className="codeblock">
                    <div className="cb-head"><span><Icon name="code" size={12} /> {m.code.file}</span></div>
                    <pre>{m.code.text}</pre>
                  </div>
                )}

                {m.sources && (
                  <div>
                    {m.sources.map((s) => (
                      <span className="source" key={s.file + s.page}><Icon name="file" size={13} /> {s.file} · page {s.page}</span>
                    ))}
                  </div>
                )}

                {m.approval && (
                  <div className="card approve-card">
                    <b>{m.approval.title}</b>
                    <p>{m.approval.detail}</p>
                    {m.approval.state === "pending" ? (
                      <div className="row">
                        <button className="btn primary small" onClick={() => decide(m.id, "approved")}>Approve</button>
                        <button className="btn small danger" onClick={() => decide(m.id, "rejected")}>Reject</button>
                      </div>
                    ) : (
                      <div style={{ fontSize: 12.5, fontWeight: 700, color: m.approval.state === "approved" ? "var(--green)" : "var(--red)" }}>
                        {m.approval.state === "approved" ? "Approved" : "Rejected"}
                      </div>
                    )}
                  </div>
                )}

                {m.options && (
                  <div className="chips wrap">
                    {m.options.map((o) => (
                      <button className="chip" key={o} onClick={() => send(o)}>{o}</button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        )}

        {busy && (
          <div className="msg agent">
            <div className="av"><Icon name="spark" size={15} /></div>
            <div className="bubble typing"><span /><span /><span /></div>
          </div>
        )}

        {showStarters && (
          <div className="starters">
            {starters.map((s) => (
              <button key={s} onClick={() => send(s)}>{s}</button>
            ))}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className={"composer" + (dragging ? " dragging" : "")}>
        {files.length > 0 && (
          <div className="attached">
            {files.map((f, i) => (
              <span className="file-chip" key={f.name + i}>
                <Icon name="file" size={12} /> {f.name}
                <button onClick={() => setFiles(files.filter((_, j) => j !== i))} title="Remove"><Icon name="close" size={12} /></button>
              </span>
            ))}
          </div>
        )}
        <div className="input-row">
          <button className="icon-btn" title="Attach documents" onClick={() => fileInput.current.click()}>
            <Icon name="clip" size={18} />
          </button>
          <input
            ref={fileInput}
            type="file"
            multiple
            style={{ display: "none" }}
            onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }}
          />
          <input
            value={input}
            placeholder={dragging ? "Drop files here..." : "Ask anything, or attach a document..."}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button className="send" title="Send" onClick={() => send()}><Icon name="send" size={16} /></button>
        </div>
        {MOCK && <div className="preview-note">Preview mode: replies are sample data until the backend is connected</div>}
      </div>
    </div>
  );
}