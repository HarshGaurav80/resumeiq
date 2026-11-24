// About page: project description, team, technologies and architecture (for college submission).
import { motion } from "framer-motion";
import { BrainCircuit, Database, Layers, Server } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// ✏️ Replace these with your real team details before submission.
const TEAM = [
  { name: "Team Member 1", role: "Team Lead · Backend & AI", roll: "Roll No. 000000" },
  { name: "Team Member 2", role: "Frontend & UI/UX", roll: "Roll No. 000000" },
  { name: "Team Member 3", role: "NLP & Testing", roll: "Roll No. 000000" },
  { name: "Team Member 4", role: "Database & Documentation", roll: "Roll No. 000000" },
];
const GUIDE = { name: "Prof. Project Guide", dept: "Department of Computer Science & Engineering" };

const TECH = [
  { icon: Layers, title: "Frontend", items: ["React 19 + Vite", "Tailwind CSS v4", "shadcn/ui components", "Framer Motion", "Recharts", "Sonner toasts"] },
  { icon: Server, title: "Backend", items: ["Python FastAPI", "pdfplumber (PDF)", "python-docx (DOCX)", "ReportLab (PDF reports)", "Pydantic validation"] },
  { icon: BrainCircuit, title: "AI & NLP", items: ["Google Gemini API", "OpenAI API (optional)", "TF-IDF + cosine similarity", "300+ skill keyword matcher", "Rule-based section parser"] },
  { icon: Database, title: "Storage", items: ["SQLite database", "Analysis history", "REST API with OpenAPI docs"] },
];

const FLOW = [
  "User uploads a resume (PDF/DOCX) and pastes a job description.",
  "Backend validates the file and extracts text with pdfplumber / python-docx.",
  "Text + job description are sent to Gemini/OpenAI with a strict-JSON prompt.",
  "The JSON is validated with Pydantic; scores are clamped and lists cleaned.",
  "If no API key is set or the AI fails, the offline analyzer runs: skill keyword matching + TF-IDF cosine similarity + heuristic section scoring.",
  "The result is saved in SQLite and rendered as a dashboard; a PDF report can be downloaded.",
];

const initials = (n) => n.split(" ").map((w) => w[0]).slice(0, 2).join("");

export default function About() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          About <span className="text-gradient">ResumeIQ</span>
        </h1>
        <p className="mx-auto mt-4 max-w-3xl leading-relaxed text-muted-foreground">
          ResumeIQ is an AI-powered resume analyzer built as a final-year college project. Many resumes are rejected by
          Applicant Tracking Systems (ATS) before a recruiter ever reads them. ResumeIQ helps students and job seekers
          understand how well their resume matches a specific job, which skills are missing, and exactly how to improve it —
          combining Large Language Models with classic NLP techniques so it works even without an internet AI service.
        </p>
      </motion.section>

      {/* Objectives */}
      <section className="mt-12 grid gap-4 sm:grid-cols-3">
        {[
          ["Objective", "Automate resume screening feedback that normally requires a career counsellor or recruiter."],
          ["Problem", "Candidates don't know why they're rejected — missing keywords, weak bullets or ATS-unfriendly formatting."],
          ["Outcome", "An instant, explainable match score with skill gaps and actionable suggestions, plus a downloadable report."],
        ].map(([t, d], i) => (
          <motion.div key={t} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
            <Card className="h-full">
              <CardContent className="p-5">
                <h3 className="font-semibold text-violet-600 dark:text-violet-400">{t}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{d}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* How it works (architecture) */}
      <section className="mt-14">
        <h2 className="mb-6 text-2xl font-bold">System workflow</h2>
        <ol className="relative space-y-4 border-l-2 border-violet-200 pl-6 dark:border-violet-900">
          {FLOW.map((step, i) => (
            <li key={i} className="relative">
              <span className="bg-brand absolute -left-[35px] grid size-6 place-items-center rounded-full text-xs font-bold text-white">{i + 1}</span>
              <p className="text-sm leading-relaxed">{step}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Technologies */}
      <section className="mt-14">
        <h2 className="mb-6 text-2xl font-bold">Technologies used</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {TECH.map(({ icon: Icon, title, items }) => (
            <Card key={title}>
              <CardHeader>
                <CardTitle><Icon className="size-4 text-violet-500" /> {title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {items.map((t) => (
                    <span key={t} className="rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">{t}</span>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="mt-14">
        <h2 className="mb-6 text-2xl font-bold">Team</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {TEAM.map((m) => (
            <Card key={m.name + m.role}>
              <CardContent className="flex flex-col items-center p-6 text-center">
                <div className="bg-brand grid size-16 place-items-center rounded-full text-lg font-bold text-white">{initials(m.name)}</div>
                <p className="mt-3 font-semibold">{m.name}</p>
                <p className="text-sm text-muted-foreground">{m.role}</p>
                <p className="mt-1 text-xs text-muted-foreground">{m.roll}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        <p className="mt-6 text-center text-sm text-muted-foreground">
          Under the guidance of <span className="font-medium text-foreground">{GUIDE.name}</span>, {GUIDE.dept}
        </p>
      </section>
    </div>
  );
}
