import { sampleDocAnswers } from "./sampleData";

// PREVIEW MODE: replies below are sample data.
// When Person 1's backend is ready, replace the body of askAgent()
// with a fetch() call to the backend and return the same shape.
export const MOCK = true;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

const step = (node, label) => ({ node, label });

export async function askAgent(text, fileNames = [], lastFiles = []) {
  await wait(1000);
  const q = text.toLowerCase();

  // 1. The user shared documents
  if (fileNames.length > 0) {
    return {
      steps: [
        step("orchestrator", "Routing your request"),
        step("doc_read", "Reading " + fileNames.join(", ")),
        step("output_validator", "Checking the output"),
        step("guardrails_check", "Checking your permission rules"),
      ],
      text: "I read " + fileNames.join(", ") + ". What would you like to do with it?",
      options: ["Summarise it", "List the key dates", "Ask a question about it"],
    };
  }

  // 2. Dangerous request: blocked by the permission rules
  if (q.includes("delete") || q.includes("remove all")) {
    return {
      steps: [
        step("orchestrator", "Routing your request"),
        step("guardrails_check", "Checking your permission rules"),
      ],
      text: "I did not do this. Deleting files is set to Never in your Rules. You can change that in the Rules tab if you want me to.",
    };
  }

  // 3. Coding path
  if (q.includes("code") || q.includes("test") || q.includes("bug") || q.includes("function") || q.includes("fix")) {
    return {
      steps: [
        step("orchestrator", "Routing to the coding agent"),
        step("coding_agent", "Writing the change"),
        step("code_test_agent", "Running tests: 3 passed"),
        step("code_review_agent", "Reviewing the code: approved"),
        step("output_validator", "Checking the output"),
        step("guardrails_check", "Checking your permission rules"),
      ],
      text: "I wrote a test for the date parser. All 3 tests passed and the reviewer approved it.",
      code: {
        file: "tests/test_date_parser.py",
        text:
          "from utils import parse_date\n\n" +
          "def test_simple_date():\n" +
          "    assert parse_date('2026-10-30') == (2026, 10, 30)\n\n" +
          "def test_slash_date():\n" +
          "    assert parse_date('30/10/2026') == (2026, 10, 30)\n\n" +
          "def test_bad_date():\n" +
          "    assert parse_date('hello') is None\n",
      },
      approval: { title: "Save tests/test_date_parser.py?", detail: "This adds one new file to your project.", state: "pending" },
    };
  }

  // 4. Document question with sources
  const doc = sampleDocAnswers.find((d) => d.keywords.some((k) => q.includes(k)));
  if (doc) {
    return {
      steps: [
        step("orchestrator", "Routing to document search"),
        step("doc_read", "Searching your documents"),
        step("output_validator", "Checking the answer"),
      ],
      text: doc.answer,
      sources: doc.sources,
    };
  }

  // 5. Summaries of shared files
  if (q.includes("summar") || q.includes("key dates")) {
    const name = lastFiles.length ? lastFiles.join(", ") : "your document";
    return {
      steps: [
        step("orchestrator", "Routing to the document agent"),
        step("doc_read", "Reading " + name),
        step("doc_write", "Writing the summary"),
        step("output_validator", "Checking the output"),
        step("guardrails_check", "Checking your permission rules"),
        step("artifact_generator", "Creating summary.docx"),
      ],
      text: "I wrote a one-page summary of " + name + ".",
      approval: { title: "Save summary.docx to Documents?", detail: "This adds one new file.", state: "pending" },
    };
  }

  // 6. Email
  if (q.includes("email") || q.includes("inbox") || q.includes("urgent") || q.includes("mail")) {
    return {
      steps: [
        step("orchestrator", "Routing to the inbox agent"),
        step("output_validator", "Checking the output"),
      ],
      text: "You have 2 urgent emails: Rahul moved the meeting to 3 PM, and the college fee is due Friday. I drafted a reply to each. You can approve them in the Inbox tab.",
    };
  }

  // 7. Not clear: ask the user
  return {
    steps: [
      step("orchestrator", "Routing your request"),
      step("clarification_node", "Asking you a question"),
    ],
    text: "I am not sure what you mean. What would you like me to do?",
    options: ["Search my documents", "Write or fix code", "Check my urgent emails"],
  };
}