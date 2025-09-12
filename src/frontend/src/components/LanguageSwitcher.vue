<template>
  <div class="language-switcher">
    <el-dropdown @command="handleLanguageChange" trigger="click">
      <el-button type="primary" link class="language-btn">
        <span class="globe-icon">🌐</span>
        <span class="current-lang">{{ getCurrentLanguageName() }}</span>
        <el-icon class="arrow"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="zh" :class="{ 'is-active': currentLocale === 'zh' }">
            🇨🇳 {{ $t('language.chinese') }}
          </el-dropdown-item>
          <el-dropdown-item command="en" :class="{ 'is-active': currentLocale === 'en' }">
            🇺🇸 {{ $t('language.english') }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'LanguageSwitcher',
  components: {
    ArrowDown
  },
  setup() {
    const { locale, t } = useI18n()
    
    const currentLocale = computed(() => locale.value)
    
    const getCurrentLanguageName = () => {
      return locale.value === 'zh' ? '中文' : 'English'
    }
    
    const handleLanguageChange = (command) => {
      if (command !== locale.value) {
        locale.value = command
        localStorage.setItem('movieclip-locale', command)
        
        // 显示切换成功提示
        ElMessage({
          message: t('language.switch') + ': ' + (command === 'zh' ? '中文' : 'English'),
          type: 'success',
          duration: 2000
        })
      }
    }
    
    return {
      currentLocale,
      getCurrentLanguageName,
      handleLanguageChange
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: inline-block;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.language-btn:hover {
  color: #409eff;
  background: rgba(255, 255, 255, 0.95);
  border-color: #409eff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.globe-icon {
  font-size: 16px;
  display: flex;
  align-items: center;
}

.current-lang {
  font-size: 13px;
  font-weight: 600;
}

.arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
}

:deep(.el-dropdown-menu) {
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.el-dropdown-menu__item) {
  border-radius: 6px;
  margin: 2px 0;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f0f9ff;
  color: #409eff;
}

:deep(.el-dropdown-menu__item.is-active) {
  background: #409eff;
  color: white;
  font-weight: 600;
}

:deep(.el-dropdown-menu__item.is-active:hover) {
  background: #337ecc;
}

@media (max-width: 768px) {
  .language-btn {
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .current-lang {
    font-size: 12px;
  }
  
  :deep(.el-dropdown-menu__item) {
    font-size: 13px;
  }
}
</style>
