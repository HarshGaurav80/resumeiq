// Analyze page: resume drag-and-drop, job description, optional role, and submit.
import { useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { AnimatePresence, motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { CloudUpload, FileText, LoaderCircle, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
const MIN_JD = 30;
const ACCEPT = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
};
// Used if the backend's /api/roles can't be reached
const FALLBACK_ROLES = ["Software Developer", "Data Analyst", "Web Developer", "UI/UX Designer", "Data Scientist", "DevOps Engineer"];

// Messages cycled while the analysis runs
const LOADING_STEPS = ["Reading your resume…", "Extracting skills and sections…", "Comparing with the job description…", "Writing suggestions…"];

const formatSize = (bytes) => (bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(0)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`);

export default function Analyze() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [roles, setRoles] = useState(FALLBACK_ROLES);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    api.roles().then((r) => setRoles(r.roles)).catch(() => {});
  }, []);

  // Cycle loading messages
  useEffect(() => {
    if (!loading) return;
    setStep(0);
    const t = setInterval(() => setStep((s) => Math.min(s + 1, LOADING_STEPS.length - 1)), 2500);
    return () => clearInterval(t);
  }, [loading]);

  const onDrop = (accepted, rejected) => {
    if (rejected.length) {
      const code = rejected[0].errors[0]?.code;
      const msg =
        code === "file-too-large" ? "File is too large. Maximum size is 5 MB."
        : code === "file-invalid-type" ? "Only PDF and DOCX files are supported."
        : rejected[0].errors[0]?.message || "That file can't be used.";
      setErrors((e) => ({ ...e, file: msg }));
      toast.error(msg);
      return;
    }
    if (accepted[0]) {
      setFile(accepted[0]);
      setErrors((e) => ({ ...e, file: undefined }));
      toast.success(`${accepted[0].name} ready to analyze`);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPT,
    maxSize: MAX_SIZE,
    multiple: false,
    disabled: loading,
  });

  const validate = () => {
    const e = {};
    if (!file) e.file = "Please upload your resume (PDF or DOCX).";
    if (!jobDescription.trim()) e.jd = "Please paste the job description.";
    else if (jobDescription.trim().length < MIN_JD) e.jd = `Job description is too short (minimum ${MIN_JD} characters).`;
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) {
      toast.error("Please fix the highlighted fields.");
      return;
    }
    setLoading(true);
    try {
      const record = await api.analyze({ file, jobDescription: jobDescription.trim(), jobRole });
      if (record.notice) toast.warning(record.notice);
      toast.success("Analysis complete!");
      navigate(`/results/${record.id}`, { state: { record } });
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Analyze your <span className="text-gradient">resume</span>
        </h1>
        <p className="mt-2 text-muted-foreground">Upload your resume and paste the job description you're targeting.</p>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-6" noValidate>
        {/* ---------------- Upload ---------------- */}
        <Card>
          <CardHeader>
            <CardTitle>1. Upload resume</CardTitle>
            <CardDescription>PDF or DOCX, maximum 5 MB.</CardDescription>
          </CardHeader>
          <CardContent>
            <AnimatePresence mode="wait">
              {file ? (
                <motion.div
                  key="file"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-3 rounded-lg border bg-accent/50 p-4"
                >
                  <div className="bg-brand grid size-10 shrink-0 place-items-center rounded-lg text-white">
                    <FileText className="size-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{formatSize(file.size)}</p>
                  </div>
                  <Button type="button" variant="ghost" size="icon" onClick={() => setFile(null)} disabled={loading} aria-label="Remove file">
                    <X />
                  </Button>
                </motion.div>
              ) : (
                <motion.div key="drop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <div
                    {...getRootProps()}
                    className={cn(
                      "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors",
                      isDragActive ? "border-violet-500 bg-violet-50 dark:bg-violet-950/30" : "hover:border-violet-400 hover:bg-muted/50",
                      errors.file && "border-red-400",
                    )}
                  >
                    <input {...getInputProps()} aria-label="Resume file" />
                    <motion.div animate={isDragActive ? { y: -6, scale: 1.1 } : { y: 0, scale: 1 }}>
                      <CloudUpload className="size-10 text-violet-500" />
                    </motion.div>
                    <p className="mt-3 font-medium">{isDragActive ? "Drop it here!" : "Drag & drop your resume here"}</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      or <span className="font-medium text-violet-600 dark:text-violet-400">browse files</span>
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            {errors.file && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.file}</p>}
          </CardContent>
        </Card>

        {/* ---------------- Job details ---------------- */}
        <Card>
          <CardHeader>
            <CardTitle>2. Job details</CardTitle>
            <CardDescription>Paste the full job description for the most accurate match.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-5">
            <div className="grid gap-2">
              <Label htmlFor="role">Job role (optional)</Label>
              <NativeSelect id="role" value={jobRole} onChange={(e) => setJobRole(e.target.value)} disabled={loading}>
                <option value="">Select a role…</option>
                {roles.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </NativeSelect>
            </div>
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="jd">Job description</Label>
                <span className="text-xs text-muted-foreground">{jobDescription.length.toLocaleString()} characters</span>
              </div>
              <Textarea
                id="jd"
                rows={10}
                value={jobDescription}
                onChange={(e) => {
                  setJobDescription(e.target.value);
                  if (errors.jd) setErrors((x) => ({ ...x, jd: undefined }));
                }}
                placeholder="e.g. We are looking for a Frontend Developer with 1+ years of experience in React, TypeScript, REST APIs…"
                className={cn("resize-y", errors.jd && "border-red-400")}
                disabled={loading}
                aria-invalid={!!errors.jd}
              />
              {errors.jd && <p className="text-sm text-red-600 dark:text-red-400">{errors.jd}</p>}
            </div>
          </CardContent>
        </Card>

        <Button type="submit" variant="gradient" size="lg" disabled={loading} className="h-14 text-base">
          {loading ? (
            <>
              <LoaderCircle className="animate-spin" />
              <AnimatePresence mode="wait">
                <motion.span key={step} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}>
                  {LOADING_STEPS[step]}
                </motion.span>
              </AnimatePresence>
            </>
          ) : (
            <>
              <Sparkles /> Analyze
            </>
          )}
        </Button>
      </form>
    </div>
  );
}
