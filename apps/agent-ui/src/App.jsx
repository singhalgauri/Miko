import { useState, useEffect } from "react";
import Icon from "./icon";
import Chat from "./chat";
import { Today, Inbox, Documents, Files, Approvals, Permissions } from "./screens";
import { sampleLog, sampleRequests } from "./sampleData";

const nav = [
  { id: "chat", label: "Chat", icon: "chat" },
  { id: "today", label: "Today", icon: "zap" },
  { id: "inbox", label: "Inbox", icon: "inbox" },
  { id: "docs", label: "Docs", icon: "doc" },
  { id: "files", label: "Files", icon: "folder" },
  { id: "approvals", label: "Approve", icon: "check" },
  { id: "rules", label: "Rules", icon: "shield" },
];

export default function App() {
  const [tab, setTab] = useState("chat");
  const [provider, setProvider] = useState("nebius");
  const [log, setLog] = useState(sampleLog);
  const [requests, setRequests] = useState(sampleRequests);
  const [resetCount, setResetCount] = useState(0);
  const [toastText, setToastText] = useState("");
  const [wide, setWide] = useState(window.innerWidth >= 700);

  useEffect(() => {
    const onResize = () => setWide(window.innerWidth >= 700);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  function switchMode() {
    if (window.agent) window.agent.setMode(wide ? "side" : "full");
  }

  const toast = (t) => { setToastText(t); setTimeout(() => setToastText(""), 1800); };
  const cloud = provider === "nebius";

  function resetAll() {
    setLog(sampleLog); setRequests(sampleRequests); setResetCount(resetCount + 1); setTab("chat");
    toast("Sample data reset");
  }

  return (
    <div className={"shell" + (wide ? " wide" : "")}>
      <div className="header">
        <div className="logo"><Icon name="spark" size={18} /></div>
        <div>
          <div className="title">Sovereign Agent</div>
          <div className="status"><span className="dot" /> Running in background</div>
        </div>
        <div className="grow" />
        {window.agent && (
          <button className="icon-btn" title={wide ? "Dock to the side" : "Full screen"} onClick={switchMode}>
            <Icon name={wide ? "side" : "expand"} />
          </button>
        )}
        <button className="icon-btn" title="Switch local / Nebius (demo)" onClick={() => setProvider(cloud ? "local" : "nebius")}>
          <Icon name={cloud ? "cloud" : "lock"} />
        </button>
        <button className="icon-btn" title="Reset sample data" onClick={resetAll}><Icon name="refresh" /></button>
      </div>

      <div className={"provider " + (cloud ? "cloud" : "local")}>
        <Icon name={cloud ? "cloud" : "lock"} size={15} />
        {cloud ? "Nebius mode: prompts leave this machine" : "Local mode: everything stays on this machine"}
      </div>

      <div className="content chat-mode" key={"c" + resetCount} style={tab === "chat" ? undefined : { display: "none" }}>
        <Chat />
      </div>

      {tab !== "chat" && (
        <div className="content" key={tab + resetCount}>
          {tab === "today" && <Today log={log} onUndo={(id) => { setLog(log.filter((l) => l.id !== id)); toast("Change undone"); }} go={setTab} />}
          {tab === "inbox" && <Inbox toast={toast} />}
          {tab === "docs" && <Documents />}
          {tab === "files" && <Files toast={toast} />}
          {tab === "approvals" && <Approvals requests={requests} onDecide={(id, a) => { setRequests(requests.filter((r) => r.id !== id)); toast(a); }} />}
          {tab === "rules" && <Permissions />}
        </div>
      )}

      {toastText && <div className="toast">{toastText}</div>}

      <div className="nav">
        {nav.map((n) => (
          <button key={n.id} className={tab === n.id ? "on" : ""} onClick={() => setTab(n.id)}>
            <Icon name={n.icon} size={19} />
            {n.label}
            {n.id === "approvals" && requests.length > 0 && <span className="pip">{requests.length}</span>}
          </button>
        ))}
      </div>
    </div>
  );
}