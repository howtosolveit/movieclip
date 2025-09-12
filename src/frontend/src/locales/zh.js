export default {
  // Main title and header
  title: 'Film Editting Workflow',
  poweredBy: '⭐ Powered by {model} ⭐',
  
  // Navigation and steps
  operationSteps: '操作步骤',
  operationSuggestion: '请参照提示设置参数，然后按步骤执行',
  
  // Step titles
  steps: {
    step1: 'Step1: 提取剧情',
    step2: 'Step2: 生成高光视频', 
    step3: 'Step3: 生成视频旁白',
    step4: 'Step4: 合成旁白视频'
  },
  
  // Parameter configuration
  paramConfig: '{operation} - 参数配置',
  
  // Extract plots section
  extractPlots: {
    videoSource: '视频来源 (二选一)',
    gcsVideoLink: 'GCS视频地址',
    gcsPlaceholder: 'gs://movie-clip/sample/yhhhs.1.mp4',
    uploadLocalFile: '上传本地文件',
    dragUpload: '将视频文件拖到此处，或',
    clickUpload: '点击上传',
    uploadTip: '支持 MP4/MKV/WEBM/MPEG4 格式，文件大小限制 10GB',
    gcsHint: '提示：请上传到 project:veo-testing bucket:movie-clip，建议分析10分钟以上视频',
    actorsInfo: '演员信息',
    actorsPlaceholder: '演员姓名及角色信息，如：马小帅的扮演者是姜文',
    executeExtract: '执行提取剧情'
  },
  
  // Generate highlight section
  generateHighlight: {
    prerequisite: '🎬 请先提取剧情',
    prerequisiteDesc: '需要先完成 Step1: 提取剧情，才能进行高光视频生成。请返回 Step1 上传视频并提取剧情。',
    backToStep1: '返回 Step1: 提取剧情',
    highlightParams: '高光视频参数',
    starring: '高光短片主角',
    starringPlaceholder: '请输入主角名称',
    duration: '高光短片时长',
    durationPlaceholder: '如：5分钟',
    executeGenerate: '执行生成高光视频'
  },
  
  // Generate narration section  
  generateNarration: {
    prerequisite: '🎥 请先生成高光视频',
    prerequisiteDesc: '需要先完成 Step2: 生成高光视频，才能进行视频旁白生成。请返回 Step2 生成高光视频。',
    backToStep2: '返回 Step2: 生成高光视频',
    roleStyleSettings: '角色与风格设定',
    roleSet: '角色设定',
    roleSetPlaceholder: '请描述角色设定，如：将张秋生重新设想为一个超级英雄',
    movieBg: '影片背景',
    movieBgPlaceholder: '影片背景信息，如：视频为《有话好好说》关于角色张秋生的剪辑视频',
    narrationStyle: '叙述风格',
    narrationStylePlaceholder: '如：王家卫电影风格',
    characterNickname: '角色代号',
    characterNicknamePlaceholder: '角色的称呼方式，如：李保田称之为老李',
    selectVoice: '选择配音',
    executeNarration: '执行生成视频旁白'
  },
  
  // Generate narration video section
  generateNarrationVideo: {
    prerequisite: '🎬 请先生成视频旁白',
    prerequisiteDesc: '需要先完成 Step3: 生成视频旁白，才能进行最终视频合成。请返回相应步骤完成前置操作。',
    backToStep3: '返回 Step3: 生成视频旁白',
    synthConfig: '合成配置',
    minimaxApiKey: 'MiniMax API Key',
    minimaxGroupId: 'MiniMax Group ID',
    apiKeyPlaceholder: 'API Key (可选)',
    groupIdPlaceholder: 'Group ID (可选)',
    executeSynth: '执行合成旁白视频'
  },
  
  // Results section
  results: {
    title: '处理结果',
    clickForDetails: '点击卡片查看详情',
    plotExtraction: '剧情提取结果',
    highlightVideo: '高光视频',
    narrationContent: '旁白内容',
    finalVideo: '最终合成视频',
    completed: '已完成',
    clickForVideo: '点击播放视频',
    clickForDetails2: '点击查看详情',
    regenerate: '重新生成',
    generate: '去生成',
    waiting: {
      plots: '等待剧情提取...',
      highlight: '等待高光视频生成...',
      narration: '等待旁白生成...',
      final: '等待最终视频合成...'
    },
    narrationCount: '已生成 {count} 段旁白'
  },
  
  // Modal titles
  modals: {
    plotsResult: '剧情提取结果',
    highlightVideo: '高光视频',
    narrationContent: '旁白内容',
    finalVideo: '最终合成视频',
    segment: '片段 {index}',
    downloadHighlight: '下载高光视频',
    downloadFinal: '下载最终视频',
    browserNotSupported: '您的浏览器不支持视频播放。',
    timestamp: '时间戳',
    relativeTime: '相对时间(s)',
    narrationText: '旁白内容'
  },
  
  // Common actions
  actions: {
    or: '或',
    download: '下载',
    close: '关闭',
    confirm: '确认',
    cancel: '取消'
  },
  
  // Error messages
  errors: {
    fillRequired: '请填写必要的参数',
    extractFirst: '请先执行提取剧情',
    generateHighlightFirst: '请先生成高光视频',
    generateNarrationFirst: '请先生成视频旁白',
    extractFailed: '提取剧情失败',
    highlightFailed: '生成高光视频失败',
    narrationFailed: '生成视频旁白失败',
    synthFailed: '合成旁白视频失败',
    configLoadFailed: '配置加载失败',
    backendConnect: '无法连接到后端服务，请确保后端服务已启动'
  },
  
  // Language switcher
  language: {
    switch: '切换语言',
    chinese: '中文',
    english: 'English'
  },
  
  // Default values
  defaults: {
    actorsInfo: '马小帅的扮演者是姜文，张秋生的扮演者是李保田',
    highlightStarring: '李保田',
    highlightDuration: '5分钟',
    roleSet: '将张秋生（由李保田饰演）重新设想为一个超级英雄',
    narrationStyle: '王家卫电影风格',
    narrationCharacterNickname: '李保田称之为老李',
    narrationMovieBg: '视频为《有话好好说》关于角色张秋生的剪辑视频，请参考此背景以及人物的设定'
  }
}
