<template>
  <div class="app-container">
    <!-- Main Content -->
    <div class="main-container">
      <!-- Main Title Section -->
      <div class="main-title-section">
        <div class="title-content">
          <h1 class="main-title mario-title">
            🍄 超级玛丽剪辑工作室 🍄
            <span v-if="selectedModel" class="model-info-inline mario-power">
              ⭐ Powered by {{ selectedModel }} ⭐
            </span>
          </h1>
        </div>
      </div>
      <!-- Content Area -->
      <div class="content-area">
        <!-- Operations Section -->
        <el-card class="section-card operations-card" shadow="hover">
          <template #header>
            <div class="section-header">
              <el-icon class="section-icon"><Operation /></el-icon>
              <span class="section-title">操作步骤</span>
            </div>
          </template>

          <div class="operations-grid">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-button
                  type="primary"
                  size="large"
                  @click="selectOperation('extractPlots')"
                  class="operation-btn step1"
                  :class="{ 'selected': selectedOperation === 'extractPlots' }"
                  data-operation="extractPlots"
                >
                  <el-icon><Document /></el-icon>
                  Step1: 提取剧情
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button
                  type="success"
                  size="large"
                  @click="selectOperation('generateHighlight')"
                  class="operation-btn step2"
                  :class="{ 'selected': selectedOperation === 'generateHighlight' }"
                  data-operation="generateHighlight"
                >
                  <el-icon><VideoPlay /></el-icon>
                  Step2: 生成高光视频
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button
                  type="warning"
                  size="large"
                  @click="selectOperation('generateNarration')"
                  class="operation-btn step3"
                  :class="{ 'selected': selectedOperation === 'generateNarration' }"
                  data-operation="generateNarration"
                >
                  <el-icon><Microphone /></el-icon>
                  Step3: 生成视频旁白
                </el-button>
              </el-col>
              <el-col :span="6">
                <el-button
                  type="danger"
                  size="large"
                  @click="selectOperation('generateNarrationVideo')"
                  class="operation-btn step4"
                  :class="{ 'selected': selectedOperation === 'generateNarrationVideo' }"
                  data-operation="generateNarrationVideo"
                >
                  <el-icon><Film /></el-icon>
                  Step4: 合成旁白视频
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- Operation Parameters Section -->
          <div v-if="selectedOperation" class="operation-params">
            <el-divider content-position="center">
              <el-tag type="primary" size="large">{{ getOperationTitle(selectedOperation) }} - 参数配置</el-tag>
            </el-divider>

            <!-- Extract Plots Parameters -->
            <div v-if="selectedOperation === 'extractPlots'" class="params-section">
              <div class="param-group">
                <h4 class="group-title">
                  <el-icon><Folder /></el-icon>
                  视频来源 (二选一)
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="24">
                      <el-form-item label="GCS视频地址" class="form-item-enhanced">
                        <el-input
                          v-model="videoGcsLink"
                          :placeholder="uploadedFile ? '' : 'gs://bucket/path/to/video.mp4'"
                          @input="handleGcsLinkChange"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Link /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  
                  <div class="divider-with-text">
                    <span>或</span>
                  </div>
                  
                  <el-row>
                    <el-col :span="24">
                      <el-form-item label="上传本地文件" class="form-item-enhanced">
                        <el-upload
                          ref="uploadRef"
                          class="upload-enhanced"
                          drag
                          :auto-upload="false"
                          :limit="1"
                          accept=".mp4,.mkv,.webm,.mpeg4"
                          :on-change="handleFileChange"
                          :file-list="fileList"
                          :key="uploadKey"
                        >
                          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                          <div class="el-upload__text">
                            将视频文件拖到此处，或<em>点击上传</em>
                          </div>
                          <template #tip>
                            <div class="el-upload__tip">
                              支持 MP4/MKV/WEBM/MPEG4 格式，文件大小限制 10GB
                            </div>
                          </template>
                        </el-upload>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="param-group">
                <h4 class="group-title">
                  <el-icon><User /></el-icon>
                  演员信息
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="24">
                      <el-form-item label="演员信息" class="form-item-enhanced">
                        <el-input
                          v-model="actorsInfo"
                          placeholder="演员姓名及角色信息，如：马小帅的扮演者是姜文"
                          size="large"
                          type="textarea"
                          :rows="2"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="execute-section">
                <el-button
                  type="primary"
                  size="large"
                  :loading="loading.extractPlots"
                  @click="executeExtractPlots"
                  :disabled="!canExtractPlots"
                  class="execute-btn"
                >
                  <el-icon><CaretRight /></el-icon>
                  执行提取剧情
                </el-button>
              </div>
            </div>

            <!-- Generate Highlight Parameters -->
            <div v-if="selectedOperation === 'generateHighlight'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !plotsResult" class="prerequisite-reminder">
                <el-alert
                  title="🎬 请先提取剧情"
                  type="warning"
                  description="需要先完成 Step1: 提取剧情，才能进行高光视频生成。请返回 Step1 上传视频并提取剧情。"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large">
                    <el-icon><Document /></el-icon>
                    返回 Step1: 提取剧情
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><User /></el-icon>
                  高光视频参数
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="高光短片主角" class="form-item-enhanced">
                        <el-input
                          v-model="highlightStarring"
                          placeholder="请输入主角名称"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Avatar /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="高光短片时长" class="form-item-enhanced">
                        <el-input
                          v-model="highlightDuration"
                          placeholder="如：5分钟"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Timer /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="execute-section">
                <el-button
                  type="success"
                  size="large"
                  :loading="loading.generateHighlight"
                  @click="executeGenerateHighlight"
                  :disabled="!canGenerateHighlight"
                  class="execute-btn"
                >
                  <el-icon><CaretRight /></el-icon>
                  执行生成高光视频
                </el-button>
              </div>
            </div>

            <!-- Generate Narration Parameters -->
            <div v-if="selectedOperation === 'generateNarration'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !highlightVideoPath" class="prerequisite-reminder">
                <el-alert
                  title="🎥 请先生成高光视频"
                  type="warning"
                  description="需要先完成 Step2: 生成高光视频，才能进行视频旁白生成。请返回 Step2 生成高光视频。"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large" v-if="!sessionId || !plotsResult">
                    <el-icon><Document /></el-icon>
                    返回 Step1: 提取剧情
                  </el-button>
                  <el-button type="success" @click="selectOperation('generateHighlight')" size="large" v-else>
                    <el-icon><VideoPlay /></el-icon>
                    返回 Step2: 生成高光视频
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><EditPen /></el-icon>
                  角色与风格设定
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="角色设定" class="form-item-enhanced">
                        <el-input
                          v-model="roleSet"
                          type="textarea"
                          :rows="3"
                          placeholder="请描述角色设定，如：将张秋生重新设想为一个超级英雄"
                          size="large"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="影片背景" class="form-item-enhanced">
                        <el-input
                          v-model="narrationMovieBg"
                          type="textarea"
                          :rows="3"
                          placeholder="影片背景信息，如：视频为《有话好好说》关于角色张秋生的剪辑视频"
                          size="large"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="叙述风格" class="form-item-enhanced">
                        <el-input
                          v-model="narrationStyle"
                          placeholder="如：王家卫电影风格"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Brush /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="角色代号" class="form-item-enhanced">
                        <el-input
                          v-model="narrationCharacterNickname"
                          placeholder="角色的称呼方式，如：李保田称之为老李"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Avatar /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item label="选择配音" class="form-item-enhanced">
                        <el-select v-model="voiceSelected" size="large" style="width: 100%">
                          <el-option
                            v-for="voice in voices"
                            :key="voice"
                            :label="voice"
                            :value="voice"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="execute-section">
                <el-button
                  type="warning"
                  size="large"
                  :loading="loading.generateNarration"
                  @click="executeGenerateNarration"
                  :disabled="!canGenerateNarration"
                  class="execute-btn"
                >
                  <el-icon><CaretRight /></el-icon>
                  执行生成视频旁白
                </el-button>
              </div>
            </div>

            <!-- Generate Narration Video Parameters -->
            <div v-if="selectedOperation === 'generateNarrationVideo'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !highlightVideoPath || !narrationResult.length" class="prerequisite-reminder">
                <el-alert
                  title="🎬 请先生成视频旁白"
                  type="warning"
                  description="需要先完成 Step3: 生成视频旁白，才能进行最终视频合成。请返回相应步骤完成前置操作。"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large" v-if="!sessionId || !plotsResult">
                    <el-icon><Document /></el-icon>
                    返回 Step1: 提取剧情
                  </el-button>
                  <el-button type="success" @click="selectOperation('generateHighlight')" size="large" v-else-if="!highlightVideoPath">
                    <el-icon><VideoPlay /></el-icon>
                    返回 Step2: 生成高光视频
                  </el-button>
                  <el-button type="warning" @click="selectOperation('generateNarration')" size="large" v-else>
                    <el-icon><Microphone /></el-icon>
                    返回 Step3: 生成视频旁白
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><Tools /></el-icon>
                  合成配置
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="8">
                      <el-form-item label="选择配音" class="form-item-enhanced">
                        <el-select v-model="voiceSelected" size="large" style="width: 100%">
                          <el-option
                            v-for="voice in voices"
                            :key="voice"
                            :label="voice"
                            :value="voice"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="MiniMax API Key" class="form-item-enhanced">
                        <el-input
                          v-model="minimaxApiKey"
                          placeholder="API Key (可选)"
                          show-password
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Key /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="MiniMax Group ID" class="form-item-enhanced">
                        <el-input
                          v-model="minimaxGroupId"
                          placeholder="Group ID (可选)"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Key /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="execute-section">
                <el-button
                  type="danger"
                  size="large"
                  :loading="loading.generateNarrationVideo"
                  @click="executeGenerateNarrationVideo"
                  :disabled="!canGenerateNarrationVideo"
                  class="execute-btn"
                >
                  <el-icon><CaretRight /></el-icon>
                  执行合成旁白视频
                </el-button>
              </div>
            </div>
          </div>

        </el-card>

        <!-- Results Section -->
        <div class="results-section" v-if="plotsResult || highlightVideoPath || narrationResult.length || finalVideoPath">
          <el-card class="section-card results-overview-card" shadow="hover">
            <template #header>
              <div class="section-header-simple">
                <el-icon class="section-icon"><Operation /></el-icon>
                <span class="section-title-simple">处理结果</span>
                <el-tag type="success" size="small">点击卡片查看详情</el-tag>
              </div>
            </template>

            <el-row :gutter="20" class="results-grid">
              <!-- Plot Results -->
              <el-col :xl="6" :lg="6" :md="12" :sm="24" :xs="24">
                <div class="result-item-card" :class="{ 'has-content': plotsResult }" @click="plotsResult && togglePlotsModal()">
                  <div class="result-item-header">
                    <el-icon class="result-item-icon"><Document /></el-icon>
                    <h4 class="result-item-title">剧情提取结果</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="plotsResult" class="result-summary">
                      <el-tag type="success" size="small">已完成</el-tag>
                      <el-button type="primary" link @click="togglePlotsModal()">点击查看详情</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="primary" @click.stop="selectOperationAndScroll('extractPlots')">
                          <el-icon><Refresh /></el-icon>
                          重新生成
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>等待剧情提取...</p>
                      <div class="action-buttons">
                        <el-button size="small" type="primary" @click.stop="selectOperationAndScroll('extractPlots')">
                          <el-icon><CaretRight /></el-icon>
                          去生成
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>

              <!-- Highlight Video -->
              <el-col :xl="6" :lg="6" :md="12" :sm="24" :xs="24">
                <div class="result-item-card" :class="{ 'has-content': highlightVideoPath }" @click="highlightVideoPath && toggleHighlightVideoModal()">
                  <div class="result-item-header">
                    <el-icon class="result-item-icon"><VideoPlay /></el-icon>
                    <h4 class="result-item-title">高光视频</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="highlightVideoPath" class="result-summary">
                      <el-tag type="success" size="small">已完成</el-tag>
                      <div class="video-thumbnail">
                        <video 
                          :key="`thumb-highlight-${sessionId}-${highlightVideoPath}`"
                          style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px;"
                          preload="metadata"
                          muted
                        >
                          <source :src="highlightVideoUrl" type="video/mp4">
                        </video>
                      </div>
                      <el-button type="primary" link @click="toggleHighlightVideoModal()">点击播放视频</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="success" @click.stop="selectOperationAndScroll('generateHighlight')">
                          <el-icon><Refresh /></el-icon>
                          重新生成
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>等待高光视频生成...</p>
                      <div class="action-buttons">
                        <el-button size="small" type="success" @click.stop="selectOperationAndScroll('generateHighlight')">
                          <el-icon><CaretRight /></el-icon>
                          去生成
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>

              <!-- Narration Content -->
              <el-col :xl="6" :lg="6" :md="12" :sm="24" :xs="24">
                <div class="result-item-card" :class="{ 'has-content': narrationResult.length }" @click="narrationResult.length && toggleNarrationModal()">
                  <div class="result-item-header">
                    <el-icon class="result-item-icon"><ChatLineRound /></el-icon>
                    <h4 class="result-item-title">旁白内容</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="narrationResult.length" class="result-summary">
                      <el-tag type="success" size="small">已完成</el-tag>
                      <p class="summary-text">已生成 {{ narrationResult.length }} 段旁白</p>
                      <div class="narration-preview">
                        <p class="preview-text">{{ narrationResult[0]?.narration?.substring(0, 50) }}...</p>
                      </div>
                      <el-button type="primary" link>点击查看详情</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="warning" @click.stop="selectOperationAndScroll('generateNarration')">
                          <el-icon><Refresh /></el-icon>
                          重新生成
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>等待旁白生成...</p>
                      <div class="action-buttons">
                        <el-button size="small" type="warning" @click.stop="selectOperationAndScroll('generateNarration')">
                          <el-icon><CaretRight /></el-icon>
                          去生成
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>

              <!-- Final Video -->
              <el-col :xl="6" :lg="6" :md="12" :sm="24" :xs="24">
                <div class="result-item-card" :class="{ 'has-content': finalVideoPath }" @click="finalVideoPath && toggleFinalVideoModal()">
                  <div class="result-item-header">
                    <el-icon class="result-item-icon"><Film /></el-icon>
                    <h4 class="result-item-title">最终合成视频</h4>
                  </div>
                  <div class="result-item-content">
              <div v-if="finalVideoPath" class="result-summary">
                <el-tag type="success" size="small">已完成</el-tag>
                <div class="video-thumbnail">
                  <video 
                    :key="`thumb-final-${sessionId}-${finalVideoPath}`"
                    style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px;"
                    preload="metadata"
                    muted
                  >
                    <source :src="finalVideoUrl" type="video/mp4">
                  </video>
                </div>
                <el-button type="primary" link>点击播放视频</el-button>
                <div class="action-buttons">
                  <el-button size="small" type="danger" @click.stop="selectOperationAndScroll('generateNarrationVideo')">
                    <el-icon><Refresh /></el-icon>
                    重新生成
                  </el-button>
                </div>
              </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>等待最终视频合成...</p>
                      <div class="action-buttons">
                        <el-button size="small" type="danger" @click.stop="selectOperationAndScroll('generateNarrationVideo')">
                          <el-icon><CaretRight /></el-icon>
                          去生成
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <!-- Detail Modals -->
        <!-- Plots Detail Modal -->
        <el-dialog v-model="plotsModalVisible" title="剧情提取结果" width="80%" draggable>
          <div class="plots-modal-content">
            <el-collapse v-model="activePlotsCollapse">
              <el-collapse-item
                v-for="(plot, index) in plotsResult"
                :key="index"
                :title="`片段 ${index + 1}`"
                :name="index.toString()"
              >
                <div class="plot-text">{{ plot }}</div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-dialog>

        <!-- Highlight Video Modal -->
        <el-dialog v-model="highlightVideoModalVisible" title="高光视频" width="80%" draggable>
          <div class="video-modal-content">
            <video 
              v-if="highlightVideoPath"
              :key="`modal-highlight-${sessionId}-${highlightVideoPath}`"
              controls 
              style="width: 100%; max-height: 500px;"
              preload="metadata"
              @loadstart="() => console.log('Highlight video loading started')"
              @canplay="() => console.log('Highlight video can start playing')"
            >
              <source :src="highlightVideoUrl" type="video/mp4">
              您的浏览器不支持视频播放。
            </video>
            <div class="video-modal-actions">
              <el-button type="primary" @click="downloadVideo('highlight')">
                <el-icon><Download /></el-icon>
                下载高光视频
              </el-button>
            </div>
          </div>
        </el-dialog>

        <!-- Narration Detail Modal -->
        <el-dialog v-model="narrationModalVisible" title="旁白内容" width="80%" draggable>
          <div class="narration-modal-content">
            <el-table :data="narrationResult" stripe style="width: 100%" max-height="400">
              <el-table-column prop="timestamp" label="时间戳" width="150" />
              <el-table-column prop="narration_relative_time" label="相对时间(s)" width="120" />
              <el-table-column prop="narration" label="旁白内容" />
            </el-table>
          </div>
        </el-dialog>

        <!-- Final Video Modal -->
        <el-dialog v-model="finalVideoModalVisible" title="最终合成视频" width="80%" draggable>
          <div class="video-modal-content">
            <video 
              v-if="finalVideoPath"
              :key="`modal-final-${sessionId}-${finalVideoPath}`"
              controls 
              style="width: 100%; max-height: 500px;"
              preload="metadata"
              @loadstart="() => console.log('Final video loading started')"
              @canplay="() => console.log('Final video can start playing')"
            >
              <source :src="finalVideoUrl" type="video/mp4" />
              您的浏览器不支持视频播放。
            </video>
            <div class="video-modal-actions">
              <el-button type="primary" @click="downloadVideo('narration')">
                <el-icon><Download /></el-icon>
                下载最终视频
              </el-button>
            </div>
          </div>
        </el-dialog>

        <!-- Error Messages -->
        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          show-icon
          :closable="true"
          @close="errorMessage = ''"
          class="error-alert"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import {
  VideoCamera, Guide, Setting, Operation, Document, VideoPlay,
  Microphone, Film, Download, ChatLineRound, UploadFilled,
  Folder, Link, User, Avatar, Timer, EditPen, Brush, Tools, Key, Loading, CaretRight, Cpu, Refresh
} from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    VideoCamera, Guide, Setting, Operation, Document, VideoPlay,
    Microphone, Film, Download, ChatLineRound, UploadFilled,
    Folder, Link, User, Avatar, Timer, EditPen, Brush, Tools, Key, Cpu
  },
  setup() {
    // Reactive data
    const models = ref([])
    const voices = ref([])
    const selectedModel = ref('')
    const selectedOperation = ref('')
    const videoGcsLink = ref('gs://gemini-oolongz/movie-demo/yhhhs.1.mp4')
    const actorsInfo = ref('马小帅的扮演者是姜文，张秋生的扮演者是李保田')
    const highlightStarring = ref('李保田')
    const highlightDuration = ref('5分钟')
    const roleSet = ref('将张秋生（由李保田饰演）重新设想为一个超级英雄')
    const narrationStyle = ref('王家卫电影')
    const narrationCharacterNickname = ref('李保田称之为老李')
    const narrationMovieBg = ref('视频为《有话好好说》关于角色张秋生的剪辑视频，请参考此背景以及人物的设定')
    const narrationTypeSelected = ref('第三人称叙事')
    const voiceSelected = ref('')
    const minimaxApiKey = ref('')
    const minimaxGroupId = ref('')

    const fileList = ref([])
    const uploadedFile = ref(null)
    const uploadRef = ref(null)
    const uploadKey = ref(0)
    const activeCollapse = ref(['video-params', 'narration-params'])
    const activePlotsCollapse = ref([])

    // Session and results
    const sessionId = ref('')
    const plotsResult = ref(null)
    const highlightVideoPath = ref('')
    const finalVideoPath = ref('')
    const narrationResult = ref([])
    const segmentsResult = ref([])

    // Loading states
    const loading = reactive({
      extractPlots: false,
      generateHighlight: false,
      generateNarration: false,
      generateNarrationVideo: false
    })

    const currentStep = ref(0)
    const errorMessage = ref('')
    
    // Modal states
    const plotsModalVisible = ref(false)
    const highlightVideoModalVisible = ref(false)
    const narrationModalVisible = ref(false)
    const finalVideoModalVisible = ref(false)

    // Computed properties
    const canExtractPlots = computed(() => {
      return selectedModel.value && (videoGcsLink.value || uploadedFile.value)
    })

    const canGenerateHighlight = computed(() => {
      return sessionId.value && selectedModel.value && (videoGcsLink.value || uploadedFile.value) && highlightDuration.value.trim()
    })

    const canGenerateNarration = computed(() => {
      return sessionId.value && highlightVideoPath.value && 
             roleSet.value && narrationStyle.value && narrationCharacterNickname.value && 
             voiceSelected.value && narrationTypeSelected.value
    })

    const canGenerateNarrationVideo = computed(() => {
      return canGenerateNarration.value && narrationResult.value.length > 0
    })

    const highlightVideoGenerated = computed(() => {
      return sessionId.value && highlightVideoPath.value
    })

    const narrationGenerated = computed(() => {
      return highlightVideoGenerated.value && narrationResult.value.length > 0
    })

    const highlightVideoUrl = computed(() => {
      return highlightVideoPath.value ? `/api/download/${sessionId.value}/highlight_video` : ''
    })

    const finalVideoUrl = computed(() => {
      return finalVideoPath.value ? `/api/download/${sessionId.value}/narration_video` : ''
    })

    // Methods
    const loadConfig = async () => {
      try {
        console.log('Loading config from backend...')
        const response = await axios.get('/config')
        console.log('Config response:', response.data)
        
        if (response.data && response.data.models && response.data.voices) {
          models.value = response.data.models
          voices.value = response.data.voices
          
          if (models.value.length > 0) {
            selectedModel.value = models.value[0]
            console.log('Auto-selected model:', selectedModel.value)
          }
          if (voices.value.length > 2) {
            voiceSelected.value = voices.value[2]
          } else if (voices.value.length > 0) {
            voiceSelected.value = voices.value[0]
          }
          
          console.log('Config loaded successfully:', {
            models: models.value,
            voices: voices.value
          })
        } else {
          throw new Error('Invalid config response format')
        }
      } catch (error) {
        console.error('Failed to load config:', error)
        // 设置默认值以防后端连接失败
        models.value = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
        voices.value = ['google_AliceSample', 'minimax_Alex', 'google_BethSample']
        selectedModel.value = models.value[0]
        voiceSelected.value = voices.value[0]
        console.log('Using fallback model:', selectedModel.value)
        
        if (error.response) {
          errorMessage.value = `配置加载失败: ${error.response.status} ${error.response.statusText}`
        } else if (error.request) {
          errorMessage.value = '无法连接到后端服务，请确保后端服务已启动'
        } else {
          errorMessage.value = `配置加载失败: ${error.message}`
        }
      }
    }

    const handleFileChange = (file) => {
      console.log('File uploaded, clearing GCS link')
      uploadedFile.value = file.raw
      fileList.value = [file]  // Keep file in the list for display
      videoGcsLink.value = ''  // Clear GCS link when file is uploaded
    }

    const handleGcsLinkChange = () => {
      console.log('GCS link changed, clearing uploaded file only if there is actually a GCS link')
      if (videoGcsLink.value && videoGcsLink.value.trim()) {
        // Only clear uploaded file if user actually provides a GCS link
        uploadedFile.value = null
        fileList.value = []
        // Force refresh the upload component by clearing its internal state
        if (uploadRef.value) {
          uploadRef.value.clearFiles()
        }
      }
    }

    const clearVideoFile = () => {
      // Clear all video file sources
      uploadedFile.value = null
      fileList.value = []
      videoGcsLink.value = ''
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
    }

    const resetAllStates = () => {
      // Reset all states when starting a completely new workflow
      sessionId.value = ''
      plotsResult.value = null
      highlightVideoPath.value = ''
      finalVideoPath.value = ''
      narrationResult.value = []
      segmentsResult.value = []
      currentStep.value = 0
      errorMessage.value = ''
    }

    const extractPlots = async () => {
      if (!canExtractPlots.value) {
        errorMessage.value = '请填写必要的参数'
        return
      }

      // Only clear workflow results, keep file info intact
      resetAllStates()

      loading.extractPlots = true
      try {
        const formData = new FormData()
        if (uploadedFile.value) {
          formData.append('video_file', uploadedFile.value)
        } else {
          formData.append('video_gcs_link', videoGcsLink.value)
        }
        formData.append('actors_info', actorsInfo.value)
        formData.append('model', selectedModel.value)

        const response = await axios.post('/api/extract-plots', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          sessionId.value = response.data.session_id
          plotsResult.value = response.data.data.plots
          currentStep.value = 1
          errorMessage.value = ''
        } else {
          errorMessage.value = response.data.message
        }
      } catch (error) {
        console.error('Extract plots failed:', error)
        errorMessage.value = error.response?.data?.detail || '提取剧情失败'
      } finally {
        loading.extractPlots = false
      }
    }

    const generateHighlight = async () => {
      if (!sessionId.value) {
        errorMessage.value = '请先执行提取剧情'
        return
      }

      // Clear previous highlight and narration results
      highlightVideoPath.value = ''
      finalVideoPath.value = ''
      narrationResult.value = []
      segmentsResult.value = []
      if (currentStep.value > 2) {
        currentStep.value = 1
      }
      errorMessage.value = ''

      loading.generateHighlight = true
      try {
        const response = await axios.post('/api/generate-highlight', {
          session_id: sessionId.value,
          highlight_starring: highlightStarring.value,
          highlight_duration: highlightDuration.value
        })

        if (response.data.success) {
          highlightVideoPath.value = response.data.data.highlight_video_path
          segmentsResult.value = response.data.data.segments
          currentStep.value = 2
          errorMessage.value = ''
        } else {
          errorMessage.value = response.data.message
        }
      } catch (error) {
        console.error('Generate highlight failed:', error)
        errorMessage.value = error.response?.data?.detail || '生成高光视频失败'
      } finally {
        loading.generateHighlight = false
      }
    }

    const generateNarration = async () => {
      if (!highlightVideoGenerated.value) {
        errorMessage.value = '请先生成高光视频'
        return
      }

      // Clear previous narration results
      narrationResult.value = []
      finalVideoPath.value = ''
      if (currentStep.value > 3) {
        currentStep.value = 2
      }
      errorMessage.value = ''

      loading.generateNarration = true
      try {
        const response = await axios.post('/api/generate-narration', {
          session_id: sessionId.value,
          role_set: roleSet.value,
          narration_style: narrationStyle.value,
          narration_character_nickname: narrationCharacterNickname.value,
          voice_selected: voiceSelected.value,
          narration_type_selected: narrationTypeSelected.value
        })

        if (response.data.success) {
          narrationResult.value = response.data.data.narration
          currentStep.value = 3
          errorMessage.value = ''
        } else {
          errorMessage.value = response.data.message
        }
      } catch (error) {
        console.error('Generate narration failed:', error)
        errorMessage.value = error.response?.data?.detail || '生成视频旁白失败'
      } finally {
        loading.generateNarration = false
      }
    }

    const generateNarrationVideo = async () => {
      if (!narrationGenerated.value) {
        errorMessage.value = '请先生成视频旁白'
        return
      }

      // Clear previous final video results
      finalVideoPath.value = ''
      if (currentStep.value > 4) {
        currentStep.value = 3
      }
      errorMessage.value = ''

      loading.generateNarrationVideo = true
      try {
        const response = await axios.post('/api/generate-narration-video', {
          session_id: sessionId.value,
          voice_selected: voiceSelected.value
        })

        if (response.data.success) {
          finalVideoPath.value = response.data.data.final_video_path
          currentStep.value = 4
          errorMessage.value = ''
        } else {
          errorMessage.value = response.data.message
        }
      } catch (error) {
        console.error('Generate narration video failed:', error)
        errorMessage.value = error.response?.data?.detail || '合成旁白视频失败'
      } finally {
        loading.generateNarrationVideo = false
      }
    }

    const downloadVideo = (type) => {
      const url = type === 'highlight' ? highlightVideoUrl.value : finalVideoUrl.value
      window.open(url, '_blank')
    }

    // Modal toggle functions
    const togglePlotsModal = () => {
      plotsModalVisible.value = true
    }

    const toggleHighlightVideoModal = () => {
      highlightVideoModalVisible.value = true
    }

    const toggleNarrationModal = () => {
      narrationModalVisible.value = true
    }

    const toggleFinalVideoModal = () => {
      finalVideoModalVisible.value = true
    }

    // New UI interaction functions
    const selectOperation = (operation) => {
      selectedOperation.value = operation
    }

    const selectOperationAndScroll = (operation) => {
      selectedOperation.value = operation
      // Scroll to the operation button
      nextTick(() => {
        const operationButton = document.querySelector(`[data-operation="${operation}"]`)
        if (operationButton) {
          operationButton.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          })
        }
      })
    }

    const getOperationTitle = (operation) => {
      const titles = {
        extractPlots: 'Step1: 提取剧情',
        generateHighlight: 'Step2: 生成高光视频',
        generateNarration: 'Step3: 生成视频旁白',
        generateNarrationVideo: 'Step4: 合成旁白视频'
      }
      return titles[operation] || ''
    }

    // Execute wrapper functions for new UI pattern
    const executeExtractPlots = () => {
      extractPlots()
    }

    const executeGenerateHighlight = () => {
      generateHighlight()
    }

    const executeGenerateNarration = () => {
      generateNarration()
    }

    const executeGenerateNarrationVideo = () => {
      generateNarrationVideo()
    }

    // Lifecycle
    onMounted(() => {
      loadConfig()
    })

    return {
      // Data
      models, voices, selectedModel, selectedOperation, videoGcsLink, actorsInfo, highlightStarring,
      highlightDuration, roleSet, narrationStyle, narrationCharacterNickname,
      narrationMovieBg, narrationTypeSelected, voiceSelected, minimaxApiKey, minimaxGroupId,
      fileList, uploadedFile, activeCollapse, activePlotsCollapse,
      sessionId, plotsResult, highlightVideoPath, finalVideoPath, narrationResult,
      segmentsResult, loading, currentStep, errorMessage,
      
      // Modal states
      plotsModalVisible, highlightVideoModalVisible, narrationModalVisible, finalVideoModalVisible,

      // Computed
      canExtractPlots, canGenerateHighlight, canGenerateNarration, canGenerateNarrationVideo,
      highlightVideoGenerated, narrationGenerated, highlightVideoUrl, finalVideoUrl,

      // Methods
      handleFileChange, handleGcsLinkChange, clearVideoFile, extractPlots, generateHighlight,
      generateNarration, generateNarrationVideo, downloadVideo,
      togglePlotsModal, toggleHighlightVideoModal, toggleNarrationModal, toggleFinalVideoModal,
      
      // New UI interaction methods
      selectOperation, selectOperationAndScroll, getOperationTitle, executeExtractPlots, executeGenerateHighlight,
      executeGenerateNarration, executeGenerateNarrationVideo,
      
      // Refs
      uploadRef, uploadKey
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(180deg, 
    #87CEEB 0%, 
    #87CEEB 60%, 
    #228B22 60%, 
    #228B22 80%, 
    #8B4513 80%);
  position: relative;
  overflow-x: hidden;
}

.app-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20px 20px, #FFFFFF 2px, transparent 2px),
    radial-gradient(circle at 80px 80px, #FFFF00 3px, transparent 3px),
    radial-gradient(circle at 140px 140px, #FFFFFF 2px, transparent 2px);
  background-size: 200px 200px, 160px 160px, 180px 180px;
  background-position: 0 0, 40px 40px, 80px 80px;
  opacity: 0.3;
  pointer-events: none;
  z-index: 0;
}

.app-header {
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.app-title .el-icon {
  color: #4299e1;
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.main-title-section {
  margin-bottom: 40px;
  padding: 20px 0;
}

.title-content {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

.main-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-align: left;
}

.model-info-inline {
  font-size: 16px;
  font-weight: 600;
  color: #4f46e5 !important;
  opacity: 1;
  margin-left: 12px;
  background: none !important;
  -webkit-background-clip: initial !important;
  -webkit-text-fill-color: #4f46e5 !important;
  text-shadow: none !important;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(79, 70, 229, 0.1) !important;
  border: 1px solid rgba(79, 70, 229, 0.2);
}

.content-area {
  width: 100%;
}

.model-selection-section {
  padding: 24px;
  background: #f7fafc;
  border-radius: 12px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
}

.config-info {
  width: 100%;
}

.config-alert {
  border-radius: 12px;
  border: 1px solid rgba(34, 197, 94, 0.2);
  background: linear-gradient(135deg, rgba(240, 253, 244, 0.9) 0%, rgba(236, 253, 245, 0.8) 100%);
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.1);
  transition: all 0.3s ease;
}

.config-alert:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.15);
}

.config-alert :deep(.el-alert__icon) {
  color: #059669;
  font-size: 20px;
}

.config-alert :deep(.el-alert__title) {
  color: #065f46;
  font-weight: 600;
}

.config-alert :deep(.el-alert__description) {
  color: #047857;
}

.model-info-section {
  margin-top: 32px;
  padding: 16px 0;
}

.model-info-section .el-divider {
  margin: 16px 0;
}

.model-info-section .el-divider__text {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 20px;
  padding: 12px 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);
  transition: all 0.3s ease;
}

