import { useState } from "react";
import Icon from "./icon";
import {
  sampleEmails, sampleFileChanges, sampleCatchUp, sampleDocAnswers, sampleRules, roadmap,
} from "./sampleData";

const avatarColors = ["#7c6cff", "#2dd4a0", "#f5a524", "#f4607a", "#5b8cff", "#a855f7", "#14b8a6", "#ef6c3a"];
const colorFor = (name) => avatarColors[[...name].reduce((a, c) => a + c.charCodeAt(0), 0) % avatarColors.length];
const initials = (name) => name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();

/* ---------- Today ---------- */
export function Today({ log, onUndo, go }) {
  return (
    <>
      <h1 className="page-title">Welcome back</h1>
      <p className="page-sub">{sampleCatchUp.awayFor}. Here is what your agent did.</p>

      <div className="hero">
        <div className="label row"><Icon name="spark" size={14} /> Daily briefing</div>
        <p>{sampleCatchUp.briefing}</p>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="btn primary small" onClick={() => go("inbox")}>Open inbox</button>
          <button className="btn small" onClick={() => go("approvals")}>Review approvals</button>
        </div>
      </div>

      <div className="stats">
        {sampleCatchUp.stats.map((s) => (
          <div className="stat" key={s.label}><b>{s.value}</b><span>{s.label}</span></div>
        ))}
      </div>

      <div className="section-title">Activity log</div>
      <div className="card" style={{ padding: "2px 14px" }}>
        {log.length === 0 && <div className="empty">Nothing here. Press reset to restore the sample data.</div>}
        {log.map((item) => (
          <div className="list-item" key={item.id}>
            <div
              style={{
                width: 34, height: 34, borderRadius: 10, display: "grid", placeItems: "center",
                background: item.kind === "files" ? "rgba(124,108,255,.15)" : "rgba(91,140,255,.15)",
                color: item.kind === "files" ? "var(--accent)" : "var(--accent-2)",
              }}
            >
              <Icon name={item.kind === "files" ? "folder" : item.kind === "briefing" ? "spark" : "mail"} size={16} />
            </div>
            <div className="li-main">
              {item.text}
              <div className="li-time">{item.time}</div>
            </div>
            {item.canUndo && (
              <button className="btn small" onClick={() => onUndo(item.id)}>
                <span className="row" style={{ gap: 5 }}><Icon name="undo" size={12} /> Undo</span>
              </button>
            )}
          </div>
        ))}
      </div>
    </>
  );
}

/* ---------- Inbox ---------- */
export function Inbox({ toast }) {
  const [filter, setFilter] = useState("all");
  const [openId, setOpenId] = useState(null);
  const [sent, setSent] = useState([]);
  const shown = sampleEmails.filter((m) => filter === "all" || m.tag === filter);
  const counts = (t) => sampleEmails.filter((m) => m.tag === t).length;

  return (
    <>
      <h1 className="page-title">Inbox</h1>
      <p className="page-sub">Your agent sorted {sampleEmails.length} emails and drafted replies.</p>

      <div className="chips">
        {[["all", "All"], ["urgent", `Urgent ${counts("urgent")}`], ["normal", `Normal ${counts("normal")}`], ["spam", `Spam ${counts("spam")}`]].map(([k, label]) => (
          <button key={k} className={"chip" + (filter === k ? " on" : "")} onClick={() => setFilter(k)}>{label}</button>
        ))}
      </div>

      {shown.map((m) => (
        <div className="mail" key={m.id}>
          <button className="mail-head" onClick={() => setOpenId(openId === m.id ? null : m.id)}>
            <div className="avatar" style={{ background: colorFor(m.from) }}>{initials(m.from)}</div>
            <div className="mail-main">
              <span className={"badge " + m.tag}>{m.tag.toUpperCase()}</span>
              <div className="mail-top"><span className="mail-from">{m.from}</span><span className="mail-time">{m.time}</span></div>
              <div className="mail-subject">{m.subject}</div>
              {openId !== m.id && <div className="mail-preview">{m.preview}</div>}
            </div>
          </button>
          {openId === m.id && (
            <div className="mail-body">
              <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>{m.preview}</p>
              {m.draft ? (
                <>
                  <div className="draft"><small><Icon name="spark" size={12} /> Agent's drafted reply</small>{m.draft}</div>
                  {sent.includes(m.id) ? (
                    <div className="row" style={{ color: "var(--green)", fontSize: 13, fontWeight: 600 }}>
                      <Icon name="check" size={15} /> Reply approved and sent
                    </div>
                  ) : (
                    <div className="row">
                      <button className="btn primary small" onClick={() => { setSent([...sent, m.id]); toast("Reply sent"); }}>
                        <span className="row" style={{ gap: 6 }}><Icon name="send" size={12} /> Approve and send</span>
                      </button>
                      <button className="btn small">Edit</button>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ fontSize: 12.5, color: "var(--muted)", marginTop: 8 }}>No reply needed.</div>
              )}
            </div>
          )}
        </div>
      ))}
    </>
  );
}

