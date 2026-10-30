// All data here is made up. Person 1/2's backend will replace it later.

export const sampleEmails = [
  { id: 1, from: "Rahul Verma", subject: "Meeting moved to 3 PM today", preview: "Hi, the team sync is now at 3 PM in the main hall.", time: "09:41", tag: "urgent", draft: "Thanks Rahul, I will join the 3 PM meeting." },
  { id: 2, from: "College Office", subject: "Fee payment last date is Friday", preview: "This is a reminder that the last date for fee payment is Friday.", time: "09:12", tag: "urgent", draft: "Thank you for the reminder. I will pay the fee before Friday." },
  { id: 3, from: "Hackathon Team", subject: "Can you share the demo script?", preview: "Please send the demo script so we can review it tonight.", time: "08:50", tag: "normal", draft: "Sure, I will share the script by tonight." },
  { id: 4, from: "Priya Nair", subject: "Notes from yesterday's class", preview: "Attaching my notes in case you missed the last lecture.", time: "08:20", tag: "normal", draft: "" },
  { id: 5, from: "GitHub", subject: "New sign-in to your account", preview: "We noticed a new sign-in from Windows.", time: "07:58", tag: "normal", draft: "" },
  { id: 6, from: "Library", subject: "Book due date reminder", preview: "Your borrowed book is due in 2 days.", time: "07:30", tag: "normal", draft: "" },
  { id: 7, from: "Mega Deals", subject: "You won a free phone! Click now", preview: "Claim your prize in the next 5 minutes.", time: "06:15", tag: "spam", draft: "" },
  { id: 8, from: "Cheap Loans Ltd", subject: "Get money in 5 minutes", preview: "No documents needed. Apply today.", time: "05:40", tag: "spam", draft: "" },
];

export const sampleRequests = [
  { id: 1, kind: "email", title: "Send reply to Rahul Verma", detail: "\"Thanks Rahul, I will join the 3 PM meeting.\"" },
  { id: 2, kind: "files", title: "Move 12 old files to Archive", detail: "From Downloads to Documents/Archive" },
  { id: 3, kind: "delete", title: "Delete 5 duplicate photos", detail: "Found in Pictures/Events. This cannot be undone." },
];

export const sampleLog = [
  { id: 1, time: "09:10", kind: "briefing", text: "Wrote today's briefing", canUndo: false },
  { id: 2, time: "09:07", kind: "files", text: "Renamed scan001.jpg to passport_copy.jpg", canUndo: true },
  { id: 3, time: "09:05", kind: "email", text: "Marked 2 emails as urgent", canUndo: false },
  { id: 4, time: "09:02", kind: "files", text: "Moved invoice_final_v2.pdf to Documents/Bills", canUndo: true },
  { id: 5, time: "08:58", kind: "email", text: "Moved 2 spam emails to Spam", canUndo: false },
];

export const sampleRules = [
  { id: "move", label: "Move or rename files", hint: "Organise your folders", choice: "ask" },
  { id: "delete", label: "Delete files", hint: "Risky. Off by default", choice: "never" },
  { id: "label", label: "Mark emails as important", hint: "Triage your inbox", choice: "alone" },
  { id: "send", label: "Send an email reply", hint: "Always check drafts first", choice: "ask" },
];

export const sampleFileChanges = [
  { id: 1, oldName: "scan001.jpg", newName: "passport_copy.jpg", oldFolder: "Downloads", newFolder: "Documents/ID" },
  { id: 2, oldName: "invoice_final_v2.pdf", newName: "invoice_4471.pdf", oldFolder: "Downloads", newFolder: "Documents/Bills" },
  { id: 3, oldName: "IMG_2041.png", newName: "team_photo.png", oldFolder: "Desktop", newFolder: "Pictures/Events" },
  { id: 4, oldName: "notes (1).txt", newName: "hackathon_notes.txt", oldFolder: "Downloads", newFolder: "Documents/Projects" },
  { id: 5, oldName: "fee_notice_copy.pdf", newName: "fee_notice.pdf", oldFolder: "Downloads", newFolder: "Documents/College" },
  { id: 6, oldName: "New Document.docx", newName: "team_plan.docx", oldFolder: "Desktop", newFolder: "Documents/Projects" },
];

export const sampleCatchUp = {
  awayFor: "You were away for 9 hours",
  stats: [
    { label: "Emails checked", value: 24 },
    { label: "Marked urgent", value: 2 },
    { label: "Spam removed", value: 2 },
    { label: "Files organised", value: 6 },
  ],
  briefing: "2 urgent emails need you: Rahul moved the meeting to 3 PM, and the college fee is due Friday. 3 replies are drafted and 6 files were sorted.",
};

export const sampleDocAnswers = [
  {
    id: 1,
    question: "When is the fee payment due?",
    keywords: ["fee", "payment", "due", "college"],
    answer: "The fee payment is due this Friday. A late fee of 500 rupees applies after that.",
    sources: [{ file: "fee_notice.pdf", page: 1 }],
  },
  {
    id: 2,
    question: "What did we decide in the hackathon meeting?",
    keywords: ["hackathon", "meeting", "decide", "decided"],
    answer: "The team decided to build a local-first agent with four jobs: inbox, files, document search and a daily briefing.",
    sources: [
      { file: "hackathon_notes.txt", page: 1 },
      { file: "team_plan.docx", page: 2 },
    ],
  },
  {
    id: 3,
    question: "What is the total on invoice 4471?",
    keywords: ["invoice", "4471", "total", "amount"],
    answer: "Invoice 4471 has a total of 12,400 rupees, due in 15 days.",
    sources: [{ file: "invoice_4471.pdf", page: 1 }],
  },
];

export const roadmap = [
  { name: "Coding agent", note: "Tests and small fixes in a safe sandbox", phase: "Phase 2" },
  { name: "Reviewer agent", note: "Checks the coding agent's work", phase: "Phase 2" },
  { name: "Authoring agent", note: "Reports and slides as Word and PowerPoint", phase: "Phase 2" },
  { name: "Research agent", note: "Web research, only when you allow it", phase: "Phase 2" },
  { name: "Custom agent builder", note: "Build your own agents without code", phase: "Phase 3" },
  { name: "Scheduled monitors", note: "Watch things and alert you later", phase: "Phase 3" },
];