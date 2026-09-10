import { useState, useEffect, Component, type ReactNode } from "react";
import { ArrowRight, Clock, Menu, X, ShieldCheck, GraduationCap, Globe, LogIn, ExternalLink } from "lucide-react";
import { Shader, Swirl, ChromaFlow, FlutedGlass, FilmGrain } from "shaders/react";

// Error boundary to protect shader rendering on unsupported hardware
class ShaderErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.warn("Shader canvas initialization fallback:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full bg-gradient-to-br from-[#EFEFEF] via-[#F5EFEA] to-[#EAEAEA] opacity-80" />
      );
    }
    return this.props.children;
  }
}

// Reusable text roll component for buttons
function TextRoll({ text }: { text: string }) {
  return (
    <div className="overflow-hidden h-[20px] inline-flex flex-col justify-start">
      <div className="flex flex-col transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-translate-y-1/2">
        <span className="h-[20px] flex items-center leading-none select-none">{text}</span>
        <span className="h-[20px] flex items-center leading-none select-none">{text}</span>
      </div>
    </div>
  );
}

// Partner badge starburst/compass SVG
function StarburstBadgeIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      className="w-5 h-5 sm:w-6 sm:h-6 fill-current text-[#E8704E] shrink-0"
    >
      <path d="m19.6 66.5 19.7-11 .3-1-.3-.5h-1l-3.3-.2-11.2-.3L14 53l-9.5-.5-2.4-.5L0 49l.2-1.5 2-1.3 2.9.2 6.3.5 9.5.6 6.9.4L38 49.1h1.6l.2-.7-.5-.4-.4-.4L29 41l-10.6-7-5.6-4.1-3-2-1.5-2-.6-4.2 2.7-3 3.7.3.9.2 3.7 2.9 8 6.1L37 36l1.5 1.2.6-.4.1-.3-.7-1.1L33 25l-6-10.4-2.7-4.3-.7-2.6c-.3-1-.4-2-.4-3l3-4.2L28 0l4.2.6L33.8 2l2.6 6 4.1 9.3L47 29.9l2 3.8 1 3.4.3 1h.7v-.5l.5-7.2 1-8.7 1-11.2.3-3.2 1.6-3.8 3-2L61 2.6l2 2.9-.3 1.8-1.1 7.7L59 27.1l-1.5 8.2h.9l1-1.1 4.1-5.4 6.9-8.6 3-3.5L77 13l2.3-1.8h4.3l3.1 4.7-1.4 4.9-4.4 5.6-3.7 4.7-5.3 7.1-3.2 5.7.3.4h.7l12-2.6 6.4-1.1 7.6-1.3 3.5 1.6.4 1.6-1.4 3.4-8.2 2-9.6 2-14.3 3.3-.2.1.2.3 6.4.6 2.8.2h6.8l12.6 1 3.3 2 1.9 2.7-.3 2-5.1 2.6-6.8-1.6-16-3.8-5.4-1.3h-.8v.4l4.6 4.5 8.3 7.5L89 80.1l.5 2.4-1.3 2-1.4-.2-9.2-7-3.6-3-8-6.8h-.5v.7l1.8 2.7 9.8 14.7.5 4.5-.7 1.4-2.6 1-2.7-.6-5.8-8-6-9-4.7-8.2-.5.4-2.9 30.2-1.3 1.5-3 1.2-2.5-2-1.4-3 1.4-6.2 1.6-8 1.3-6.4 1.2-7.9.7-2.6v-.2H49L43 72l-9 12.3-7.2 7.6-1.7.7-3-1.5.3-2.8L24 86l10-12.8 6-7.9 4-4.6-.1-.5h-.3L17.2 77.4l-4.7.6-2-2 .2-3 1-1 8-5.5Z" />
    </svg>
  );
}

