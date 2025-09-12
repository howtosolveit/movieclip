<template>
  <div class="app-container">
    <!-- Main Content -->
    <div class="main-container">
      <!-- Main Title Section -->
      <div class="main-title-section">
        <div class="title-content">
          <h1 class="main-title mario-title">
            {{ $t('title') }}
            <span v-if="selectedModel" class="model-info-inline mario-power">
              {{ $t('poweredBy', { model: selectedModel }) }}
            </span>
          </h1>
          <div class="title-actions">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
      <!-- Content Area -->
      <div class="content-area">
        <!-- Operations Section -->
        <el-card class="section-card operations-card" shadow="hover">
          <!-- <template #header> -->
            <div class="section-header-unified">
              <div class="header-left">
                <el-icon class="section-icon"><Operation /></el-icon>
                <span class="section-title-main">{{ $t('operationSteps') }}</span>
                <span class="section-subtitle">{{ $t('operationSuggestion') }}</span>
              </div>
            </div>
          <!-- </template> -->

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
                  {{ $t('steps.step1') }}
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
                  {{ $t('steps.step2') }}
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
                  {{ $t('steps.step3') }}
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
                  {{ $t('steps.step4') }}
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- Operation Parameters Section -->
          <div v-if="selectedOperation" class="operation-params">
            <el-divider content-position="center">
              <el-tag type="primary" size="large">{{ $t('paramConfig', { operation: getOperationTitle(selectedOperation) }) }}</el-tag>
            </el-divider>

            <!-- Extract Plots Parameters -->
            <div v-if="selectedOperation === 'extractPlots'" class="params-section">
              <div class="param-group">
                <h4 class="group-title">
                  <el-icon><Folder /></el-icon>
                  {{ $t('extractPlots.videoSource') }}
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item :label="$t('extractPlots.uploadLocalFile')" class="form-item-enhanced">
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
                            {{ $t('extractPlots.dragUpload') }}<em>{{ $t('extractPlots.clickUpload') }}</em>
                          </div>
                          <template #tip>
                            <div class="el-upload__tip">
                              {{ $t('extractPlots.uploadTip') }}
                            </div>
                          </template>
                        </el-upload>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="$t('extractPlots.gcsVideoLink')" class="form-item-enhanced">
                        <el-input
                          v-model="videoGcsLink"
                          :placeholder="uploadedFile ? '' : $t('extractPlots.gcsPlaceholder')"
                          @input="handleGcsLinkChange"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Link /></el-icon>
                          </template>
                        </el-input>
                        <div class="gcs-hint">
                          <el-text size="small" type="info">
                            <el-icon><InfoFilled /></el-icon>
                            {{ $t('extractPlots.gcsHint') }}
                          </el-text>
                        </div>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <div class="param-group">
                <h4 class="group-title">
                  <el-icon><User /></el-icon>
                  {{ $t('extractPlots.actorsInfo') }}
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="24">
                      <el-form-item :label="$t('extractPlots.actorsInfo')" class="form-item-enhanced">
                        <el-input
                          v-model="actorsInfo"
                          :placeholder="$t('extractPlots.actorsPlaceholder')"
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
                  {{ $t('extractPlots.executeExtract') }}
                </el-button>
              </div>
            </div>

            <!-- Generate Highlight Parameters -->
            <div v-if="selectedOperation === 'generateHighlight'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !plotsResult" class="prerequisite-reminder">
                <el-alert
                  :title="$t('generateHighlight.prerequisite')"
                  type="warning"
                  :description="$t('generateHighlight.prerequisiteDesc')"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large">
                    <el-icon><Document /></el-icon>
                    {{ $t('generateHighlight.backToStep1') }}
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><User /></el-icon>
                  {{ $t('generateHighlight.highlightParams') }}
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item :label="$t('generateHighlight.starring')" class="form-item-enhanced">
                        <el-input
                          v-model="highlightStarring"
                          :placeholder="$t('generateHighlight.starringPlaceholder')"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Avatar /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="$t('generateHighlight.duration')" class="form-item-enhanced">
                        <el-input
                          v-model="highlightDuration"
                          :placeholder="$t('generateHighlight.durationPlaceholder')"
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
                  {{ $t('generateHighlight.executeGenerate') }}
                </el-button>
              </div>
            </div>

            <!-- Generate Narration Parameters -->
            <div v-if="selectedOperation === 'generateNarration'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !highlightVideoPath" class="prerequisite-reminder">
                <el-alert
                  :title="$t('generateNarration.prerequisite')"
                  type="warning"
                  :description="$t('generateNarration.prerequisiteDesc')"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large" v-if="!sessionId || !plotsResult">
                    <el-icon><Document /></el-icon>
                    {{ $t('generateHighlight.backToStep1') }}
                  </el-button>
                  <el-button type="success" @click="selectOperation('generateHighlight')" size="large" v-else>
                    <el-icon><VideoPlay /></el-icon>
                    {{ $t('generateNarration.backToStep2') }}
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><EditPen /></el-icon>
                  {{ $t('generateNarration.roleStyleSettings') }}
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item :label="$t('generateNarration.roleSet')" class="form-item-enhanced">
                        <el-input
                          v-model="roleSet"
                          type="textarea"
                          :rows="3"
                          :placeholder="$t('generateNarration.roleSetPlaceholder')"
                          size="large"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="$t('generateNarration.movieBg')" class="form-item-enhanced">
                        <el-input
                          v-model="narrationMovieBg"
                          type="textarea"
                          :rows="3"
                          :placeholder="$t('generateNarration.movieBgPlaceholder')"
                          size="large"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  
                  <el-row :gutter="24">
                    <el-col :span="12">
                      <el-form-item :label="$t('generateNarration.narrationStyle')" class="form-item-enhanced">
                        <el-input
                          v-model="narrationStyle"
                          :placeholder="$t('generateNarration.narrationStylePlaceholder')"
                          size="large"
                        >
                          <template #prefix>
                            <el-icon><Brush /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="$t('generateNarration.characterNickname')" class="form-item-enhanced">
                        <el-input
                          v-model="narrationCharacterNickname"
                          :placeholder="$t('generateNarration.characterNicknamePlaceholder')"
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
                      <el-form-item :label="$t('generateNarration.selectVoice')" class="form-item-enhanced">
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
                  {{ $t('generateNarration.executeNarration') }}
                </el-button>
              </div>
            </div>

            <!-- Generate Narration Video Parameters -->
            <div v-if="selectedOperation === 'generateNarrationVideo'" class="params-section">
              <!-- Prerequisite Check -->
              <div v-if="!sessionId || !highlightVideoPath || !narrationResult.length" class="prerequisite-reminder">
                <el-alert
                  :title="$t('generateNarrationVideo.prerequisite')"
                  type="warning"
                  :description="$t('generateNarrationVideo.prerequisiteDesc')"
                  show-icon
                  :closable="false"
                  class="reminder-alert"
                />
                <div class="reminder-actions">
                  <el-button type="primary" @click="selectOperation('extractPlots')" size="large" v-if="!sessionId || !plotsResult">
                    <el-icon><Document /></el-icon>
                    {{ $t('generateHighlight.backToStep1') }}
                  </el-button>
                  <el-button type="success" @click="selectOperation('generateHighlight')" size="large" v-else-if="!highlightVideoPath">
                    <el-icon><VideoPlay /></el-icon>
                    {{ $t('generateNarration.backToStep2') }}
                  </el-button>
                  <el-button type="warning" @click="selectOperation('generateNarration')" size="large" v-else>
                    <el-icon><Microphone /></el-icon>
                    {{ $t('generateNarrationVideo.backToStep3') }}
                  </el-button>
                </div>
              </div>

              <div v-else class="param-group">
                <h4 class="group-title">
                  <el-icon><Tools /></el-icon>
                  {{ $t('generateNarrationVideo.synthConfig') }}
                </h4>
                <div class="group-content">
                  <el-row :gutter="24">
                    <el-col :span="8">
                      <el-form-item :label="$t('generateNarration.selectVoice')" class="form-item-enhanced">
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
                      <el-form-item :label="$t('generateNarrationVideo.minimaxApiKey')" class="form-item-enhanced">
                        <el-input
                          v-model="minimaxApiKey"
                          :placeholder="$t('generateNarrationVideo.apiKeyPlaceholder')"
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
                      <el-form-item :label="$t('generateNarrationVideo.minimaxGroupId')" class="form-item-enhanced">
                        <el-input
                          v-model="minimaxGroupId"
                          :placeholder="$t('generateNarrationVideo.groupIdPlaceholder')"
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
                  {{ $t('generateNarrationVideo.executeSynth') }}
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
                <span class="section-title-simple">{{ $t('results.title') }}</span>
                <el-tag type="success" size="small">{{ $t('results.clickForDetails') }}</el-tag>
              </div>
            </template>

            <el-row :gutter="20" class="results-grid">
              <!-- Plot Results -->
              <el-col :xl="6" :lg="6" :md="12" :sm="24" :xs="24">
                <div class="result-item-card" :class="{ 'has-content': plotsResult }" @click="plotsResult && togglePlotsModal()">
                  <div class="result-item-header">
                    <el-icon class="result-item-icon"><Document /></el-icon>
                    <h4 class="result-item-title">{{ $t('results.plotExtraction') }}</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="plotsResult" class="result-summary">
                      <el-tag type="success" size="small">{{ $t('results.completed') }}</el-tag>
                      <el-button type="primary" link @click="togglePlotsModal()">{{ $t('results.clickForDetails2') }}</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="primary" @click.stop="selectOperationAndScroll('extractPlots')">
                          <el-icon><Refresh /></el-icon>
                          {{ $t('results.regenerate') }}
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>{{ $t('results.waiting.plots') }}</p>
                      <div class="action-buttons">
                        <el-button size="small" type="primary" @click.stop="selectOperationAndScroll('extractPlots')">
                          <el-icon><CaretRight /></el-icon>
                          {{ $t('results.generate') }}
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
                    <h4 class="result-item-title">{{ $t('results.highlightVideo') }}</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="highlightVideoPath" class="result-summary">
                      <el-tag type="success" size="small">{{ $t('results.completed') }}</el-tag>
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
                      <el-button type="primary" link @click="toggleHighlightVideoModal()">{{ $t('results.clickForVideo') }}</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="success" @click.stop="selectOperationAndScroll('generateHighlight')">
                          <el-icon><Refresh /></el-icon>
                          {{ $t('results.regenerate') }}
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>{{ $t('results.waiting.highlight') }}</p>
                      <div class="action-buttons">
                        <el-button size="small" type="success" @click.stop="selectOperationAndScroll('generateHighlight')">
                          <el-icon><CaretRight /></el-icon>
                          {{ $t('results.generate') }}
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
                    <h4 class="result-item-title">{{ $t('results.narrationContent') }}</h4>
                  </div>
                  <div class="result-item-content">
                    <div v-if="narrationResult.length" class="result-summary">
                      <el-tag type="success" size="small">{{ $t('results.completed') }}</el-tag>
                      <p class="summary-text">{{ $t('results.narrationCount', { count: narrationResult.length }) }}</p>
                      <div class="narration-preview">
                        <p class="preview-text">{{ narrationResult[0]?.narration?.substring(0, 50) }}...</p>
                      </div>
                      <el-button type="primary" link>{{ $t('results.clickForDetails2') }}</el-button>
                      <div class="action-buttons">
                        <el-button size="small" type="warning" @click.stop="selectOperationAndScroll('generateNarration')">
                          <el-icon><Refresh /></el-icon>
                          {{ $t('results.regenerate') }}
                        </el-button>
                      </div>
                    </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>{{ $t('results.waiting.narration') }}</p>
                      <div class="action-buttons">
                        <el-button size="small" type="warning" @click.stop="selectOperationAndScroll('generateNarration')">
                          <el-icon><CaretRight /></el-icon>
                          {{ $t('results.generate') }}
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
                    <h4 class="result-item-title">{{ $t('results.finalVideo') }}</h4>
                  </div>
                  <div class="result-item-content">
              <div v-if="finalVideoPath" class="result-summary">
                <el-tag type="success" size="small">{{ $t('results.completed') }}</el-tag>
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
                <el-button type="primary" link>{{ $t('results.clickForVideo') }}</el-button>
                <div class="action-buttons">
                  <el-button size="small" type="danger" @click.stop="selectOperationAndScroll('generateNarrationVideo')">
                    <el-icon><Refresh /></el-icon>
                    {{ $t('results.regenerate') }}
                  </el-button>
                </div>
              </div>
                    <div v-else class="result-placeholder">
                      <el-icon class="placeholder-icon"><Loading /></el-icon>
                      <p>{{ $t('results.waiting.final') }}</p>
                      <div class="action-buttons">
                        <el-button size="small" type="danger" @click.stop="selectOperationAndScroll('generateNarrationVideo')">
                          <el-icon><CaretRight /></el-icon>
                          {{ $t('results.generate') }}
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
        <el-dialog v-model="plotsModalVisible" :title="$t('modals.plotsResult')" width="80%" draggable>
          <div class="plots-modal-content">
            <el-collapse v-model="activePlotsCollapse">
              <el-collapse-item
                v-for="(plot, index) in plotsResult"
                :key="index"
                :title="$t('modals.segment', { index: index })"
                :name="index.toString()"
              >
                <div class="plot-text">{{ plot }}</div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-dialog>

        <!-- Highlight Video Modal -->
        <el-dialog v-model="highlightVideoModalVisible" :title="$t('modals.highlightVideo')" width="80%" draggable>
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
              {{ $t('modals.browserNotSupported') }}
            </video>
            <div class="video-modal-actions">
              <el-button type="primary" @click="downloadVideo('highlight')">
                <el-icon><Download /></el-icon>
                {{ $t('modals.downloadHighlight') }}
              </el-button>
            </div>
          </div>
        </el-dialog>

        <!-- Narration Detail Modal -->
        <el-dialog v-model="narrationModalVisible" :title="$t('modals.narrationContent')" width="80%" draggable>
          <div class="narration-modal-content">
            <el-table :data="narrationResult" stripe style="width: 100%" max-height="400">
              <el-table-column prop="timestamp" :label="$t('modals.timestamp')" width="150" />
              <el-table-column prop="narration_relative_time" :label="$t('modals.relativeTime')" width="120" />
              <el-table-column prop="narration" :label="$t('modals.narrationText')" />
            </el-table>
          </div>
        </el-dialog>

        <!-- Final Video Modal -->
        <el-dialog v-model="finalVideoModalVisible" :title="$t('modals.finalVideo')" width="80%" draggable>
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
              {{ $t('modals.browserNotSupported') }}
            </video>
            <div class="video-modal-actions">
              <el-button type="primary" @click="downloadVideo('narration')">
                <el-icon><Download /></el-icon>
                {{ $t('modals.downloadFinal') }}
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
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import {
  VideoCamera, Guide, Setting, Operation, Document, VideoPlay,
  Microphone, Film, Download, ChatLineRound, UploadFilled,
  Folder, Link, User, Avatar, Timer, EditPen, Brush, Tools, Key, Loading, CaretRight, Cpu, Refresh, InfoFilled
} from '@element-plus/icons-vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    VideoCamera, Guide, Setting, Operation, Document, VideoPlay,
    Microphone, Film, Download, ChatLineRound, UploadFilled,
    Folder, Link, User, Avatar, Timer, EditPen, Brush, Tools, Key, Cpu,
    LanguageSwitcher
  },
  setup() {
    const { t } = useI18n()
    
    // Reactive data
    const models = ref([])
    const voices = ref([])
    const selectedModel = ref('')
    const selectedOperation = ref('')
    const videoGcsLink = ref('gs://movie-clip/sample/yhhhs.1.mp4')
    const actorsInfo = ref(t('defaults.actorsInfo'))
    const highlightStarring = ref(t('defaults.highlightStarring'))
    const highlightDuration = ref(t('defaults.highlightDuration'))
    const roleSet = ref(t('defaults.roleSet'))
    const narrationStyle = ref(t('defaults.narrationStyle'))
    const narrationCharacterNickname = ref(t('defaults.narrationCharacterNickname'))
    const narrationMovieBg = ref(t('defaults.narrationMovieBg'))
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
        errorMessage.value = t('errors.fillRequired')
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
        errorMessage.value = t('errors.extractFirst')
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
        errorMessage.value = t('errors.generateHighlightFirst')
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
        errorMessage.value = t('errors.generateNarrationFirst')
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
      const { t } = useI18n()
      const titles = {
        extractPlots: t('steps.step1'),
        generateHighlight: t('steps.step2'),
        generateNarration: t('steps.step3'),
        generateNarrationVideo: t('steps.step4')
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
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 30%, #000000 100%);
  position: relative;
  overflow-x: hidden;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.app-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 50%, rgba(220, 38, 38, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 215, 0, 0.06) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(184, 134, 11, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.app-container > * {
  position: relative;
  z-index: 1;
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
  justify-content: space-between;
  width: 100%;
}

.title-actions {
  margin-left: 20px;
}

.main-title {
  margin: 0;
  font-size: 42px;
  font-weight: 500;
  color: #ffffff;
  line-height: 1.2;
  letter-spacing: 2px;
  text-align: left;
  font-family: 'Noto Serif SC', 'SimSun', '宋体', serif;
  background: linear-gradient(135deg, #dc2626 0%, #ffd700 25%, #ffffff 50%, #ffd700 75%, #dc2626 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 
    0 0 10px rgba(220, 38, 38, 0.3),
    0 0 20px rgba(255, 215, 0, 0.2),
    2px 2px 4px rgba(0, 0, 0, 0.3);
  position: relative;
  text-transform: none;
  animation: titleGlow 4s ease-in-out infinite alternate;
  filter: contrast(1.2) brightness(1.1);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.main-title::before {
  content: '';
  position: absolute;
  top: -5px;
  left: -10px;
  right: -10px;
  bottom: -5px;
  background: linear-gradient(45deg, 
    rgba(255, 215, 0, 0.1) 0%, 
    rgba(255, 140, 0, 0.1) 25%,
    rgba(220, 20, 60, 0.1) 50%,
    rgba(138, 43, 226, 0.1) 75%,
    rgba(255, 215, 0, 0.1) 100%);
  border-radius: 8px;
  filter: blur(10px);
  z-index: -1;
  opacity: 0.6;
  animation: auraBreathe 3s ease-in-out infinite alternate;
}

.main-title::after {
  content: '🎬';
  position: absolute;
  left: -60px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 28px;
  opacity: 0.8;
  animation: filmIconRotate 8s linear infinite;
}

@keyframes titleGlow {
  0% {
    text-shadow: 
      0 0 10px rgba(255, 255, 255, 0.3),
      0 0 20px rgba(255, 215, 0, 0.2),
      0 0 30px rgba(255, 140, 0, 0.1);
  }
  100% {
    text-shadow: 
      0 0 20px rgba(255, 255, 255, 0.5),
      0 0 30px rgba(255, 215, 0, 0.3),
      0 0 40px rgba(220, 20, 60, 0.2),
      0 0 50px rgba(138, 43, 226, 0.1);
  }
}

@keyframes auraBreathe {
  0% {
    opacity: 0.4;
    transform: scale(0.98);
  }
  100% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}

@keyframes filmIconRotate {
  0% {
    transform: translateY(-50%) rotate(0deg);
    opacity: 0.6;
  }
  25% {
    opacity: 0.9;
  }
  50% {
    transform: translateY(-50%) rotate(180deg);
    opacity: 0.7;
  }
  75% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-50%) rotate(360deg);
    opacity: 0.6;
  }
}

/* Enhanced title for art academy style */
.main-title.art-academy {
  font-family: 'Cormorant Garamond', 'Playfair Display', 'Times New Roman', serif;
  font-weight: 400;
  font-style: italic;
  background: linear-gradient(135deg, 
    #ffd700 0%, 
    #ffffff 25%, 
    #f8f9fa 50%, 
    #e9ecef 75%, 
    #ffd700 100%);
  background-clip: text;
  -webkit-background-clip: text;
  position: relative;
}

.main-title.art-academy::before {
  background: linear-gradient(45deg, 
    rgba(212, 175, 55, 0.15) 0%, 
    rgba(255, 215, 0, 0.15) 25%,
    rgba(184, 134, 11, 0.15) 50%,
    rgba(146, 64, 14, 0.15) 75%,
    rgba(212, 175, 55, 0.15) 100%);
}

.main-title.shanghai-studio {
  font-family: 'Noto Serif SC', 'SimSun', serif;
  font-weight: 500;
  background: linear-gradient(135deg, 
    #dc2626 0%, 
    #ffffff 30%, 
    #f8f9fa 60%, 
    #dc2626 100%);
  background-clip: text;
  -webkit-background-clip: text;
  border-bottom: 3px solid rgba(220, 38, 38, 0.3);
  padding-bottom: 8px;
}

.main-title.shanghai-studio::before {
  background: linear-gradient(45deg, 
    rgba(220, 38, 38, 0.1) 0%, 
    rgba(255, 0, 0, 0.1) 25%,
    rgba(139, 0, 0, 0.1) 50%,
    rgba(220, 38, 38, 0.1) 100%);
}

.main-title.shanghai-studio::after {
  content: '🎭';
  left: -55px;
  animation: theaterMaskFloat 6s ease-in-out infinite alternate;
}

@keyframes theaterMaskFloat {
  0% {
    transform: translateY(-50%) translateX(0) rotate(-5deg);
  }
  100% {
    transform: translateY(-60%) translateX(5px) rotate(5deg);
  }
}

.model-info-inline {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin-left: 12px;
  padding: 4px 12px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
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
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid rgba(120, 119, 198, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(20px);
}

/* Operations card - remove card styling */
.operations-card {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.section-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(120, 119, 198, 0.5), transparent);
}

.section-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  border-color: rgba(120, 119, 198, 0.4);
}

/* Unified header styles */
.section-header-unified {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: #000000;
  padding: 16px 20px;
  color: #ffffff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  text-rendering: optimizeLegibility;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title-main {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.5px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.section-subtitle {
  font-size: 13px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.7);
  margin-left: 8px;
  font-style: italic;
}

.section-icon {
  font-size: 20px;
  color: rgba(120, 219, 255, 0.9);
}

.section-header-simple {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-weight: 600;
  font-size: 16px;
  color: #ffffff;
  text-shadow: none;
  padding: 8px 0;
  background: none;
  border: none;
}

.section-title-simple {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
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
  font-weight: 600;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
  backdrop-filter: blur(10px);
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  letter-spacing: 0.8px;
  text-align: center;
  padding: 8px 12px;
  line-height: 1.2;
  white-space: normal;
  word-wrap: break-word;
  hyphens: auto;
}

/* Enhanced responsive text sizing for different languages */
.operation-btn {
  font-size: clamp(13px, 2.5vw, 16px);
}

/* Specific adjustments for longer English text */
@media (max-width: 1400px) {
  .operation-btn {
    font-size: clamp(12px, 2.2vw, 14px);
    padding: 10px 8px;
    height: 76px;
  }
}

@media (max-width: 1200px) {
  .operation-btn {
    font-size: clamp(11px, 2vw, 13px);
    height: 80px;
    padding: 12px 6px;
  }
}

@media (max-width: 992px) {
  .operation-btn {
    font-size: clamp(10px, 1.8vw, 12px);
    height: 84px;
    padding: 14px 4px;
  }
}

/* Language-specific adjustments using CSS attribute selectors */
[lang="en"] .operation-btn {
  font-size: clamp(11px, 2.2vw, 14px);
  letter-spacing: 0.3px;
  line-height: 1.1;
}

[lang="zh"] .operation-btn {
  font-size: clamp(13px, 2.5vw, 16px);
  letter-spacing: 0.8px;
  line-height: 1.2;
}

/* Dynamic height adjustment for text overflow */
.operation-btn span {
  display: block;
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
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
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #2196f3;
  color: #1565c0;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
}

.operation-btn.step1:hover:not(:disabled) {
  background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
  border-color: #1976d2;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(33, 150, 243, 0.3);
}

.operation-btn.step2 {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  border: 1px solid #4caf50;
  color: #2e7d32;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
}

.operation-btn.step2:hover:not(:disabled) {
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
  border-color: #388e3c;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.3);
}

.operation-btn.step3 {
  background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
  border: 1px solid #ff9800;
  color: #ef6c00;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
}

.operation-btn.step3:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffcc02 0%, #ffb300 100%);
  border-color: #f57c00;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 152, 0, 0.3);
}

.operation-btn.step4 {
  background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
  border: 1px solid #e91e63;
  color: #ad1457;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.2);
}

.operation-btn.step4:hover:not(:disabled) {
  background: linear-gradient(135deg, #f8bbd9 0%, #f48fb1 100%);
  border-color: #c2185b;
  transform: translateY(-2px);
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
  background: #007bff !important;
  color: white !important;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
  border-color: #007bff;
}

.operation-btn.step2.selected {
  background: #007bff !important;
  color: white !important;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
  border-color: #007bff;
}

.operation-btn.step3.selected {
  background: #007bff !important;
  color: white !important;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
  border-color: #007bff;
}

.operation-btn.step4.selected {
  background: #007bff !important;
  color: white !important;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
  border-color: #007bff;
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
  background: #f8f9fa;
  color: #495057;
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.operation-params .params-section {
  background: #ffffff;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.operation-params .params-section:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

/* Execute section styling */
.execute-section {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  text-align: center;
  transition: all 0.3s ease;
}

.execute-section:hover {
  background: #e9ecef;
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
  background: #1a1a1a;
  border-radius: 8px;
  margin-top: 16px;
  border: 1px solid #2a2a2a;
  backdrop-filter: blur(15px);
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
  color: #2c3e50;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border-left: 4px solid #dc2626;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: 0.3px;
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
  color: #495057;
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
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}


.results-grid {
  padding: 24px;
}

.result-item-card {
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  height: 280px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
}

.result-item-card.has-content {
  border-color: #007bff;
  background: #f8f9fa;
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
  font-size: 20px;
  color: #6c757d;
  transition: all 0.3s ease;
}

.result-item-card.has-content .result-item-icon {
  color: #007bff;
}

.result-item-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #495057;
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
  color: #6c757d;
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
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
  border-left: 3px solid #007bff;
}

.preview-text {
  margin: 0;
  font-size: 13px;
  color: #6c757d;
  font-style: italic;
  line-height: 1.4;
}

.result-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #6b7280;
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

/* GCS Hint Styles */
.gcs-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.gcs-hint .el-text {
  font-size: 12px !important;
  color: #64748b !important;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 6px;
}

.gcs-hint .el-icon {
  font-size: 14px;
  color: #3b82f6;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .gcs-hint {
    padding: 6px 10px;
    margin-top: 6px;
  }
  
  .gcs-hint .el-text {
    font-size: 11px !important;
  }
  
  .gcs-hint .el-icon {
    font-size: 12px;
  }
}
</style>
