// Landing page: hero, feature cards, how-it-works steps and a closing call to action.
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, ClipboardList, Gauge, Lightbulb, ScanSearch, Sparkles, Target, Upload } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const features = [
  {
    icon: Gauge,
    title: "ATS Score",
    text: "See how Applicant Tracking Systems read your resume and get a compatibility score with formatting checks.",
  },
  {
    icon: Target,
    title: "Skill Gap Analysis",
    text: "Compare your skills against the job description and instantly spot the keywords you're missing.",
  },
  {
    icon: Lightbulb,
    title: "AI Suggestions",
    text: "Get specific, actionable fixes — weak bullet points rewritten with action verbs and measurable impact.",
  },
];

const steps = [
  { icon: Upload, title: "Upload your resume", text: "Drag and drop a PDF or DOCX file (up to 5 MB)." },
  { icon: ClipboardList, title: "Paste the job description", text: "Add the role you're applying for so we know what to match against." },
  { icon: ScanSearch, title: "Get your report", text: "Review your match score, skill gaps and suggestions — then download the PDF." },
];

// Stagger children into view as the user scrolls
const container = { hidden: {}, show: { transition: { staggerChildren: 0.12 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { duration: 0.45 } } };

export default function Landing() {
  return (
    <>
      {/* ---------------- Hero ---------------- */}
      <section className="relative overflow-hidden">
        {/* soft gradient glow */}
        <div aria-hidden className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center">
          <div className="h-[480px] w-[900px] rounded-full bg-gradient-to-r from-violet-400/30 via-indigo-400/25 to-fuchsia-300/20 blur-3xl dark:from-violet-700/25 dark:via-indigo-700/20 dark:to-fuchsia-700/10" />
        </div>

        <div className="mx-auto max-w-4xl px-4 pb-20 pt-20 text-center sm:px-6 sm:pt-28">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-xs font-medium text-muted-foreground shadow-sm"
          >
            <Sparkles className="size-3.5 text-violet-500" /> Powered by AI + NLP
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="text-4xl font-extrabold tracking-tight sm:text-6xl"
          >
            Get Your Resume <span className="text-gradient">Job-Ready</span> with AI
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 }}
            className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground"
          >
            Upload your resume, paste a job description, and ResumeIQ tells you how well you match — with an ATS score,
            the skills you're missing, and concrete suggestions to land more interviews.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Link to="/analyze" className={buttonVariants({ variant: "gradient", size: "lg" })}>
              Analyze My Resume <ArrowRight />
            </Link>
            <a href="#how-it-works" className={buttonVariants({ variant: "outline", size: "lg" })}>
              How it works
            </a>
          </motion.div>

          <p className="mt-6 text-xs text-muted-foreground">Free · No sign-up · PDF &amp; DOCX supported</p>
        </div>
      </section>

      {/* ---------------- Features ---------------- */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="mx-auto mb-10 max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight">Everything you need to stand out</h2>
          <p className="mt-3 text-muted-foreground">Three tools in one report, built for students and job seekers.</p>
        </div>
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.3 }}
          className="grid gap-6 md:grid-cols-3"
        >
          {features.map(({ icon: Icon, title, text }) => (
            <motion.div key={title} variants={item} whileHover={{ y: -4 }}>
              <Card className="h-full transition-shadow hover:shadow-lg hover:shadow-indigo-500/10">
                <CardContent className="p-6">
                  <div className="bg-brand mb-4 grid size-11 place-items-center rounded-xl text-white shadow-md shadow-indigo-500/30">
                    <Icon className="size-5" />
                  </div>
                  <h3 className="text-lg font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{text}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ---------------- How it works ---------------- */}
      <section id="how-it-works" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-16 sm:px-6">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight">How it works</h2>
          <p className="mt-3 text-muted-foreground">From upload to actionable report in under a minute.</p>
        </div>
        <motion.ol
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.3 }}
          className="grid gap-8 md:grid-cols-3"
        >
          {steps.map(({ icon: Icon, title, text }, i) => (
            <motion.li key={title} variants={item} className="relative flex flex-col items-center text-center">
              {/* connector line between steps on desktop */}
              {i < steps.length - 1 && (
                <div aria-hidden className="absolute left-[calc(50%+2.5rem)] top-7 hidden h-px w-[calc(100%-5rem)] bg-gradient-to-r from-violet-300 to-indigo-300 md:block dark:from-violet-800 dark:to-indigo-800" />
              )}
              <div className="relative grid size-14 place-items-center rounded-full border-2 border-violet-200 bg-card text-violet-600 dark:border-violet-900 dark:text-violet-400">
                <Icon className="size-6" />
                <span className="bg-brand absolute -right-1 -top-1 grid size-6 place-items-center rounded-full text-xs font-bold text-white">
                  {i + 1}
                </span>
              </div>
              <h3 className="mt-4 font-semibold">{title}</h3>
              <p className="mt-1 max-w-xs text-sm text-muted-foreground">{text}</p>
            </motion.li>
          ))}
        </motion.ol>
      </section>

      {/* ---------------- CTA ---------------- */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="bg-brand relative overflow-hidden rounded-2xl px-6 py-12 text-center text-white shadow-xl shadow-indigo-500/20"
        >
          <h2 className="text-2xl font-bold sm:text-3xl">Ready to see your score?</h2>
          <p className="mx-auto mt-2 max-w-lg text-white/80">It takes less than a minute. Your report is saved to your history.</p>
          <Link
            to="/analyze"
            className={cn(buttonVariants({ size: "lg" }), "mt-6 bg-white text-indigo-700 hover:bg-white/90")}
          >
            Analyze My Resume <ArrowRight />
          </Link>
        </motion.div>
      </section>
    </>
  );
}