// 12 Indian languages config
const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी (Hindi)" },
  { code: "or", label: "ଓଡ଼ିଆ (Odia)" },
  { code: "mr", label: "मराठी (Marathi)" },
  { code: "bn", label: "বাংলা (Bengali)" },
  { code: "ta", label: "தமிழ் (Tamil)" },
  { code: "te", label: "తెలుగు (Telugu)" },
  { code: "kn", label: "ಕನ್ನಡ (Kannada)" },
  { code: "gu", label: "ગુજરાતી (Gujarati)" },
  { code: "pa", label: "ਪੰਜਾਬੀ (Punjabi)" },
  { code: "ml", label: "മലയാളം (Malayalam)" },
  { code: "ur", label: "اردو (Urdu)" },
];

export default function App() {
  const [londonTime, setLondonTime] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState("en");

  // Load language preference
  useEffect(() => {
    const saved = localStorage.getItem("field_atlas_lang") || "en";
    setCurrentLang(saved);
  }, []);

  const handleLangChange = (langCode: string) => {
    setCurrentLang(langCode);
    localStorage.setItem("field_atlas_lang", langCode);
    // If FieldAtlasI18N engine is loaded in page context, trigger apply
    if (typeof (window as unknown as { FieldAtlasI18N?: { setLanguage: (c: string) => void } }).FieldAtlasI18N?.setLanguage === "function") {
      (window as unknown as { FieldAtlasI18N: { setLanguage: (c: string) => void } }).FieldAtlasI18N.setLanguage(langCode);
    }
  };

  // Live London Clock (HH:MM)
  useEffect(() => {
    const updateTime = () => {
      const formatter = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/London",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      });
      setLondonTime(formatter.format(new Date()));
    };

    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#EFEFEF] text-gray-900 selection:bg-[#F26522] selection:text-white font-sans antialiased">
      {/* ========================================================================= */}
      {/* SECTION 1: HERO (Full viewport height) */}
      {/* ========================================================================= */}
      <section className="relative h-screen min-h-[640px] flex flex-col justify-between bg-[#EFEFEF] overflow-hidden">
        {/* Animated Shader Overlay */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          <ShaderErrorBoundary>
            <Shader className="w-full h-full">
              <Swirl colorA="#ffffff" colorB="#f0f0f0" detail={1.7} />
              <ChromaFlow
                baseColor="#ffffff"
                downColor="#ff5f03"
                leftColor="#ff5f03"
                rightColor="#ff5f03"
                upColor="#ff5f03"
                momentum={13}
                radius={3.5}
              />
              <FlutedGlass
                aberration={0.61}
                angle={31}
                frequency={8}
                highlight={0.12}
                highlightSoftness={0}
                lightAngle={-90}
                refraction={4}
                shape="rounded"
                softness={1}
                speed={0.15}
              />
              <FilmGrain strength={0.05} />
            </Shader>
          </ShaderErrorBoundary>
        </div>

        {/* Navigation (z-20, relative) */}
        <header className="relative z-20 max-w-[1440px] mx-auto w-full p-2 sm:p-3">
          <nav className="bg-white rounded-full p-[5px] flex items-center justify-between shadow-[0_1px_6px_rgba(0,0,0,0.04)]">
            {/* LEFT: Logo & Links */}
            <div className="flex items-center">
              <a
                href="/"
                className="w-9 h-9 sm:w-10 sm:h-10 bg-gray-900 rounded-full flex items-center justify-center shrink-0 hover:opacity-90 transition-opacity"
                aria-label="SkillPulse Axion Studio Home"
              >
                <span className="text-[10px] sm:text-[11px] font-bold tracking-tight text-white select-none">
                  AX
                </span>
              </a>

              <div className="hidden md:flex items-center gap-6 ml-6">
                <a
                  href="#projects"
                  className="text-[14px] text-gray-900 hover:text-gray-500 transition-colors duration-300 font-medium"
                >
                  Projects
                </a>
                <a
                  href="#studio"
                  className="text-[14px] text-gray-900 hover:text-gray-500 transition-colors duration-300 font-medium"
                >
                  Studio
                </a>
                <a
                  href="#demo"
                  className="text-[14px] text-gray-900 hover:text-gray-500 transition-colors duration-300 font-medium"
                >
                  Demo
                </a>
                <a
                  href="trainer"
                  className="text-[14px] text-gray-900 hover:text-[#F26522] transition-colors duration-300 font-medium flex items-center gap-1.5"
                >
                  <ShieldCheck size={14} className="text-[#F26522]" />
                  Trainer
                </a>
                <a
                  href="trainee"
                  className="text-[14px] text-gray-900 hover:text-[#0E8176] transition-colors duration-300 font-medium flex items-center gap-1.5"
                >
                  <GraduationCap size={14} className="text-[#0E8176]" />
                  Trainee
                </a>
              </div>
            </div>

            {/* RIGHT (Desktop) */}
            <div className="hidden md:flex items-center gap-4 lg:gap-6 pr-1">
              {/* Language Selector */}
              <div className="flex items-center gap-1.5 bg-gray-50 hover:bg-gray-100 transition-colors px-2.5 py-1 rounded-full border border-gray-200 text-[12px]">
                <Globe size={13} className="text-gray-500 shrink-0" />
                <select
                  value={currentLang}
                  onChange={(e) => handleLangChange(e.target.value)}
                  className="bg-transparent text-gray-800 font-medium focus:outline-none cursor-pointer pr-1"
                  aria-label="Select Language"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code} className="text-gray-900 bg-white">
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>

              <span className="text-[13px] text-gray-600 hidden xl:block select-none">
                Taking on projects for Q1 2026
              </span>

              <div className="flex items-center gap-1.5 text-[13px] text-gray-600 select-none">
                <Clock size={14} className="text-gray-600 shrink-0" />
                <span>{londonTime || "12:00"} in London</span>
              </div>

              <a
                href="login.html"
                className="bg-gray-900 hover:bg-gray-800 text-white text-[13px] font-medium rounded-full pl-5 pr-2 py-2 group flex items-center gap-3 transition-colors duration-300"
              >
                <TextRoll text="Book a strategy call" />
                <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center text-gray-900 shrink-0">
                  <ArrowRight
                    size={14}
                    className="transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45"
                  />
                </div>
              </a>
            </div>

            {/* MOBILE: Menu Toggle */}
            <div className="md:hidden">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="w-9 h-9 bg-gray-900 text-white rounded-full flex items-center justify-center"
                aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
              >
                {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
              </button>
            </div>
          </nav>
        </header>

        {/* Mobile Menu Overlay */}
        <div
          className={`fixed inset-0 z-50 bg-black/60 transition-opacity duration-500 flex flex-col justify-end md:hidden ${
            mobileMenuOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
          }`}
          onClick={() => setMobileMenuOpen(false)}
        >
          <div
            className={`bg-white rounded-2xl mx-3 mb-3 p-6 sm:p-8 flex flex-col justify-between shadow-2xl transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${
              mobileMenuOpen ? "translate-y-0" : "translate-y-full"
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top row: Time badge & close */}
            <div className="flex items-center justify-between pb-5 border-b border-gray-100">
              <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-600 bg-gray-100 px-3.5 py-1.5 rounded-full font-medium">
                <Clock size={14} />
                <span>{londonTime || "12:00"} in London</span>
              </div>
              <button
                type="button"
                onClick={() => setMobileMenuOpen(false)}
                className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-900 hover:bg-gray-200 transition-colors"
                aria-label="Close menu"
              >
                <X size={18} />
              </button>
            </div>

            {/* Language selector for mobile */}
            <div className="pt-4 flex items-center gap-2">
              <Globe size={16} className="text-gray-600" />
              <select
                value={currentLang}
                onChange={(e) => handleLangChange(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 px-3 text-sm font-medium text-gray-900"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Nav links */}
            <nav className="flex flex-col gap-3 py-6">
              <a
                href="#projects"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[26px] font-medium text-gray-900 hover:text-[#F26522] transition-colors"
              >
                Projects
              </a>
              <a
                href="#studio"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[26px] font-medium text-gray-900 hover:text-[#F26522] transition-colors"
              >
                Studio
              </a>
              <a
                href="#demo"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[26px] font-medium text-gray-900 hover:text-[#F26522] transition-colors"
              >
                Demo Accounts
              </a>
              <a
                href="trainer"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[22px] font-semibold text-gray-900 hover:text-[#F26522] flex items-center gap-2 transition-colors pt-2 border-t border-gray-100"
              >
                <ShieldCheck size={20} className="text-[#F26522]" />
                Trainer Portal
              </a>
              <a
                href="trainee"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[22px] font-semibold text-gray-900 hover:text-[#0E8176] flex items-center gap-2 transition-colors"
              >
                <GraduationCap size={20} className="text-[#0E8176]" />
                Trainee Portal (Pictorial Feedback)
              </a>
              <a
                href="login.html"
                onClick={() => setMobileMenuOpen(false)}
                className="text-[20px] font-medium text-gray-700 hover:text-gray-900 flex items-center gap-2 transition-colors"
              >
                <LogIn size={18} />
                Sign In
              </a>
            </nav>

            {/* Start a project button */}
            <div className="pt-4 border-t border-gray-100">
              <a
                href="register.html"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full bg-[#F26522] hover:bg-[#e05a1a] text-white text-[15px] font-medium rounded-full pl-6 pr-2 py-2.5 group flex items-center justify-between transition-colors duration-500"
              >
                <TextRoll text="Start a project" />
                <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-[#F26522] shrink-0">
                  <ArrowRight
                    size={16}
                    className="transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45"
                  />
                </div>
              </a>
            </div>
          </div>
        </div>

        {/* Spacer to push content to bottom */}
        <div className="flex-1" />

        {/* Hero Content (z-20) */}
        <div className="relative z-20 max-w-[1440px] mx-auto w-full px-5 sm:px-8 lg:px-12 pb-14 sm:pb-16 lg:pb-20">
          <p className="text-[13px] sm:text-[14px] text-gray-900 tracking-wide mb-5 sm:mb-8 font-normal flex items-center gap-2">
            <span>Axion Studio</span>
            <span className="text-gray-400">/</span>
            <span className="text-gray-600 font-medium">SkillPulse Intelligence Platform</span>
          </p>

          <h1 className="text-[clamp(1.75rem,7vw,4.2rem)] sm:text-[clamp(2.5rem,5vw,4.2rem)] font-medium leading-[1.08] tracking-[-0.03em] text-gray-900">
            We craft digital experiences
            <br className="hidden sm:block" />
            <span className="sm:hidden"> </span>
            for brands ready to dominate
            <br className="hidden sm:block" />
            <span className="sm:hidden"> </span>
            their category online.
          </h1>

          <div className="mt-8 sm:mt-12 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-5 flex-wrap">
            {/* Orange Button */}
            <a
              href="trainer"
              className="bg-[#F26522] hover:bg-[#e05a1a] text-white text-[13px] sm:text-[14px] font-medium rounded-full pl-5 sm:pl-6 pr-2 py-2 group flex items-center justify-between sm:justify-start gap-4 transition-colors duration-500 w-fit"
            >
              <TextRoll text="Start a project" />
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-white flex items-center justify-center text-[#F26522] shrink-0">
                <ArrowRight
                  size={14}
                  className="transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45"
                />
              </div>
            </a>

            {/* Partner Badge */}
            <div className="bg-white rounded-[4px] shadow-[0_2px_8px_rgba(0,0,0,0.08)] hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] transition-shadow duration-300 px-3 sm:px-3.5 py-2 sm:py-2.5 flex items-center gap-2.5 w-fit select-none">
              <StarburstBadgeIcon />
              <span className="text-[13px] sm:text-[14px] font-medium text-gray-900">
                Certified Partner
              </span>
              <span className="text-[10px] sm:text-[11px] bg-gray-900 text-white px-1.5 sm:px-2 py-0.5 rounded font-normal">
                Featured
              </span>
            </div>

            {/* Quick Access Portal Badges */}
            <div className="flex items-center gap-2.5">
              <a
                href="trainer"
                className="text-[12px] sm:text-[13px] bg-white/80 hover:bg-white backdrop-blur border border-gray-300 text-gray-800 font-medium px-3 py-2 rounded-full flex items-center gap-1.5 transition-all hover:shadow-sm"
              >
                <ShieldCheck size={14} className="text-[#F26522]" />
                Trainer Suite
              </a>
              <a
                href="trainee"
                className="text-[12px] sm:text-[13px] bg-white/80 hover:bg-white backdrop-blur border border-gray-300 text-gray-800 font-medium px-3 py-2 rounded-full flex items-center gap-1.5 transition-all hover:shadow-sm"
              >
                <GraduationCap size={14} className="text-[#0E8176]" />
                Trainee Suite
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 2: ABOUT (White background) */}
      {/* ========================================================================= */}
      <section
        id="studio"
        className="bg-white pt-16 sm:pt-20 lg:pt-32 pb-12 sm:pb-16 lg:pb-24 overflow-hidden"
      >
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8 lg:px-12">
          {/* Badge row */}
          <div className="flex items-center gap-3 mb-6 sm:mb-8">
            <span className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gray-900 text-white text-[11px] sm:text-[12px] font-semibold flex items-center justify-center select-none">
              1
            </span>
            <span className="text-[12px] sm:text-[13px] font-medium border border-gray-200 rounded-full px-3 sm:px-4 py-1 sm:py-1.5 text-gray-900 select-none">
              Introducing Axion
            </span>
          </div>

          {/* Heading h2 */}
          <h2 className="text-[clamp(1.5rem,4vw,3.2rem)] font-medium leading-[1.12] tracking-[-0.02em] text-gray-900 mb-12 sm:mb-16 lg:mb-28">
            Strategy-led creatives, delivering
            <br className="hidden sm:block" /> results in digital and beyond.
          </h2>

          {/* Content Area - Mobile/Tablet (<lg) */}
          <div className="block lg:hidden">
            <p className="text-[15px] sm:text-[17px] leading-[1.6] font-medium text-gray-900 max-w-xl">
              Through research, creative thinking and iteration we help growing brands realize their
              digital full potential.
            </p>

            <a
              href="trainer"
              className="bg-[#F26522] hover:bg-[#e05a1a] text-white text-[13px] sm:text-[14px] font-medium rounded-full pl-5 sm:pl-6 pr-2 py-2 group flex items-center gap-4 transition-colors duration-500 w-fit mt-6 mb-10"
            >
              <TextRoll text="About our studio" />
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-white flex items-center justify-center text-[#F26522] shrink-0">
                <ArrowRight
                  size={14}
                  className="transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45"
                />
              </div>
            </a>

            <div className="flex flex-col sm:flex-row gap-4 sm:gap-5">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090123_74be96d4-9c1b-40cf-932a-96f4f4babed3.png&w=1280&q=85"
                alt="Studio creative work preview"
                className="w-full sm:w-[45%] aspect-[438/346] rounded-xl sm:rounded-2xl object-cover"
                loading="lazy"
              />
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090133_c157d30b-a99a-4477-bec1-a446149ec3f2.png&w=1280&q=85"
                alt="Axion studio workspace and team"
                className="w-full sm:w-[55%] aspect-[900/600] rounded-xl sm:rounded-2xl object-cover"
                loading="lazy"
              />
            </div>
          </div>

          {/* Content Area - Desktop (lg+) */}
          <div className="hidden lg:grid grid-cols-[26%_1fr_48%] items-end gap-6 xl:gap-8">
            {/* Left Column: Small image (self-end) */}
            <div className="self-end">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090123_74be96d4-9c1b-40cf-932a-96f4f4babed3.png&w=1280&q=85"
                alt="Studio creative work preview"
                className="w-full aspect-[438/346] rounded-2xl object-cover shadow-sm"
                loading="lazy"
              />
            </div>

            {/* Center Column: Paragraph + Button (self-start, flex justify-end) */}
            <div className="self-start flex flex-col justify-end items-start h-full pb-2">
              <p className="text-[16px] xl:text-[18px] leading-[1.65] font-medium text-gray-900 whitespace-nowrap mb-8">
                Through research, creative thinking and
                <br />
                iteration we help growing brands realize
                <br />
                their digital full potential.
              </p>

              <a
                href="#projects"
                className="bg-[#F26522] hover:bg-[#e05a1a] text-white text-[13px] sm:text-[14px] font-medium rounded-full pl-5 sm:pl-6 pr-2 py-2 group flex items-center gap-4 transition-colors duration-500 w-fit"
              >
                <TextRoll text="About our studio" />
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-white flex items-center justify-center text-[#F26522] shrink-0">
                  <ArrowRight
                    size={14}
                    className="transition-transform duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45"
                  />
                </div>
              </a>
            </div>

            {/* Right Column: Large image (self-end) */}
            <div className="self-end">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090133_c157d30b-a99a-4477-bec1-a446149ec3f2.png&w=1280&q=85"
                alt="Axion studio workspace and team"
                className="w-full aspect-[3/2] rounded-2xl object-cover shadow-sm"
                loading="lazy"
              />
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 3: CASE STUDIES (Light gray background) */}
      {/* ========================================================================= */}
      <section
        id="projects"
        className="bg-[#F5F5F5] pt-16 sm:pt-20 lg:pt-28 pb-16 sm:pb-20 lg:pb-28"
      >
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8 lg:px-12">
          {/* Badge row */}
          <div className="flex items-center gap-3 mb-6 sm:mb-8">
            <span className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gray-900 text-white text-[11px] sm:text-[12px] font-semibold flex items-center justify-center select-none">
              2
            </span>
            <span className="text-[12px] sm:text-[13px] font-medium border border-gray-300 rounded-full px-3 sm:px-4 py-1 sm:py-1.5 text-gray-900 select-none">
              Featured client work
            </span>
          </div>

          {/* Heading h2 */}
          <h2 className="text-[clamp(1.75rem,7vw,4.2rem)] sm:text-[clamp(2.5rem,5vw,4.2rem)] font-medium leading-[1.08] tracking-[-0.03em] text-gray-900 mb-10 sm:mb-14 lg:mb-16">
            Our projects
          </h2>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 lg:gap-7">
            {/* Card 1: Narrativ */}
            <div className="flex flex-col">
              <div className="aspect-[329/246] rounded-2xl overflow-hidden bg-[#1a1d2e] relative group cursor-pointer shadow-sm">
                <video
                  src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260516_122702_390f5305-8719-41d5-ae80-d23ab3796c28.mp4"
                  autoPlay
                  muted
                  loop
                  playsInline
                  className="w-full h-full object-cover"
                />

                {/* Expanding hover button */}
                <div className="absolute bottom-4 left-4 h-9 w-9 group-hover:w-[148px] bg-white rounded-full flex items-center justify-between px-2.5 overflow-hidden transition-all duration-300 ease-in-out shadow-md">
                  <span className="text-[13px] font-medium text-gray-900 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100 pl-1">
                    Learn more
                  </span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-gray-900 shrink-0 transform -rotate-45 group-hover:rotate-0 transition-transform duration-300 ease-in-out"
                  >
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                </div>
              </div>

              <p className="text-[13px] sm:text-[14px] text-gray-600 mt-4 leading-relaxed">
                Winner of Site of the Month 2025 - an interactive 3D showcase driving record engagement
              </p>

              <h3 className="text-[14px] sm:text-[15px] font-semibold text-gray-900 mt-1">
                Narrativ
              </h3>
            </div>

            {/* Card 2: Luminar */}
            <div className="flex flex-col">
              <div className="aspect-square rounded-2xl overflow-hidden bg-[#6b6b6b] relative group cursor-pointer shadow-sm">
                <video
                  src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260516_123323_f909c2b8-ff6c-4edf-882b-8ebcdbe389b5.mp4"
                  autoPlay
                  muted
                  loop
                  playsInline
                  className="w-full h-full object-cover"
                />

                {/* Expanding hover button */}
                <div className="absolute bottom-4 left-4 h-9 w-9 group-hover:w-[168px] bg-gray-900 text-white rounded-full flex items-center justify-between px-2.5 overflow-hidden transition-all duration-300 ease-in-out shadow-md">
                  <span className="text-[13px] font-medium text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100 pl-1">
                    View case study
                  </span>
                  <ArrowRight
                    size={14}
                    className="text-white shrink-0 transform -rotate-45 group-hover:rotate-0 transition-transform duration-300 ease-in-out"
                  />
                </div>
              </div>

              <p className="text-[13px] sm:text-[14px] text-gray-600 mt-4 leading-relaxed">
                Transforming a dated platform into a conversion-focused brand experience
              </p>

              <h3 className="text-[14px] sm:text-[15px] font-semibold text-gray-900 mt-1">
                Luminar
              </h3>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 4: PLATFORM DEMO ACCESS & PORTAL LAUNCH */}
      {/* ========================================================================= */}
      <section id="demo" className="bg-[#1E2749] text-white py-16 sm:py-20 px-5 sm:px-8 lg:px-12">
        <div className="max-w-[1440px] mx-auto text-center">
          <span className="inline-flex items-center gap-2 bg-white/10 text-cyan-300 px-4 py-1.5 rounded-full text-[12px] font-semibold tracking-wider uppercase mb-4">
            <ShieldCheck size={14} />
            Live National Workspace
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold mb-4 text-white">
            Try the Live Platform Demo
          </h2>
          <p className="text-gray-300 max-w-2xl mx-auto mb-10 text-sm sm:text-base leading-relaxed">
            Instantly evaluate the SkillPulse outcomes tracking suites with pre-configured demo credentials. Both Trainer and Trainee roles are preloaded with real cohort data and ratings.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-4xl mx-auto mb-10">
            {/* Trainer Card */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-left hover:bg-white/10 transition-colors">
              <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-400 block mb-2">
                Trainer Portal
              </span>
              <p className="font-semibold text-white text-base mb-1">trainer@fieldatlas.in</p>
              <p className="text-xs text-gray-400 font-mono mb-4">ID: FA-TR-1001</p>
              <a
                href="trainer"
                className="inline-flex items-center gap-2 text-xs font-semibold text-white bg-[#F26522] hover:bg-[#e05a1a] px-3.5 py-2 rounded-full transition-colors"
              >
                Launch Trainer Suite <ArrowRight size={12} />
              </a>
            </div>

            {/* Trainee Card */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-left hover:bg-white/10 transition-colors">
              <span className="text-[11px] font-bold uppercase tracking-wider text-teal-400 block mb-2">
                Trainee Portal
              </span>
              <p className="font-semibold text-white text-base mb-1">trainee@fieldatlas.in</p>
              <p className="text-xs text-gray-400 font-mono mb-4">ID: FA-24-0182</p>
              <a
                href="trainee"
                className="inline-flex items-center gap-2 text-xs font-semibold text-white bg-[#0E8176] hover:bg-[#0b6a61] px-3.5 py-2 rounded-full transition-colors"
              >
                Launch Trainee Suite <ArrowRight size={12} />
              </a>
            </div>

            {/* Admin Card */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-left hover:bg-white/10 transition-colors">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400 block mb-2">
                Outcome Verifier
              </span>
              <p className="font-semibold text-white text-base mb-1">admin@fieldatlas.in</p>
              <p className="text-xs text-gray-400 font-mono mb-4">ID: FA-AD-0001</p>
              <a
                href="login.html"
                className="inline-flex items-center gap-2 text-xs font-semibold text-white bg-gray-700 hover:bg-gray-600 px-3.5 py-2 rounded-full transition-colors"
              >
                Sign In As Admin <ExternalLink size={12} />
              </a>
            </div>
          </div>

          <p className="text-xs text-gray-400">
            Universal Password: <code className="text-cyan-300 bg-white/10 px-2.5 py-1 rounded font-mono font-medium">Atlas@2026!</code>
          </p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* FOOTER */}
      {/* ========================================================================= */}
      <footer className="bg-white border-t border-gray-200 py-10 px-5 sm:px-8 text-center text-xs text-gray-500">
        <p className="mb-2">
          Consent-aware by design · No raw Aadhaar stored · Built for India's National Skill Ecosystem
        </p>
        <p className="text-gray-400">
          &copy; 2026 Axion Studio x SkillPulse Platform · #crafted by team Synkro
        </p>
      </footer>
    </div>
  );
}