.model-info-section .el-divider__text:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15);
}

.model-info-section .el-tag {
  font-size: 14px;
  font-weight: 600;
  color: #4c1d95;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  padding: 8px 16px;
  height: auto;
  line-height: 1.4;
}

.model-info-section .el-tag .el-icon {
  margin-right: 6px;
  color: #6366f1;
}

.section-card {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #FFE5B4 0%, #FFCCCB 100%);
  border: 6px solid #000000;
  box-shadow: 
    inset 0 0 0 4px #FFFFFF,
    0 8px 0 #000000,
    0 12px 24px rgba(0, 0, 0, 0.4);
  border-radius: 24px;
  overflow: hidden;
  position: relative;
  font-family: 'Courier New', monospace;
}

.section-card::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  border: 2px dashed #FF0000;
  border-radius: 16px;
  pointer-events: none;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  font-weight: bold;
  font-size: 18px;
  background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #FFD93D 100%);
  color: #FFFFFF;
  text-shadow: 2px 2px 0 #000000;
  padding: 4px 8px;
  border-radius: 8px;
  margin: -4px;
  position: relative;
  z-index: 1;
}

.section-header .section-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-model-info {
  margin-left: auto;
}

.header-model-info .el-tag {
  font-size: 13px;
  font-weight: bold;
  color: #000000;
  background: linear-gradient(45deg, #FFD700 0%, #FFA500 100%);
  border: 3px solid #000000;
  padding: 8px 16px;
  height: auto;
  line-height: 1.2;
  border-radius: 20px;
  transition: all 0.2s ease-out;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  box-shadow: 0 4px 0 #B8860B, 0 6px 12px rgba(0, 0, 0, 0.3);
}


.header-model-info .el-tag .el-icon {
  margin-right: 4px;
  color: #FF0000;
  filter: drop-shadow(1px 1px 0 #FFFFFF);
}

.section-icon {
  font-size: 24px;
  color: #FFD700;
  filter: drop-shadow(2px 2px 0 #000000);
}

.section-header-simple {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  text-shadow: none;
  padding: 8px 0;
  background: none;
  border: none;
}

.section-title-simple {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  text-shadow: none;
}

.params-grid {
  padding: 20px 0;
}

.operations-grid {
  padding: 20px;
}

.operation-btn {
  width: 100%;
  height: 72px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
  backdrop-filter: blur(10px);
}

.operation-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.operation-btn:hover:not(:disabled) {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.operation-btn:hover:not(:disabled)::before {
  left: 100%;
}

.operation-btn:active:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
}

.operation-btn.step1 {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border: 4px solid #000000;
  color: #000000;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  font-weight: 900;
  text-shadow: 1px 1px 0 #FFFFFF;
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 4px 0 #B8860B,
    0 6px 12px rgba(0, 0, 0, 0.3);
  position: relative;
}

.operation-btn.step1::before {
  content: '🎬';
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 20px;
  animation: coinSpin 2s linear infinite;
}

.operation-btn.step1:hover:not(:disabled) {
  background: linear-gradient(135deg, #FFFF00 0%, #FFD700 100%);
  transform: translateY(-6px) scale(1.03);
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 6px 0 #B8860B,
    0 8px 16px rgba(0, 0, 0, 0.4);
  animation: powerUpBounce 0.3s ease-out;
}

.operation-btn.step2 {
  background: linear-gradient(135deg, #32CD32 0%, #228B22 100%);
  border: 4px solid #000000;
  color: #FFFFFF;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  font-weight: 900;
  text-shadow: 2px 2px 0 #000000;
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 4px 0 #006400,
    0 6px 12px rgba(0, 0, 0, 0.3);
  position: relative;
}

.operation-btn.step2::before {
  content: '🍄';
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 20px;
  animation: mushroomBounce 1.5s ease-in-out infinite;
}

.operation-btn.step2:hover:not(:disabled) {
  background: linear-gradient(135deg, #00FF00 0%, #32CD32 100%);
  transform: translateY(-6px) scale(1.03);
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 6px 0 #006400,
    0 8px 16px rgba(0, 0, 0, 0.4);
  animation: powerUpBounce 0.3s ease-out;
}

.operation-btn.step3 {
  background: linear-gradient(135deg, #FF4500 0%, #FF0000 100%);
  border: 4px solid #000000;
  color: #FFFFFF;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  font-weight: 900;
  text-shadow: 2px 2px 0 #000000;
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 4px 0 #8B0000,
    0 6px 12px rgba(0, 0, 0, 0.3);
  position: relative;
}

.operation-btn.step3::before {
  content: '🌟';
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 20px;
  animation: starTwinkle 1s ease-in-out infinite alternate;
}

.operation-btn.step3:hover:not(:disabled) {
  background: linear-gradient(135deg, #FF6347 0%, #FF4500 100%);
  transform: translateY(-6px) scale(1.03);
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 6px 0 #8B0000,
    0 8px 16px rgba(0, 0, 0, 0.4);
  animation: powerUpBounce 0.3s ease-out;
}

.operation-btn.step4 {
  background: linear-gradient(135deg, #8A2BE2 0%, #4B0082 100%);
  border: 4px solid #000000;
  color: #FFFFFF;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  font-weight: 900;
  text-shadow: 2px 2px 0 #000000;
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 4px 0 #2F004F,
    0 6px 12px rgba(0, 0, 0, 0.3);
  position: relative;
}

.operation-btn.step4::before {
  content: '👑';
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 20px;
  animation: crownFloat 2s ease-in-out infinite;
}

.operation-btn.step4:hover:not(:disabled) {
  background: linear-gradient(135deg, #9932CC 0%, #8A2BE2 100%);
  transform: translateY(-6px) scale(1.03);
  box-shadow: 
    inset 0 0 0 2px #FFFFFF,
    0 6px 0 #2F004F,
    0 8px 16px rgba(0, 0, 0, 0.4);
  animation: powerUpBounce 0.3s ease-out;
}

@keyframes coinSpin {
  0% { transform: rotateY(0deg); }
  100% { transform: rotateY(360deg); }
}

@keyframes mushroomBounce {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}

@keyframes starTwinkle {
  0% { transform: scale(1) rotate(0deg); opacity: 1; }
  100% { transform: scale(1.2) rotate(180deg); opacity: 0.7; }
}

@keyframes crownFloat {
  0%, 100% { transform: translateY(0px) rotate(-5deg); }
  50% { transform: translateY(-4px) rotate(5deg); }
}

@keyframes powerUpBounce {
  0%, 100% { transform: translateY(-6px) scale(1.03); }
  50% { transform: translateY(-10px) scale(1.05); }
}

.operation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Selected operation button styling */
.operation-btn.selected {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.operation-btn.step1.selected {
  background: #4c51bf !important;
  color: white !important;
  box-shadow: 0 8px 32px rgba(76, 81, 191, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
}

.operation-btn.step2.selected {
  background: #ed64a6 !important;
  color: white !important;
  box-shadow: 0 8px 32px rgba(237, 100, 166, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
}

.operation-btn.step3.selected {
  background: #4299e1 !important;
  color: white !important;
  box-shadow: 0 8px 32px rgba(66, 153, 225, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
}

.operation-btn.step4.selected {
  background: #48bb78 !important;
  color: white !important;
  box-shadow: 0 8px 32px rgba(72, 187, 120, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
}

/* Operation parameters section styling */
.operation-params {
  margin-top: 24px;
  opacity: 0;
  animation: slideInFromTop 0.6s ease-out forwards;
}

@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.operation-params .el-divider {
  margin: 24px 0;
}

.operation-params .el-divider__text {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 12px 24px;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.operation-params .params-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(15px);
  transition: all 0.3s ease;
}

.operation-params .params-section:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* Execute section styling */
.execute-section {
  margin-top: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(249, 250, 251, 0.9) 0%, rgba(243, 244, 246, 0.8) 100%);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  text-align: center;
  transition: all 0.3s ease;
}

.execute-section:hover {
  background: linear-gradient(135deg, rgba(247, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.9) 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.execute-btn {
  min-width: 200px;
  height: 56px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.execute-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.execute-btn:hover:not(:disabled)::before {
  left: 100%;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.execute-btn:active:not(:disabled) {
  transform: translateY(-1px) scale(1.02);
}

.execute-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Enhanced parameter group animations */
.param-group {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

.param-group:nth-child(1) {
  animation-delay: 0.1s;
}

.param-group:nth-child(2) {
  animation-delay: 0.2s;
}

.param-group:nth-child(3) {
  animation-delay: 0.3s;
}

.param-group:nth-child(4) {
  animation-delay: 0.4s;
}

.results-section {
  margin-top: 30px;
}

.result-card {
  margin-bottom: 24px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.result-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.plots-content {
  max-height: 400px;
  overflow-y: auto;
}

.plot-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #444;
}

.video-container {
  text-align: center;
}

.video-actions {
  margin-top: 15px;
}

.narration-content {
  max-height: 500px;
  overflow-y: auto;
}

.error-alert {
  margin-top: 20px;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:deep(.el-upload-dragger::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent 0%, rgba(64, 158, 255, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
}

:deep(.el-upload-dragger:hover::before) {
  opacity: 1;
}

:deep(.el-steps--vertical .el-step__main) {
  padding-left: 16px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
}

:deep(.el-card__header) {
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

/* Enhanced Parameter Settings Styles */
.params-collapse {
  background: transparent;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 16px;
}

.collapse-icon {
  font-size: 18px;
  color: #409eff;
}

.params-section {
  padding: 24px 16px;
  background: rgba(249, 250, 251, 0.8);
  border-radius: 8px;
  margin-top: 16px;
}

.param-group {
  margin-bottom: 32px;
}

.param-group:last-child {
  margin-bottom: 0;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.group-content {
  padding: 0 16px;
}

.form-item-enhanced {
  margin-bottom: 20px;
}

.form-item-enhanced :deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-item-enhanced :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(5px);
}

.form-item-enhanced :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
  border-color: #409eff;
}

.form-item-enhanced :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(5px);
  background: rgba(255, 255, 255, 0.9);
}

.form-item-enhanced :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.upload-enhanced {
  width: 100%;
}

.upload-enhanced :deep(.el-upload-dragger) {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 48px 24px;
  position: relative;
  overflow: hidden;
}

.upload-enhanced :deep(.el-icon--upload) {
  font-size: 56px;
  color: #409eff;
  margin-bottom: 20px;
}

.upload-enhanced :deep(.el-upload__text) {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
}

.upload-enhanced :deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
  font-weight: 600;
}

.upload-enhanced :deep(.el-upload__tip) {
  color: #909399;
  font-size: 13px;
  margin-top: 12px;
}

.divider-with-text {
  position: relative;
  text-align: center;
  margin: 24px 0;
}

.divider-with-text::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e5e7eb 20%, #e5e7eb 80%, transparent 100%);
}

.divider-with-text span {
  display: inline-block;
  padding: 8px 24px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}


:deep(.el-collapse-item__header) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  margin-bottom: 12px;
  padding: 0 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

:deep(.el-collapse-item__header::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.1), transparent);
  transition: left 0.6s;
}


:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}


:deep(.el-select-dropdown) {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.95);
}


/* Loading states */
.operation-btn[loading] {
  position: relative;
  overflow: hidden;
}

.operation-btn[loading]::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: loading-shimmer 1.5s infinite;
}

@keyframes loading-shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Enhanced responsive design */
@media (min-width: 1920px) {
  .main-container {
    max-width: 1800px;
    padding: 60px 40px;
  }
  
  .header-content {
    max-width: 2000px;
    padding: 0 40px;
  }
  
  .operation-btn {
    height: 80px;
    font-size: 18px;
  }
  
  .app-title {
    font-size: 28px;
  }
}

@media (min-width: 1200px) and (max-width: 1919px) {
  .main-container {
    max-width: 1400px;
    padding: 50px 30px;
  }
  
  .operation-btn {
    height: 76px;
    font-size: 17px;
  }
}

@media (max-width: 1200px) {
  .main-container {
    max-width: 1000px;
    padding: 40px 20px;
  }
}

@media (max-width: 768px) {
  .main-container {
    padding: 20px 16px;
  }
  
  .operations-grid .el-col {
    margin-bottom: 12px;
  }
  
  .operation-btn {
    height: 64px;
    font-size: 14px;
  }
  
  .app-title {
    font-size: 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .model-selection-section {
    padding: 16px;
  }
}

/* Scroll animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-card {
  animation: fadeInUp 0.6s ease-out;
}

.section-card:nth-child(2) {
  animation-delay: 0.1s;
}

.section-card:nth-child(3) {
  animation-delay: 0.2s;
}

/* Enhanced focus states */
:deep(.el-button:focus-visible) {
  outline: 3px solid rgba(64, 158, 255, 0.5);
  outline-offset: 2px;
}

:deep(.el-input:focus-within .el-input__wrapper) {
  outline: 2px solid rgba(64, 158, 255, 0.5);
  outline-offset: 1px;
}

/* Custom scrollbar */
.plots-content::-webkit-scrollbar,
.narration-content::-webkit-scrollbar {
  width: 8px;
}

.plots-content::-webkit-scrollbar-track,
.narration-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.plots-content::-webkit-scrollbar-thumb,
.narration-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.plots-content::-webkit-scrollbar-thumb:hover,
.narration-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

/* Results Section Styles */
.results-overview-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid rgba(64, 158, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}


.results-grid {
  padding: 24px;
}

.result-item-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%);
  border: 2px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  padding: 20px;
  height: 280px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

.result-item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.08), transparent);
  transition: left 0.6s;
}


.result-item-card.has-content {
  border-color: rgba(34, 197, 94, 0.2);
  background: linear-gradient(135deg, rgba(240, 253, 244, 0.9) 0%, rgba(236, 253, 245, 0.7) 100%);
}


.result-item-card:not(.has-content):hover {
  transform: none;
  box-shadow: none;
}

.result-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.result-item-icon {
  font-size: 24px;
  color: #64748b;
  transition: all 0.3s ease;
}

.result-item-card.has-content .result-item-icon {
  color: #059669;
}

.result-item-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.2;
}

.result-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.result-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.summary-text {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.video-thumbnail {
  width: 100%;
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}


.narration-preview {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  border-left: 3px solid #059669;
}

.preview-text {
  margin: 0;
  font-size: 13px;
  color: #475569;
  font-style: italic;
  line-height: 1.4;
}

.result-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #9ca3af;
}

.placeholder-icon {
  font-size: 32px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.result-placeholder p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

/* Modal Styles */
.plots-modal-content,
.narration-modal-content,
.video-modal-content {
  max-height: 70vh;
  overflow-y: auto;
}

.video-modal-content {
  text-align: center;
}

.video-modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.plots-modal-content .plot-text {
  background: rgba(248, 250, 252, 0.8);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  margin: 8px 0;
}

/* Enhanced responsive design for new layout */
@media (max-width: 1200px) {
  .results-grid {
    padding: 20px;
  }
  
  .result-item-card {
    height: 260px;
    padding: 18px;
  }
}

@media (max-width: 768px) {
  .results-grid {
    padding: 16px;
  }
  
  .result-item-card {
    height: 240px;
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .result-item-title {
    font-size: 15px;
  }
  
  .summary-text {
    font-size: 13px;
  }
  
  .result-item-icon {
    font-size: 20px;
  }
  
  .video-thumbnail {
    margin: 8px 0;
  }
}

@media (max-width: 576px) {
  .result-item-card {
    height: 220px;
    padding: 14px;
  }
  
  .result-item-header {
    margin-bottom: 12px;
    padding-bottom: 8px;
  }
  
  .result-item-title {
    font-size: 14px;
  }
  
  .placeholder-icon {
    font-size: 28px;
  }
}

/* Loading animation for result cards */
.result-item-card.loading {
  position: relative;
  overflow: hidden;
}

.result-item-card.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: loading-sweep 1.5s infinite;
}

@keyframes loading-sweep {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Enhanced dialog styles */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  font-weight: 600;
  color: #1e293b;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__close) {
  font-size: 18px;
  color: #64748b;
  transition: all 0.3s ease;
}

:deep(.el-dialog__close:hover) {
  color: #ef4444;
  transform: scale(1.1);
}

/* Prerequisite Reminder Styles */
.prerequisite-reminder {
  padding: 24px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.8) 0%, rgba(253, 230, 138, 0.6) 100%);
  border: 2px solid rgba(245, 158, 11, 0.2);
  border-radius: 16px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  animation: reminderFadeIn 0.6s ease-out;
}

.prerequisite-reminder::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.8), transparent);
  animation: reminderShimmer 2s infinite;
}

@keyframes reminderFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes reminderShimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.prerequisite-reminder:hover {
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 8px 32px rgba(245, 158, 11, 0.2);
  transform: translateY(-2px);
}

.reminder-alert {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.15);
}

.reminder-alert :deep(.el-alert__icon) {
  font-size: 24px;
  animation: reminderPulse 2s infinite;
}

@keyframes reminderPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.reminder-alert :deep(.el-alert__title) {
  font-size: 16px;
  font-weight: 600;
  color: #92400e;
}

.reminder-alert :deep(.el-alert__description) {
  font-size: 14px;
  color: #a16207;
  line-height: 1.6;
  margin-top: 8px;
}

.reminder-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.reminder-actions .el-button {
  min-width: 180px;
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(5px);
}

.reminder-actions .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.reminder-actions .el-button:hover::before {
  left: 100%;
}

.reminder-actions .el-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.reminder-actions .el-button:active {
  transform: translateY(-1px) scale(1.02);
}

.reminder-actions .el-button[type="primary"] {
  background: linear-gradient(135deg, #4c51bf 0%, #667eea 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(76, 81, 191, 0.3);
}

.reminder-actions .el-button[type="primary"]:hover {
  background: linear-gradient(135deg, #434190 0%, #5a67d8 100%);
  box-shadow: 0 8px 32px rgba(76, 81, 191, 0.4);
}

.reminder-actions .el-button[type="success"] {
  background: linear-gradient(135deg, #48bb78 0%, #68d391 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(72, 187, 120, 0.3);
}

.reminder-actions .el-button[type="success"]:hover {
  background: linear-gradient(135deg, #38a169 0%, #4fd1c7 100%);
  box-shadow: 0 8px 32px rgba(72, 187, 120, 0.4);
}

.reminder-actions .el-button[type="warning"] {
  background: linear-gradient(135deg, #ed8936 0%, #f6ad55 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(237, 137, 54, 0.3);
}

.reminder-actions .el-button[type="warning"]:hover {
  background: linear-gradient(135deg, #dd6b20 0%, #ed8936 100%);
  box-shadow: 0 8px 32px rgba(237, 137, 54, 0.4);
}

/* Enhanced responsive design for main title */
@media (max-width: 768px) {
  .main-title-section {
    margin-bottom: 30px;
    padding: 20px 0;
  }
  
  .title-content {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    text-align: center;
  }
  
  .main-title {
    font-size: 26px;
  }
  
  .model-info-display .el-tag {
    font-size: 14px;
    padding: 10px 20px;
  }
  
  .model-info-display .el-tag .el-icon {
    font-size: 16px;
  }
}

@media (max-width: 576px) {
  .main-title-section {
    margin-bottom: 24px;
    padding: 16px 0;
  }
  
  .title-content {
    flex-direction: column;
    align-items: center;
    gap: 12px;
    text-align: center;
  }
  
  .main-title {
    font-size: 22px;
    letter-spacing: 0.3px;
  }
  
  .model-info-display .el-tag {
    font-size: 13px;
    padding: 8px 16px;
  }
  
  .model-info-display .el-tag .el-icon {
    font-size: 14px;
    margin-right: 6px;
  }
}

/* Enhanced responsive design for reminders */
@media (max-width: 768px) {
  .prerequisite-reminder {
    padding: 20px 16px;
    margin-bottom: 20px;
  }
  
  .reminder-actions {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .reminder-actions .el-button {
    width: 100%;
    max-width: 280px;
    min-width: auto;
    height: 44px;
  }
  
  .reminder-alert :deep(.el-alert__title) {
    font-size: 15px;
  }
  
  .reminder-alert :deep(.el-alert__description) {
    font-size: 13px;
  }
  
  .reminder-alert :deep(.el-alert__icon) {
    font-size: 20px;
  }
}

@media (max-width: 576px) {
  .prerequisite-reminder {
    padding: 16px 12px;
  }
  
  .reminder-actions .el-button {
    height: 40px;
    font-size: 13px;
  }
  
  .reminder-alert :deep(.el-alert__title) {
    font-size: 14px;
  }
  
  .reminder-alert :deep(.el-alert__description) {
    font-size: 12px;
  }
}

/* Accessibility improvements for reminders */
.prerequisite-reminder:focus-within {
  outline: 3px solid rgba(245, 158, 11, 0.5);
  outline-offset: 2px;
}

.reminder-actions .el-button:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.5);
  outline-offset: 2px;
}
</style>