/* ---------- Documents ---------- */
export function Documents() {
  const [query, setQuery] = useState("");
  const [state, setState] = useState("idle"); // idle | thinking | done
  const [result, setResult] = useState(null);

  function search(text) {
    const q = text.toLowerCase();
    if (!q.trim()) return;
    setState("thinking");
    setTimeout(() => {
      setResult(sampleDocAnswers.find((d) => d.keywords.some((k) => q.includes(k))) || null);
      setState("done");
    }, 700);
  }

  return (
    <>
      <h1 className="page-title">Ask your documents</h1>
      <p className="page-sub">Answers come with the file and page they were found in.</p>

      <div className="search">
        <Icon name="search" size={16} />
        <input value={query} placeholder="Ask a question about your files..."
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search(query)} />
        <button className="btn primary small" onClick={() => search(query)}>Ask</button>
      </div>

      <div className="suggest">
        {sampleDocAnswers.map((d) => (
          <button key={d.id} onClick={() => { setQuery(d.question); search(d.question); }}>{d.question}</button>
        ))}
      </div>

      {state === "thinking" && <div className="thinking"><div className="spinner" /> Searching your documents...</div>}

      {state === "done" && result && (
        <div className="card answer" style={{ marginTop: 16 }}>
          <div className="section-title" style={{ margin: "0 0 8px" }}><Icon name="spark" size={12} /> Answer</div>
          <p>{result.answer}</p>
          <div className="section-title" style={{ margin: "14px 0 0" }}>Sources</div>
          {result.sources.map((s) => (
            <span className="source" key={s.file + s.page}><Icon name="file" size={13} /> {s.file} · page {s.page}</span>
          ))}
        </div>
      )}
      {state === "done" && !result && (
        <div className="card" style={{ marginTop: 16, color: "var(--muted)", fontSize: 13 }}>
          I could not find this in your documents.
        </div>
      )}
    </>
  );
}

/* ---------- Files ---------- */
export function Files({ toast }) {
  const [undone, setUndone] = useState([]);
  return (
    <>
      <h1 className="page-title">File organiser</h1>
      <p className="page-sub">Every change is logged. You can undo any of them.</p>
      {sampleFileChanges.map((c) => {
        const isUndone = undone.includes(c.id);
        return (
          <div className="card file-card" key={c.id}>
            {isUndone ? (
              <div className="row" style={{ justifyContent: "space-between" }}>
                <div className="names"><b>{c.oldName}</b><div className="path">Restored to {c.oldFolder}</div></div>
                <span style={{ color: "var(--green)", fontSize: 12, fontWeight: 700 }}>Undone</span>
              </div>
            ) : (
              <div className="row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                <div className="names">
                  <span className="old">{c.oldName}</span><br />
                  <span className="new">{c.newName}</span>
                  <div className="path"><Icon name="folder" size={13} /> {c.oldFolder} <Icon name="arrow" size={12} /> {c.newFolder}</div>
                </div>
                <button className="btn small" onClick={() => { setUndone([...undone, c.id]); toast("File restored"); }}>
                  <span className="row" style={{ gap: 5 }}><Icon name="undo" size={12} /> Undo</span>
                </button>
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}

/* ---------- Approvals ---------- */
export function Approvals({ requests, onDecide }) {
  return (
    <>
      <h1 className="page-title">Needs your approval</h1>
      <p className="page-sub">The agent will not do these until you say yes.</p>
      {requests.length === 0 && (
        <div className="card empty"><div style={{ color: "var(--green)", marginBottom: 6 }}><Icon name="check" size={26} /></div>All caught up. Nothing is waiting.</div>
      )}
      {requests.map((r) => (
        <div className="card approval" key={r.id}>
          <div className={"ic " + r.kind}><Icon name={r.kind === "email" ? "mail" : r.kind === "files" ? "folder" : "trash"} size={18} /></div>
          <div>
            <h3>{r.title}</h3>
            <p>{r.detail}</p>
            <div className="row">
              <button className="btn primary small" onClick={() => onDecide(r.id, "Approved")}>Approve</button>
              <button className="btn small danger" onClick={() => onDecide(r.id, "Rejected")}>Reject</button>
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

/* ---------- Permissions ---------- */
export function Permissions() {
  const [rules, setRules] = useState(sampleRules);
  const set = (id, choice) => setRules(rules.map((r) => (r.id === id ? { ...r, choice } : r)));
  return (
    <>
      <h1 className="page-title">Permissions</h1>
      <p className="page-sub">You decide what the agent can do alone, what it must ask about, and what it must never do.</p>
      {rules.map((r) => (
        <div className="card" key={r.id}>
          <div className="rule"><div><b>{r.label}</b><span className="hint">{r.hint}</span></div></div>
          <div className="seg">
            {[["alone", "Act alone"], ["ask", "Ask first"], ["never", "Never"]].map(([k, label]) => (
              <button key={k} className={k + (r.choice === k ? " on" : "")} onClick={() => set(r.id, k)}>{label}</button>
            ))}
          </div>
        </div>
      ))}

      <div className="section-title">Coming soon</div>
      {roadmap.map((f) => (
        <div className="card road" key={f.name}>
          <div><b>{f.name}</b><p>{f.note}</p></div>
          <span className="phase">{f.phase}</span>
        </div>
      ))}
    </>
  );
}