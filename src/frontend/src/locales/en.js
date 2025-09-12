export default {
  // Main title and header
  title: 'Film Editing Studio',
  poweredBy: '⭐ Powered by {model} ⭐',
  
  // Navigation and steps
  operationSteps: 'Operation Steps',
  operationSuggestion: 'Please follow the prompts to set parameters, then execute step by step',
  
  // Step titles
  steps: {
    step1: 'Step1: Extract Plot',
    step2: 'Step2: Generate Highlight Video', 
    step3: 'Step3: Generate Video Narration',
    step4: 'Step4: Synthesize Narration Video'
  },
  
  // Parameter configuration
  paramConfig: '{operation} - Parameter Configuration',
  
  // Extract plots section
  extractPlots: {
    videoSource: 'Video Source (Choose One)',
    gcsVideoLink: 'GCS Video URL',
    gcsPlaceholder: 'gs://movie-clip/sample/yhhhs.1.mp4',
    uploadLocalFile: 'Upload Local File',
    dragUpload: 'Drop video file here, or',
    clickUpload: 'click to upload',
    uploadTip: 'Supports MP4/MKV/WEBM/MPEG4 formats, max file size 10GB',
    gcsHint: 'Tip: Please upload to project:veo-testing bucket:movie-clip, recommend analyzing videos over 10 minutes',
    actorsInfo: 'Actor Information',
    actorsPlaceholder: 'Actor names and character info, e.g.: Ma Xiaoshuai is played by Jiang Wen',
    executeExtract: 'Execute Plot Extraction'
  },
  
  // Generate highlight section
  generateHighlight: {
    prerequisite: '🎬 Please Extract Plot First',
    prerequisiteDesc: 'You need to complete Step1: Extract Plot before generating highlight video. Please return to Step1 to upload video and extract plot.',
    backToStep1: 'Back to Step1: Extract Plot',
    highlightParams: 'Highlight Video Parameters',
    starring: 'Highlight Video Starring',
    starringPlaceholder: 'Please enter starring actor name',
    duration: 'Highlight Video Duration',
    durationPlaceholder: 'e.g.: 5 minutes',
    executeGenerate: 'Execute Generate Highlight Video'
  },
  
  // Generate narration section  
  generateNarration: {
    prerequisite: '🎥 Please Generate Highlight Video First',
    prerequisiteDesc: 'You need to complete Step2: Generate Highlight Video before generating video narration. Please return to Step2 to generate highlight video.',
    backToStep2: 'Back to Step2: Generate Highlight Video',
    roleStyleSettings: 'Role & Style Settings',
    roleSet: 'Role Setting',
    roleSetPlaceholder: 'Please describe role setting, e.g.: Reimagine Zhang Qiusheng as a superhero',
    movieBg: 'Movie Background',
    movieBgPlaceholder: 'Movie background info, e.g.: Video is clips of character Zhang Qiusheng from "Keep Cool"',
    narrationStyle: 'Narration Style',
    narrationStylePlaceholder: 'e.g.: Wong Kar-wai movie style',
    characterNickname: 'Character Nickname',
    characterNicknamePlaceholder: 'How to address the character, e.g.: Li Baotian called as Lao Li',
    selectVoice: 'Select Voice',
    executeNarration: 'Execute Generate Video Narration'
  },
  
  // Generate narration video section
  generateNarrationVideo: {
    prerequisite: '🎬 Please Generate Video Narration First',
    prerequisiteDesc: 'You need to complete Step3: Generate Video Narration before final video synthesis. Please return to corresponding step to complete prerequisite operations.',
    backToStep3: 'Back to Step3: Generate Video Narration',
    synthConfig: 'Synthesis Configuration',
    minimaxApiKey: 'MiniMax API Key',
    minimaxGroupId: 'MiniMax Group ID',
    apiKeyPlaceholder: 'API Key (optional)',
    groupIdPlaceholder: 'Group ID (optional)',
    executeSynth: 'Execute Synthesize Narration Video'
  },
  
  // Results section
  results: {
    title: 'Processing Results',
    clickForDetails: 'Click card for details',
    plotExtraction: 'Plot Extraction Results',
    highlightVideo: 'Highlight Video',
    narrationContent: 'Narration Content',
    finalVideo: 'Final Composite Video',
    completed: 'Completed',
    clickForVideo: 'Click to play video',
    clickForDetails2: 'Click for details',
    regenerate: 'Regenerate',
    generate: 'Generate',
    waiting: {
      plots: 'Waiting for plot extraction...',
      highlight: 'Waiting for highlight video generation...',
      narration: 'Waiting for narration generation...',
      final: 'Waiting for final video synthesis...'
    },
    narrationCount: 'Generated {count} narration segments'
  },
  
  // Modal titles
  modals: {
    plotsResult: 'Plot Extraction Results',
    highlightVideo: 'Highlight Video',
    narrationContent: 'Narration Content',
    finalVideo: 'Final Composite Video',
    segment: 'Segment {index}',
    downloadHighlight: 'Download Highlight Video',
    downloadFinal: 'Download Final Video',
    browserNotSupported: 'Your browser does not support video playback.',
    timestamp: 'Timestamp',
    relativeTime: 'Relative Time(s)',
    narrationText: 'Narration Content'
  },
  
  // Common actions
  actions: {
    or: 'Or',
    download: 'Download',
    close: 'Close',
    confirm: 'Confirm',
    cancel: 'Cancel'
  },
  
  // Error messages
  errors: {
    fillRequired: 'Please fill in required parameters',
    extractFirst: 'Please execute plot extraction first',
    generateHighlightFirst: 'Please generate highlight video first',
    generateNarrationFirst: 'Please generate video narration first',
    extractFailed: 'Plot extraction failed',
    highlightFailed: 'Highlight video generation failed',
    narrationFailed: 'Video narration generation failed',
    synthFailed: 'Narration video synthesis failed',
    configLoadFailed: 'Configuration loading failed',
    backendConnect: 'Unable to connect to backend service, please ensure backend service is running'
  },
  
  // Language switcher
  language: {
    switch: 'Switch Language',
    chinese: '中文',
    english: 'English'
  },
  
  // Default values
  defaults: {
    actorsInfo: 'Ma Xiaoshuai is played by Jiang Wen, Zhang Qiusheng is played by Li Baotian',
    highlightStarring: 'Li Baotian',
    highlightDuration: '5 minutes',
    roleSet: 'Reimagine Zhang Qiusheng (played by Li Baotian) as a superhero',
    narrationStyle: 'Wong Kar-wai movie style',
    narrationCharacterNickname: 'Li Baotian called as Lao Li',
    narrationMovieBg: 'Video is clips of character Zhang Qiusheng from "Keep Cool", please refer to this background and character setting'
  }
}
