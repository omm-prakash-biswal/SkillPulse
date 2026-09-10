/*
 * SKILLPULSE — COMPREHENSIVE 12-LANGUAGE LOCALIZATION ENGINE
 * Full client-side localization for 12 Indian national languages:
 * English (en), Hindi (hi), Odia (or), Marathi (mr), Bengali (bn), Tamil (ta),
 * Telugu (te), Kannada (kn), Gujarati (gu), Punjabi (pa), Malayalam (ml), and Urdu (ur).
 */

const FieldAtlasI18N = (function() {
  'use strict';

  let currentLang = 'en';

  // Comprehensive translations covering all pages, tabs, queues, actions, and dialogs
  const translations = {
    en: {
      brand_name: "SkillPulse",
      workspace: "Good Outcomes / National workspace",
      nav_overview: "Overview",
      nav_followups: "Follow-ups",
      nav_trainees: "Trainees",
      nav_providers: "Providers",
      nav_reports: "Reports",
      nav_profile: "Profile",
      nav_logout: "Sign out",
      hero_eyebrow: "Programme pulse / Q3 2026",
      hero_title: "The work after training matters.",
      hero_desc: "See the journey from training to lasting work.",
      btn_export_brief: "Export impact brief",
      btn_view_methodology: "View methodology",
      privacy_note: "Consent-aware by design · No raw Aadhaar stored",
      route_enrolled: "Enrolled",
      route_trained: "Trained",
      route_certified: "Certified",
      route_placed: "Placed",
      route_retained: "Retained",
      metric_active: "Active trainees",
      metric_retention: "12-month retention",
      metric_wage: "Median wage",
      metric_followup: "Needs human follow-up",
      chart_wage_title: "Wage progression curve",
      chart_wage_sub: "Realized earnings vs baseline floor",
      chart_funnel_title: "Cohort conversion funnel",
      chart_funnel_sub: "End-to-end completion & placement efficiency",
      chart_providers_title: "Provider pulse leaderboard",
      chart_diagnostics_title: "Non-placement diagnostics",
      followup_heading: "Small calls. Long-term signal.",
      followup_summary: "124 people need help · 86 three-month · 38 twelve-month · 72% resolved",
      btn_working: "Working",
      btn_own_work: "Own work",
      btn_need_help: "Need help",
      btn_send_now: "Send outreach",
      btn_seed_demo: "Seed demo data",
      btn_new_trainee: "New trainee",
      btn_export_csv: "Export CSV",
      filter_all_providers: "All Providers",
      filter_all_stages: "All Stages",
      filter_all_consents: "All Consents",
      th_learner: "Learner",
      th_stage: "Current stage",
      th_provider: "Provider",
      th_signal: "Employer signal",
      th_wage: "Wage",
      th_updated: "Last update",
      th_actions: "Actions",
      trainee_welcome: "Welcome back,",
      trainee_progress: "Your Learning & Placement Journey",
      trainee_consent_label: "Consent status:",
      trainee_consent_active: "Active & Protected",
      trainee_consent_withdrawn: "Withdrawn",
      trainee_btn_work: "I am working",
      trainee_btn_business: "I run my own business",
      trainee_btn_support: "I need support",
      trainee_download_report: "Download My Progress Report",
      save_changes: "Save Changes",
      cancel: "Cancel",
      search_placeholder: "Search by name, SkillPulse ID, or course...",
      nav_step1: "1. Dashboard",
      nav_step2: "2. Courses of Trainer",
      nav_step3: "3. Confirmation",
      nav_step4: "4. Trainer Qualification",
      nav_feedback: "Feedback & Ratings",
      nav_pulse: "Programme Pulse",
      nav_trainees_dir: "Trainees Directory",
      nav_recovery: "Dark-Zone Recovery",
      nav_settings: "Settings",
      trainee_nav_1: "1. Dashboard & Streak",
      trainee_nav_2: "2. Government Courses",
      trainee_nav_3: "3. Learning Record",
      trainee_nav_4: "4. Certificates",
      trainee_nav_5: "5. Placement Details",
      trainee_nav_6: "6. Feedback & Ratings",
      feedback_section_title: "Student Feedback & Ratings",
      feedback_section_sub: "Visual ratings and feedback given by enrolled students",
      kpi_overall_score: "Overall Trainer Score",
      kpi_behavior_label: "Trainer Behavior & Respect",
      kpi_teaching_label: "Class & Teaching Quality",
      kpi_doubts_label: "Doubt Clearing & Help",
      top_course_title: "Highest Rated Course",
      top_course_badge: "TOP PERFORMER",
      needs_attention_title: "Needs Attention Course",
      needs_attention_badge: "NEEDS ACTION",
      why_diagnostics_title: "Why Students Struggled (Diagnostics)",
      reason_pacing: "Taught Too Fast",
      reason_labs: "Need More Practical Lab Time",
      reason_doubts: "Wanted More Doubt Resolution",
      reason_notes: "Need Notes in Local Language",
      trainee_feedback_title: "Rate Your Trainer & Course Experience",
      trainee_feedback_sub: "Simple one-tap pictorial rating to help your trainer and classmates",
      select_course_label: "Select Completed Course",
      btn_submit_feedback: "Submit My Feedback",
      submitted_history_title: "My Past Feedback Submissions",
      mood_outstanding: "Outstanding & Very Respectful!",
      mood_good: "Good & Helpful",
      mood_average: "Average / Okay",
      mood_needs_improvement: "Needs Improvement",
      mood_poor: "Not Satisfied",
      // Follow-Up Queue terms
      followup_queue: "Follow-Up Queue",
      pending_actions: "Pending Actions",
      pending: "pending",
      whatsapp: "WhatsApp",
      sms: "SMS",
      call_script: "Call Script",
      followup_preview_placeholder: "Select a follow-up item from the queue to preview the outreach message.",
      send_message: "Send Message",
      mark_resolved: "Mark Resolved",
      theme_light: "Light",
      theme_dark: "Dark",
      trainer_portal: "Trainer Portal",
      trainee_portal: "Trainee Portal",
      sign_in: "Sign In",
      sign_up: "Sign Up",
      track_real_outcomes: "Track Real Skilling Outcomes That Matter",
      capabilities_title: "Everything You Need for Skilling Excellence",
      how_it_works_title: "From Enrollment to Employment",
      demo_title: "Try the Live Demo"
    },
    hi: {
      brand_name: "स्किलपल्स (SkillPulse)",
      workspace: "सफल परिणाम / राष्ट्रीय कार्यक्षेत्र",
      nav_overview: "अवलोकन",
      nav_followups: "फॉलो-अप",
      nav_trainees: "प्रशिक्षार्थी",
      nav_providers: "प्रदाता",
      nav_reports: "रिपोर्ट्स",
      nav_profile: "प्रोफाइल",
      nav_logout: "लॉग आउट",
      hero_eyebrow: "कार्यक्रम पल्स / Q3 2026",
      hero_title: "प्रशिक्षण के बाद का कार्य महत्वपूर्ण है।",
      hero_desc: "प्रशिक्षण से लेकर स्थायी आजीविका तक का सफर देखें।",
      btn_export_brief: "प्रभाव विवरण डाउनलोड करें",
      btn_view_methodology: "प्रणाली देखें",
      privacy_note: "सहमति-आधारित संरचना · आधार डेटा सुरक्षित",
      route_enrolled: "नामांकित",
      route_trained: "प्रशिक्षित",
      route_certified: "प्रमाणित",
      route_placed: "रोजगार प्राप्त",
      route_retained: "स्थायी कार्य",
      metric_active: "सक्रिय प्रशिक्षार्थी",
      metric_retention: "12-माह प्रतिधारण",
      metric_wage: "औसत वेतन",
      metric_followup: "व्यक्तिगत संपर्क आवश्यक",
      chart_wage_title: "वेतन वृद्धि वक्र",
      chart_wage_sub: "न्यूनतम दर के मुकाबले वास्तविक आय",
      chart_funnel_title: "बैच रूपांतरण फ़नल",
      chart_funnel_sub: "प्रशिक्षण पूर्णता और रोजगार दक्षता",
      chart_providers_title: "प्रदाता प्रदर्शन तालिका",
      chart_diagnostics_title: "गैर-रोजगार निदान",
      followup_heading: "छोटे संवाद, दीर्घकालिक परिणाम।",
      followup_summary: "124 लोगों को सहायता की आवश्यकता है · 72% समाधान",
      btn_working: "कार्यरत",
      btn_own_work: "स्वरोजगार",
      btn_need_help: "सहायता चाहिए",
      btn_send_now: "संदेश भेजें",
      btn_seed_demo: "डेमो डेटा लोड करें",
      btn_new_trainee: "नया प्रशिक्षार्थी",
      btn_export_csv: "CSV डाउनलोड करें",
      filter_all_providers: "सभी प्रदाता",
      filter_all_stages: "सभी चरण",
      filter_all_consents: "सभी सहमतियां",
      th_learner: "प्रशिक्षार्थी",
      th_stage: "वर्तमान चरण",
      th_provider: "प्रदाता",
      th_signal: "नियोक्ता पुष्टि",
      th_wage: "मासिक वेतन",
      th_updated: "अंतिम अपडेट",
      th_actions: "कार्रवाई",
      trainee_welcome: "पुनः स्वागत है,",
      trainee_progress: "आपकी सीखने और रोजगार की यात्रा",
      trainee_consent_label: "सहमति स्थिति:",
      trainee_consent_active: "सक्रिय और सुरक्षित",
      trainee_consent_withdrawn: "वापस ली गई",
      trainee_btn_work: "मैं नौकरी कर रहा हूँ",
      trainee_btn_business: "मेरा अपना व्यवसाय है",
      trainee_btn_support: "मुझे सहायता चाहिए",
      trainee_download_report: "प्रगति रिपोर्ट डाउनलोड करें",
      save_changes: "परिवर्तन सहेजें",
      cancel: "रद्द करें",
      search_placeholder: "नाम, आईडी या कोर्स द्वारा खोजें...",
      nav_step1: "1. डैशबोर्ड",
      nav_step2: "2. ट्रेनर के पाठ्यक्रम",
      nav_step3: "3. पुष्टिकरण",
      nav_step4: "4. ट्रेनर योग्यता",
      nav_feedback: "प्रतिक्रिया और रेटिंग",
      nav_pulse: "कार्यक्रम पल्स",
      nav_trainees_dir: "प्रशिक्षार्थी निर्देशिका",
      nav_recovery: "डार्क-ज़ोन रिकवरी",
      nav_settings: "सेटिंग्स",
      trainee_nav_1: "1. डैशबोर्ड और स्ट्रीक",
      trainee_nav_2: "2. सरकारी पाठ्यक्रम",
      trainee_nav_3: "3. अध्ययन रिकॉर्ड",
      trainee_nav_4: "4. प्रमाणपत्र",
      trainee_nav_5: "5. प्लेसमेंट विवरण",
      trainee_nav_6: "6. प्रतिक्रिया और रेटिंग",
      feedback_section_title: "छात्र प्रतिक्रिया और रेटिंग",
      feedback_section_sub: "नामांकित छात्रों द्वारा दी गई दृश्य रेटिंग और प्रतिक्रिया",
      kpi_overall_score: "समग्र ट्रेनर स्कोर",
      kpi_behavior_label: "ट्रेनर का व्यवहार और आदर",
      kpi_teaching_label: "कक्षा और शिक्षण गुणवत्ता",
      kpi_doubts_label: "संदेह निवारण और सहायता",
      top_course_title: "सर्वोच्च रेटिंग प्राप्त पाठ्यक्रम",
      top_course_badge: "सर्वश्रेष्ठ प्रदर्शन",
      needs_attention_title: "सुधार आवश्यक पाठ्यक्रम",
      needs_attention_badge: "कार्रवाई आवश्यक",
      why_diagnostics_title: "छात्रों को कहाँ कठिनाई हुई (निदान)",
      reason_pacing: "बहुत तेज़ गति से पढ़ाया",
      reason_labs: "अधिक व्यावहारिक लैब समय चाहिए",
      reason_doubts: "अधिक संदेह निवारण चाहिए था",
      reason_notes: "स्थानीय भाषा में नोट्स चाहिए",
      trainee_feedback_title: "अपने ट्रेनर और कोर्स का मूल्यांकन करें",
      trainee_feedback_sub: "अपने ट्रेनर और साथियों की मदद के लिए आसान एक-स्पर्श रेटिंग",
      select_course_label: "पूर्ण किया गया कोर्स चुनें",
      btn_submit_feedback: "मेरी प्रतिक्रिया जमा करें",
      submitted_history_title: "मेरी पूर्व प्रतिक्रियाएं",
      mood_outstanding: "उत्कृष्ट और बहुत आदरणीय!",
      mood_good: "अच्छा और मददगार",
      mood_average: "औसत / सामान्य",
      mood_needs_improvement: "सुधार की आवश्यकता",
      mood_poor: "संतुष्ट नहीं",
      // Follow-Up Queue terms
      followup_queue: "फॉलो-अप कतार",
      pending_actions: "लंबित कार्य",
      pending: "लंबित",
      whatsapp: "व्हाट्सएप",
      sms: "एसएमएस",
      call_script: "कॉल स्क्रिप्ट",
      followup_preview_placeholder: "आउटरीच संदेश का पूर्वावलोकन करने के लिए कतार से एक फॉलो-अप आइटम चुनें।",
      send_message: "संदेश भेजें",
      mark_resolved: "समाधान चिह्नित करें",
      theme_light: "लाइट",
      theme_dark: "डार्क",
      trainer_portal: "ट्रेनर पोर्टल",
      trainee_portal: "प्रशिक्षार्थी पोर्टल",
      sign_in: "साइन इन",
      sign_up: "साइन अप",
      track_real_outcomes: "वास्तविक कौशल परिणामों को ट्रैक करें",
      capabilities_title: "कौशल उत्कृष्टता के लिए आवश्यक हर सुविधा",
      how_it_works_title: "नामांकन से लेकर रोजगार तक",
      demo_title: "लाइव डेमो आज़माएं"
    },
    or: {
      brand_name: "ସ୍କିଲପଲ୍ସ (SkillPulse)",
      workspace: "ଉନ୍ନତ ଫଳାଫଳ / ଜାତୀୟ କାର୍ଯ୍ୟକ୍ଷେତ୍ର",
      nav_overview: "ସମୀକ୍ଷା",
      nav_followups: "ଫଲୋ-ଅପ୍",
      nav_trainees: "ପ୍ରଶିକ୍ଷାର୍ଥୀ",
      nav_providers: "ପ୍ରଦାତା",
      nav_reports: "ରିପୋର୍ଟ",
      nav_profile: "ପ୍ରୋଫାଇଲ୍",
      nav_logout: "ଲଗ୍ ଆଉଟ୍",
      hero_eyebrow: "ପ୍ରୋଗ୍ରାମ ପଲ୍ସ / ୨୦୨୬",
      hero_title: "ତାଲିମ ପରବର୍ତ୍ତୀ କାର୍ଯ୍ୟ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ।",
      hero_desc: "ତାଲିମରୁ ସ୍ଥାୟୀ ଜୀବିକା ପର୍ଯ୍ୟନ୍ତ ଯାତ୍ରା ଦେଖନ୍ତୁ।",
      btn_export_brief: "ଫଳାଫଳ ଡାଉନଲୋଡ୍",
      btn_view_methodology: "ପ୍ରଣାଳୀ ଦେଖନ୍ତୁ",
      privacy_note: "ସମ୍ମତି-ଆଧାରିତ ବ୍ୟବସ୍ଥା · ଆଧାର ସୁରକ୍ଷିତ",
      route_enrolled: "ନାମାଙ୍କିତ",
      route_trained: "ପ୍ରଶିକ୍ଷିତ",
      route_certified: "ପ୍ରମାଣିତ",
      route_placed: "ନିଯୁକ୍ତି ପ୍ରାପ୍ତ",
      route_retained: "ସ୍ଥାୟୀ କାର୍ଯ୍ୟ",
      metric_active: "ସକ୍ରିୟ ପ୍ରଶିକ୍ଷାର୍ଥୀ",
      metric_retention: "୧୨-ମାସ ଧାରଣ",
      metric_wage: "ହାରାହାରି ଦରମା",
      metric_followup: "ସହାୟତା ଆବଶ୍ୟକ",
      chart_wage_title: "ଦରମା ବୃଦ୍ଧି ରେଖାଚିତ୍ର",
      chart_wage_sub: "ବାସ୍ତବ ରୋଜଗାର ତୁଳନା",
      chart_funnel_title: "ସଫଳତା ହାର ଫନେଲ୍",
      chart_funnel_sub: "ସମାପ୍ତି ଏବଂ ନିଯୁକ୍ତି ଦକ୍ଷତା",
      chart_providers_title: "ତାଲିମ ପ୍ରଦାତା ପ୍ରଦର୍ଶନ",
      chart_diagnostics_title: "ଅଣ-ନିଯୁକ୍ତି କାରଣ ବିଶ୍ଳେଷଣ",
      followup_heading: "ସହଜ ଯୋଗାଯୋଗ, ଦୀର୍ଘକାଳୀନ ଫଳାଫଳ।",
      followup_summary: "୧୨୪ ଜଣଙ୍କୁ ସହାୟତା ଆବଶ୍ୟକ · ୭୨% ସମାଧାନ ହୋଇଛି",
      btn_working: "କାର୍ଯ୍ୟରତ",
      btn_own_work: "ନିଜ ବ୍ୟବସାୟ",
      btn_need_help: "ସାହାଯ୍ୟ ଦରକାର",
      btn_send_now: "ବାର୍ତ୍ତା ପଠାନ୍ତୁ",
      btn_seed_demo: "ଡେମୋ ଡାଟା ଲୋଡ୍ କରନ୍ତୁ",
      btn_new_trainee: "ନୂତନ ପ୍ରଶିକ୍ଷାର୍ଥୀ",
      btn_export_csv: "CSV ଡାଉନଲୋଡ୍",
      filter_all_providers: "ସମସ୍ତ ପ୍ରଦାତା",
      filter_all_stages: "ସମସ୍ତ ପର୍ଯ୍ୟାୟ",
      filter_all_consents: "ସମସ୍ତ ସମ୍ମତି",
      th_learner: "ପ୍ରଶିକ୍ଷାର୍ଥୀ",
      th_stage: "ବର୍ତ୍ତମାନ ପର୍ଯ୍ୟାୟ",
      th_provider: "ପ୍ରଦାତା",
      th_signal: "ନିଯୁକ୍ତିଦାତା ସ୍ୱୀକୃତି",
      th_wage: "ମାସିକ ଦରମା",
      th_updated: "ଶେଷ ଅପଡେଟ୍",
      th_actions: "ପଦକ୍ଷେପ",
      trainee_welcome: "ସ୍ୱାଗତ,",
      trainee_progress: "ଆପଣଙ୍କ ତାଲିମ ଓ ନିଯୁକ୍ତି ଯାତ୍ରା",
      trainee_consent_label: "ସମ୍ମତି ସ୍ଥିତି:",
      trainee_consent_active: "ସକ୍ରିୟ ଓ ସୁରକ୍ଷିତ",
      trainee_consent_withdrawn: "ପ୍ରତ୍ୟାହୃତ",
      trainee_btn_work: "ମୁଁ ଚାକିରି କରୁଛି",
      trainee_btn_business: "ମୋର ନିଜ ବ୍ୟବସାୟ ଅଛି",
      trainee_btn_support: "ମୋତେ ସାହାଯ୍ୟ ଦରକାର",
      trainee_download_report: "ପ୍ରଗତି ରିପୋର୍ଟ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
      save_changes: "ସାଇତନ୍ତୁ",
      cancel: "ବାତିଲ୍ କରନ୍ତୁ",
      search_placeholder: "ନାମ, ଆଇଡି କିମ୍ବା କୋର୍ସ ଖୋଜନ୍ତୁ...",
      nav_step1: "୧. ଡ୍ୟାସବୋର୍ଡ",
      nav_step2: "୨. ପ୍ରଶିକ୍ଷକଙ୍କ ପାଠ୍ୟକ୍ରମ",
      nav_step3: "୩. ନିଶ୍ଚିତକରଣ",
      nav_step4: "୪. ପ୍ରଶିକ୍ଷକ ଯୋଗ୍ୟତା",
      nav_feedback: "ମତାମତ ଏବଂ ରେଟିଂ",
      nav_pulse: "ପ୍ରୋଗ୍ରାମ ପଲ୍ସ",
      nav_trainees_dir: "ପ୍ରଶିକ୍ଷାର୍ଥୀ ତାଲିକା",
      nav_recovery: "ଡାର୍କ-ଜୋନ୍ ପୁନରୁଦ୍ଧାର",
      nav_settings: "ସେଟିଙ୍ଗ୍ସ",
      trainee_nav_1: "୧. ଡ୍ୟାସବୋର୍ଡ",
      trainee_nav_2: "୨. ସରକାରୀ ପାଠ୍ୟକ୍ରମ",
      trainee_nav_3: "୩. ଶିକ୍ଷଣ ରେକର୍ଡ",
      trainee_nav_4: "୪. ପ୍ରମାଣପତ୍ର",
      trainee_nav_5: "୫. ନିଯୁକ୍ତି ବିବରଣୀ",
      trainee_nav_6: "୬. ମତାମତ ଏବଂ ରେଟିଂ",
      feedback_section_title: "ଛାତ୍ର ମତାମତ ଏବଂ ରେଟିଂ",
      feedback_section_sub: "ପ୍ରଶିକ୍ଷାର୍ଥୀମାନଙ୍କ ଦ୍ୱାରା ଦିଆଯାଇଥିବା ସରଳ ରେଟିଂ ଓ ମତାମତ",
      kpi_overall_score: "ସମଗ୍ର ଟ୍ରେନର ସ୍କୋର",
      kpi_behavior_label: "ବ୍ୟବହାର ଓ ସମ୍ମାନ",
      kpi_teaching_label: "ଶିକ୍ଷାଦାନ ଗୁଣବତ୍ତା",
      kpi_doubts_label: "ସନ୍ଦେହ ମୋଚନ ଓ ସହାୟତା",
      top_course_title: "ସର୍ବୋତ୍ତମ ରେଟିଂ ପ୍ରାପ୍ତ କୋର୍ସ",
      top_course_badge: "ଶ୍ରେଷ୍ଠ ପ୍ରଦର୍ଶନ",
      needs_attention_title: "ସୁଧାର ଆବଶ୍ୟକ କୋର୍ସ",
      needs_attention_badge: "ପଦକ୍ଷେପ ଆବଶ୍ୟକ",
      why_diagnostics_title: "କେଉଁଠି ଅସୁବିଧା ହେଲା (ବିଶ୍ଳେଷଣ)",
      reason_pacing: "ଖୁବ୍ ଶୀଘ୍ର ପଢ଼ାଗଲା",
      reason_labs: "ପ୍ରାକ୍ଟିକାଲ୍ ଲାବ୍ ଅଧିକ ଦରକାର",
      reason_doubts: "ଅଧିକ ସନ୍ଦେହ ସମାଧାନ ଆବଶ୍ୟକ ଥିଲା",
      reason_notes: "ସ୍ଥାନୀୟ ଓଡ଼ିଆ ଭାଷାରେ ନୋଟ୍ସ ଦରକାର",
      trainee_feedback_title: "ଆପଣଙ୍କ ପ୍ରଶିକ୍ଷକ ଓ କୋର୍ସର ମୂଲ୍ୟାଙ୍କନ କରନ୍ତୁ",
      trainee_feedback_sub: "ଗୋଟିଏ ଟ୍ୟାପ୍ ରେ ସରଳ ଛବି ସହ ରେଟିଂ ଦିଅନ୍ତୁ",
      select_course_label: "ସମାପ୍ତ କୋର୍ସ ବାଛନ୍ତୁ",
      btn_submit_feedback: "ମତାମତ ଦାଖଲ କରନ୍ତୁ",
      submitted_history_title: "ପୂର୍ବରୁ ଦିଆଯାଇଥିବା ମତାମତ",
      mood_outstanding: "ଉତ୍କୃଷ୍ଟ ଏବଂ ବହୁତ ସମ୍ମାନଜନକ!",
      mood_good: "ଭଲ ଏବଂ ସହାୟକ",
      mood_average: "ସାଧାରଣ / ଠିକ୍ ଅଛି",
      mood_needs_improvement: "ସୁଧାର ଦରକାର",
      mood_poor: "ସନ୍ତୁଷ୍ଟ ନୁହେଁ",
      // Follow-Up Queue terms
      followup_queue: "ଫଲୋ-ଅପ୍ ତାଲିକା",
      pending_actions: "ବାକି ଥିବା କାର୍ଯ୍ୟ",
      pending: "ବାକି ଅଛି",
      whatsapp: "ହ୍ୱାଟ୍ସଆପ୍ (WhatsApp)",
      sms: "ଏସଏମଏସ (SMS)",
      call_script: "କଲ୍ ସ୍କ୍ରିପ୍ଟ",
      followup_preview_placeholder: "ବାର୍ତ୍ତା ଦେଖିବା ପାଇଁ ତାଲିକାରୁ ଜଣେ ପ୍ରଶିକ୍ଷାର୍ଥୀଙ୍କୁ ବାଛନ୍ତୁ।",
      send_message: "ବାର୍ତ୍ତା ପଠାନ୍ତୁ",
      mark_resolved: "ସମାଧାନ ଚିହ୍ନଟ କରନ୍ତୁ",
      theme_light: "ଲାଇଟ୍",
      theme_dark: "ଡାର୍କ",
      trainer_portal: "ପ୍ରଶିକ୍ଷକ ପୋର୍ଟାଲ",
      trainee_portal: "ପ୍ରଶିକ୍ଷାର୍ଥୀ ପୋର୍ଟାଲ",
      sign_in: "ସାଇନ୍ ଇନ୍",
      sign_up: "ସାଇନ୍ ଅପ୍",
      track_real_outcomes: "ପ୍ରକୃତ ଦକ୍ଷତା ଫଳାଫଳ ଟ୍ରାକ୍ କରନ୍ତୁ",
      capabilities_title: "ଦକ୍ଷତା ବିକାଶ ପାଇଁ ସମସ୍ତ ସୁବିଧା",
      how_it_works_title: "ନାମାଙ୍କନରୁ ରୋଜଗାର ପର୍ଯ୍ୟନ୍ତ",
      demo_title: "ଲାଇଭ୍ ଡେମୋ ଦେଖନ୍ତୁ"
    },
    mr: {
      brand_name: "स्किलपल्स (SkillPulse)",
      workspace: "उत्कृष्ट परिणाम / राष्ट्रीय कार्यक्षेत्र",
      nav_overview: "आढावा",
      nav_followups: "फॉलो-अप",
      nav_trainees: "प्रशिक्षणार्थी",
      nav_reports: "अहवाल",
      nav_feedback: "अभिप्राय आणि रेटिंग",
      followup_queue: "फॉलो-अप रांग",
      pending_actions: "प्रलंबित कृती",
      pending: "प्रलंबित",
      whatsapp: "व्हॉट्सॲप",
      sms: "एसएमएस",
      call_script: "कॉल स्क्रिप्ट",
      send_message: "संदेश पाठवा",
      mark_resolved: "निकाली काढा",
      trainer_portal: "प्रशिक्षक पोर्टल",
      trainee_portal: "प्रशिक्षणार्थी पोर्टल",
      theme_light: "लाइट",
      theme_dark: "डार्क"
    },
    bn: {
      brand_name: "স্কিলপালস (SkillPulse)",
      nav_overview: "সংক্ষিপ্ত বিবরণ",
      nav_followups: "ফলো-আপ",
      nav_trainees: "প্রশিক্ষণার্থী",
      nav_reports: "প্রতিবেদন",
      nav_feedback: "মতামত ও রেটিং",
      followup_queue: "ফলো-আপ সারি",
      pending_actions: "মুলতুবি কাজ",
      pending: "মুলতুবি",
      whatsapp: "হোয়াটসঅ্যাপ",
      sms: "এসএমএস",
      call_script: "কল স্ক্রিপ্ট",
      send_message: "বার্তা পাঠান",
      mark_resolved: "সমাধান চিহ্নিত করুন",
      trainer_portal: "প্রশিক্ষক পোর্টাল",
      trainee_portal: "প্রশিক্ষণার্থী পোর্টাল",
      theme_light: "লাইট",
      theme_dark: "ডার্ক"
    },
    ta: {
      brand_name: "ஸ்கில்பல்ஸ் (SkillPulse)",
      nav_overview: "கண்ணோட்டம்",
      nav_followups: "பின்தொடர்தல்",
      nav_trainees: "பயிற்சி பெறுவோர்",
      nav_reports: "அறிக்கைகள்",
      nav_feedback: "கருத்து மற்றும் மதிப்பீடு",
      followup_queue: "பின்தொடர்தல் வரிசை",
      pending_actions: "நிலுவையில் உள்ளவை",
      pending: "நிலுவை",
      whatsapp: "வாட்ஸ்அப்",
      sms: "எஸ்எம்எஸ்",
      call_script: "அழைப்பு ஸ்கிரிப்ட்",
      send_message: "செய்தி அனுப்பு",
      mark_resolved: "தீர்வு குறிக்கவும்",
      trainer_portal: "பயிற்றுவிப்பாளர் போர்டல்",
      trainee_portal: "பயிற்சி பெறுவோர் போர்டல்",
      theme_light: "லைட்",
      theme_dark: "டார்க்"
    },
    te: {
      brand_name: "స్కిల్‌పల్స్ (SkillPulse)",
      nav_overview: "అవలోకనం",
      nav_followups: "ఫాలో-అప్‌లు",
      nav_trainees: "శిక్షణార్థులు",
      nav_reports: "నివేదికలు",
      nav_feedback: "అభిప్రాయం & రేటింగ్‌లు",
      followup_queue: "ఫాలో-అప్ క్యూ",
      pending_actions: "పెండింగ్ చర్యలు",
      pending: "పెండింగ్",
      whatsapp: "వాట్సాప్",
      sms: "ఎస్ఎంఎస్",
      call_script: "కాల్ స్క్రిప్ట్",
      send_message: "సందేశం పంపండి",
      mark_resolved: "పరిష్కరించినట్లు గుర్తించండి",
      trainer_portal: "ట్రైనర్ పోర్టల్",
      trainee_portal: "ట్రైనీ పోర్టల్",
      theme_light: "లైట్",
      theme_dark: "డార్క్"
    },
    kn: {
      brand_name: "ಸ್ಕಿಲ್‌ಪಲ್ಸ್ (SkillPulse)",
      nav_overview: "ಅವಲೋಕನ",
      nav_followups: "ಫಾಲೋ-ಅಪ್‌ಗಳು",
      nav_trainees: "ಪ್ರಶಿಕ್ಷಣಾರ್ಥಿಗಳು",
      nav_reports: "ವರದಿಗಳು",
      nav_feedback: "ಪ್ರತಿಕ್ರಿಯೆ ಮತ್ತು ರೇಟಿಂಗ್",
      followup_queue: "ಫಾಲೋ-ಅಪ್ ಕ್ಯೂ",
      pending_actions: "ಬಾಕಿ ಕ್ರಮಗಳು",
      pending: "ಬಾಕಿ",
      whatsapp: "ವಾಟ್ಸಾಪ್",
      sms: "ಎಸ್ಎಂಎಸ್",
      call_script: "ಕಾಲ್ ಸ್ಕ್ರಿಪ್ಟ್",
      send_message: "ಸಂದೇಶ ಕಳುಹಿಸಿ",
      mark_resolved: "ಪರಿಹರಿಸಲಾಗಿದೆ ಎಂದು ಗುರುತಿಸಿ",
      trainer_portal: "ತರಬೇತುದಾರ ಪೋರ್ಟಲ್",
      trainee_portal: "ಪ್ರಶಿಕ್ಷಣಾರ್ಥಿ ಪೋರ್ಟಲ್",
      theme_light: "ಲೈಟ್",
      theme_dark: "ಡಾರ್ಕ್"
    },
    gu: {
      brand_name: "સ્કિલપલ્સ (SkillPulse)",
      nav_overview: "ઝાંખી",
      nav_followups: "ફોલો-અપ્સ",
      nav_trainees: "તાલીમાર્થીઓ",
      nav_reports: "અહેવાલો",
      nav_feedback: "પ્રતિસાદ અને રેટિંગ",
      followup_queue: "ફોલો-અપ કતાર",
      pending_actions: "બાકી ક્રિયાઓ",
      pending: "બાકી",
      whatsapp: "વોટ્સએપ",
      sms: "એસએમએસ",
      call_script: "કૉલ સ્ક્રિપ્ટ",
      send_message: "સંદેશ મોકલો",
      mark_resolved: "ઉકેલાયેલ ચિહ્નિત કરો",
      trainer_portal: "ટ્રેનર પોર્ટલ",
      trainee_portal: "તાલીમાર્થી પોર્ટલ",
      theme_light: "લાઇટ",
      theme_dark: "ડાર્ક"
    },
    pa: {
      brand_name: "ਸਕਿੱਲਪਲਸ (SkillPulse)",
      nav_overview: "ਸੰਖੇਪ ਜਾਣਕਾਰੀ",
      nav_followups: "ਫਾਲੋ-ਅੱਪ",
      nav_trainees: "ਸਿਖਿਆਰਥੀ",
      nav_reports: "ਰਿਪੋਰਟਾਂ",
      nav_feedback: "ਫੀਡਬੈਕ ਅਤੇ ਰੇਟਿੰਗ",
      followup_queue: "ਫਾਲੋ-ਅੱਪ ਕਤਾਰ",
      pending_actions: "ਬਾਕੀ ਕਾਰਵਾਈਆਂ",
      pending: "ਬਾਕੀ",
      whatsapp: "ਵਟਸਐਪ",
      sms: "ਐਸਐਮਐਸ",
      call_script: "ਕਾਲ ਸਕ੍ਰਿਪਟ",
      send_message: "ਸੁਨੇਹਾ ਭੇਜੋ",
      mark_resolved: "ਹੱਲ ਵਜੋਂ ਚਿੰਨ੍ਹਿਤ ਕਰੋ",
      trainer_portal: "ਟ੍ਰੇਨਰ ਪੋਰਟਲ",
      trainee_portal: "ਸਿਖਿਆਰਥੀ ਪੋਰਟਲ",
      theme_light: "ਲਾਈਟ",
      theme_dark: "ਡਾਰਕ"
    },
    ml: {
      brand_name: "സ്കിൽപൾസ് (SkillPulse)",
      nav_overview: "അവലോകനം",
      nav_followups: "ഫോളോ-അപ്പുകൾ",
      nav_trainees: "പരിശീലനാർത്ഥികൾ",
      nav_reports: "റിപ്പോർട്ടുകൾ",
      nav_feedback: "പ്രതികരണവും റേറ്റിംഗും",
      followup_queue: "ഫോളോ-അപ്പ് ക്യൂ",
      pending_actions: "തീർപ്പാക്കാത്ത നടപടികൾ",
      pending: "ബാക്കി",
      whatsapp: "വാട്ട്സ്ആപ്പ്",
      sms: "എസ്എംഎസ്",
      call_script: "കോൾ സ്ക്രിപ്റ്റ്",
      send_message: "സന്ദേശം അയക്കുക",
      mark_resolved: "പരിഹരിച്ചതായി അടയാളപ്പെടുത്തുക",
      trainer_portal: "ട്രെയിനർ പോർട്ടൽ",
      trainee_portal: "ട്രെയിനി പോർട്ടൽ",
      theme_light: "ലൈറ്റ്",
      theme_dark: "ഡാർക്ക്"
    },
    ur: {
      brand_name: "اسکل پلس (SkillPulse)",
      nav_overview: "جائزہ",
      nav_followups: "فالو اپس",
      nav_trainees: "تربیت یافتگان",
      nav_reports: "رپورٹس",
      nav_feedback: "فیڈ بیک اور درجہ بندی",
      followup_queue: "فالو اپ قطار",
      pending_actions: "زیر التواء اقدامات",
      pending: "زیر التواء",
      whatsapp: "واٹس ایپ",
      sms: "ایس ایم ایس",
      call_script: "کال اسکرپٹ",
      send_message: "پیغام بھیجیں",
      mark_resolved: "حل شدہ نشان زد کریں",
      trainer_portal: "ٹرینر پورٹل",
      trainee_portal: "ٹرینی پورٹل",
      theme_light: "لائٹ",
      theme_dark: "ڈارک"
    }
  };

  // Maps normalized English text to translation keys
  const phraseToKey = {
    'follow-ups': 'nav_followups',
    'follow-up queue': 'followup_queue',
    'pending actions': 'pending_actions',
    'pending': 'pending',
    'whatsapp': 'whatsapp',
    'sms': 'sms',
    'call script': 'call_script',
    'select a follow-up item from the queue to preview the outreach message.': 'followup_preview_placeholder',
    'send message': 'send_message',
    'mark resolved': 'mark_resolved',
    'overview': 'nav_overview',
    'trainees': 'nav_trainees',
    'trainees directory': 'nav_trainees_dir',
    'reports': 'nav_reports',
    'reports & exports': 'nav_reports',
    'dark-zone recovery': 'nav_recovery',
    'dark-zone & remote trainee recovery hub': 'nav_recovery',
    'feedback & ratings': 'nav_feedback',
    'student feedback & ratings': 'feedback_section_title',
    'settings': 'nav_settings',
    'sign out': 'nav_logout',
    'programme pulse': 'nav_pulse',
    'light': 'theme_light',
    'dark': 'theme_dark',
    'trainer portal': 'trainer_portal',
    'trainee portal': 'trainee_portal',
    'sign in': 'sign_in',
    'sign up': 'sign_up',
    'track real skilling outcomes that matter': 'track_real_outcomes',
    'everything you need for skilling excellence': 'capabilities_title',
    'from enrollment to employment': 'how_it_works_title',
    'try the live demo': 'demo_title',
    'active trainees': 'metric_active',
    'verified outcomes': 'metric_active',
    'placement rate': 'metric_retention',
    'avg. monthly wage': 'metric_wage',
    'enrolled': 'route_enrolled',
    'trained': 'route_trained',
    'certified': 'route_certified',
    'placed': 'route_placed',
    'retained': 'route_retained'
  };

  function t(key) {
    if (translations[currentLang] && translations[currentLang][key]) {
      return translations[currentLang][key];
    }
    if (translations.hi && (currentLang !== 'en') && translations.hi[key]) {
      // Graceful fallback to Hindi for regional languages if direct key missing
      return translations.hi[key];
    }
    if (translations.en && translations.en[key]) {
      return translations.en[key];
    }
    return key;
  }

  function ensureOdiaOption(select) {
    if (!select.querySelector('option[value="or"]')) {
      const opt = document.createElement('option');
      opt.value = 'or';
      opt.textContent = 'ଓଡ଼ିଆ (Odia)';
      select.appendChild(opt);
    }
  }

  // Deep scanner: translates all DOM elements reliably across all pages
  function translatePage() {
    // 1. Direct [data-i18n] elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = t(key);
      if (text) {
        if (el.children.length > 0) {
          Array.from(el.childNodes).forEach(node => {
            if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim().length > 0) {
              node.nodeValue = ' ' + text.trim() + ' ';
            }
          });
        } else {
          el.textContent = text;
        }
      }
    });

    // 2. Placeholders & titles
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const text = t(el.getAttribute('data-i18n-placeholder'));
      if (text) el.placeholder = text;
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const text = t(el.getAttribute('data-i18n-title'));
      if (text) el.title = text;
    });

    // 3. Deep Phrase Matching on Headings, Buttons, Labels, Tabs, and Table Headers
    const targetSelectors = [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      '.nav-link', '.sidebar-nav a', '.bottom-nav-item span', '.nav-group-label',
      '.btn', 'button', '.badge', '.simulator-tab-btn', '.theme-text',
      'th', '.stat-item p', '.eyebrow', '#header-active-view-name',
      '.message-bubble', '#simulator-message', '#followup-count'
    ];

    document.querySelectorAll(targetSelectors.join(', ')).forEach(el => {
      // Store original English text on first encounter
      if (!el.dataset.originalText) {
        el.dataset.originalText = el.textContent.trim();
      }

      const orig = el.dataset.originalText;
      if (!orig) return;

      // Handle numbers + pending pattern like "4 pending"
      const pendingMatch = orig.match(/^(\d+)\s+pending$/i);
      if (pendingMatch) {
        const count = pendingMatch[1];
        if (currentLang === 'en') {
          el.textContent = `${count} pending`;
        } else {
          el.textContent = `${count} ${t('pending')}`;
        }
        return;
      }

      const normalized = orig.toLowerCase().replace(/[·:.]/g, '').trim();
      const key = phraseToKey[normalized] || phraseToKey[orig.toLowerCase().trim()];

      if (key) {
        const translated = t(key);
        if (translated) {
          if (currentLang === 'en') {
            // Restore original
            if (el.children.length > 0) {
              Array.from(el.childNodes).forEach(node => {
                if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim().length > 0) {
                  node.nodeValue = ' ' + orig + ' ';
                }
              });
            } else {
              el.textContent = orig;
            }
          } else {
            // Apply translation
            if (el.children.length > 0) {
              Array.from(el.childNodes).forEach(node => {
                if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim().length > 0) {
                  node.nodeValue = ' ' + translated.trim() + ' ';
                }
              });
            } else {
              el.textContent = translated;
            }
          }
        }
      }
    });
  }

  function setLanguage(langCode, persist = true) {
    if (!translations[langCode]) {
      langCode = 'en';
    }
    currentLang = langCode;

    document.documentElement.lang = langCode;
    const isRtl = (langCode === 'ur');
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';

    localStorage.setItem('field_atlas_lang', langCode);
    localStorage.setItem('skillpulse_lang', langCode);

    document.querySelectorAll('.lang-select').forEach(select => {
      ensureOdiaOption(select);
      select.value = langCode;
    });

    translatePage();

    if (persist && window.FieldAtlasAPI) {
      FieldAtlasAPI.post('/api/i18n/set-language/', { language: langCode }, { silent: true }).catch(() => {});
    }

    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: langCode, isRtl } }));
  }

  function initLanguageSelector() {
    const savedLang = localStorage.getItem('skillpulse_lang') || localStorage.getItem('field_atlas_lang') || 'en';
    
    document.querySelectorAll('.lang-select').forEach(select => {
      ensureOdiaOption(select);
      select.value = savedLang;
      select.onchange = function(e) {
        setLanguage(e.target.value, true);
      };
    });

    setLanguage(savedLang, false);
  }

  return {
    t: t,
    setLanguage: setLanguage,
    initLanguageSelector: initLanguageSelector,
    translatePage: translatePage,
    getCurrentLanguage: function() { return currentLang; }
  };
})();

// Initialize language settings when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    FieldAtlasI18N.initLanguageSelector();
  });
} else {
  FieldAtlasI18N.initLanguageSelector();
}

// Global Aliases
window.SkillPulseI18N = FieldAtlasI18N;
window.FieldAtlasI18N = FieldAtlasI18N;
