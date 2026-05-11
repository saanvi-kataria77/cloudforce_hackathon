"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  // trying to create a thinking agent animation, will add some more after deploying to Azure 
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (loading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < 3 ? prev + 1 : prev));
      }, 5000); // changes message every 5 seconds
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const loadingMessages = [
    "Extracting YouTube Transcript...",
    "Agent 1: Synthesizing Academic Summaries...",
    "Agent 2: Conducting Reflective Audit...",
    "Finalizing Dashboard & Formatting UI..."
  ];

  const handleAnalyze = async () => {
    if (!url) return;
    setLoading(true); setError(""); setData(null); setAnswer(""); setQuestion("");

    try {
      const response = await fetch(`https://cloudforce-hackathon-saanvi-kataria77.onrender.com/analyze?url=${encodeURIComponent(url)}`, { method: "POST" });
      if (!response.ok) {
        const errorData = await response.json(); 
        throw new Error(errorData.detail || "Failed to analyze video.");
      }
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInterrogate = async () => {
    if (!question || !data?.video_id) return;
    setAsking(true); setAnswer("");
    try {
      const response = await fetch(`https://cloudforce-hackathon-saanvi-kataria77.onrender.com/interrogate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: data.video_id, question: question })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get an answer.");
      }
      const result = await response.json();
      setAnswer(result.answer);
    } catch (err: any) {
      setAnswer(`Error: ${err.message}`);
    } finally {
      setAsking(false);
    }
  };

  return (
    // light gradient background 
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 p-8 flex flex-col items-center font-sans selection:bg-blue-200">
      
      <div className="w-full max-w-2xl text-center space-y-6 mt-16 transition-all duration-500 ease-in-out">
        <h1 className="text-5xl font-extrabold text-slate-900 tracking-tight">
          Frontier Intern <span className="text-blue-600 bg-blue-50 px-2 py-1 rounded-lg">AI</span>
        </h1>
        <p className="text-lg text-slate-500 font-light">Paste a YouTube lecture URL to generate summaries, notes, and equity audits.</p>
        
        <div className="flex space-x-2 shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg bg-white p-1">
          <Input 
            placeholder="https://www.youtube.com/watch?v=..." 
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 border-none focus-visible:ring-0 text-lg py-6 shadow-none"
          />
          <Button onClick={handleAnalyze} disabled={loading} size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-6 rounded-md transition-all">
            {loading ? "Processing..." : "Generate"}
          </Button>
        </div>
        
        {/* error message with a gentler animation */}
        {error && (
          <div className="animate-in fade-in slide-in-from-top-2 duration-300">
            <p className="text-red-500 font-medium bg-red-50 border border-red-100 py-2 rounded-md">{error}</p>
          </div>
        )}
      </div>

      {loading && (
        <div className="w-full max-w-4xl mt-20 space-y-6 animate-in fade-in duration-500">
          <div className="flex items-center justify-center space-x-3">
            {/* spinning loading ring */}
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-center font-medium text-blue-600 transition-all duration-300">
              {loadingMessages[loadingStep]}
            </p>
          </div>
          <Skeleton className="h-[200px] w-full rounded-2xl bg-white shadow-sm border border-slate-100" />
          <div className="grid grid-cols-2 gap-6">
            <Skeleton className="h-[250px] w-full rounded-2xl bg-white shadow-sm border border-slate-100" />
            <Skeleton className="h-[250px] w-full rounded-2xl bg-white shadow-sm border border-slate-100" />
          </div>
        </div>
      )}

      {data && (
        <div className="w-full max-w-5xl mt-16 space-y-8 pb-20 animate-in slide-in-from-bottom-8 fade-in duration-700">
            
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* agent 1 card */}
            <Card className="shadow-md hover:shadow-lg transition-shadow duration-300 border-t-4 border-t-blue-500 bg-white/80 backdrop-blur-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-xl text-slate-800 font-bold flex items-center gap-2">
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full uppercase tracking-wider">Agent 1</span>
                  Academic Summaries
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 space-y-4 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200">
                <p className="text-slate-700 whitespace-pre-wrap leading-relaxed prose prose-slate">
                  {data.summaries}
                </p>
              </CardContent>
            </Card>
    
            {/* agent 2 card with an indigo border */}
            <Card className="shadow-md hover:shadow-lg transition-shadow duration-300 border-t-4 border-t-indigo-500 bg-white/80 backdrop-blur-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-xl text-slate-800 font-bold flex items-center gap-2">
                  <span className="bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full uppercase tracking-wider">Agent 2</span>
                  STS Policy Audit
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 space-y-4 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200">
                <p className="text-slate-700 whitespace-pre-wrap leading-relaxed prose prose-slate">
                  {data.audit}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* agent 3 designed to be a little more interactive, add more later */}
          <Card className="shadow-xl border-slate-200 bg-white overflow-hidden">
            <CardHeader className="bg-slate-900 pb-6 pt-6">
              <CardTitle className="text-xl text-white font-bold flex items-center gap-2">
                <span className="bg-slate-700 text-slate-200 text-xs px-2 py-1 rounded-full uppercase tracking-wider">Agent 3</span>
                Interrogate the Video
              </CardTitle>
              <p className="text-slate-400 font-light mt-1">Ask a specific question to fact-check claims or find exact quotes.</p>
            </CardHeader>
            <CardContent className="pt-6 bg-slate-50">
              <div className="flex space-x-3 shadow-sm rounded-lg bg-white p-1 border border-slate-200">
                <Input 
                  placeholder="e.g., 'What did the professor say about data bias?'" 
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="flex-1 border-none focus-visible:ring-0 text-md shadow-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleInterrogate()}
                />
                <Button onClick={handleInterrogate} disabled={asking} className="bg-slate-900 hover:bg-slate-800 text-white px-6">
                  {asking ? "Searching..." : "Ask Agent"}
                </Button>
              </div>
              
              {answer && (
                <div className="mt-6 bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-in fade-in slide-in-from-top-2">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold shrink-0">
                      AI
                    </div>
                    <p className="text-slate-800 whitespace-pre-wrap leading-relaxed font-medium">
                      {answer}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

        </div>
      )}
    </main>
  );
}