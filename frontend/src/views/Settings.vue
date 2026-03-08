<template>
  <div>
    <div class="page-header">
      <h2>系统设置</h2>
      <p>配置轮询频率、API Token 与通知渠道</p>
    </div>

    <el-tabs v-model="activeTab" type="border-card" style="background:var(--bg-card); border-color:var(--border); border-radius:var(--radius)">
      <!-- ── 轮询配置 ── -->
      <el-tab-pane label="轮询设置" name="polling">
        <div style="max-width:520px; padding:12px 0">
          <el-form :model="config" label-width="130px" label-position="left">
            <el-form-item label="启用定时检查">
              <el-switch v-model="config.scheduler_enabled" />
            </el-form-item>
            <el-form-item label="轮询间隔（秒）">
              <el-input-number
                v-model="config.poll_interval_seconds"
                :min="60"
                :max="86400"
                :step="60"
                style="width:200px"
              />
              <span style="margin-left:12px; font-size:12px; color:var(--text-muted)">
                ≈ {{ (config.poll_interval_seconds / 60).toFixed(0) }} 分钟
              </span>
            </el-form-item>
            <el-form-item label="GitHub Token">
              <el-input
                v-model="config.github_token"
                placeholder="可选，提高 API 请求限额"
                show-password
              />
            </el-form-item>
            <el-form-item label="Gitee Token">
              <el-input
                v-model="config.gitee_token"
                placeholder="可选，提高 API 请求限额"
                show-password
              />
            </el-form-item>
          </el-form>
          <div style="text-align:right; margin-top:16px">
            <el-button type="primary" :loading="saving" @click="handleSave">
              保存配置
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ── 飞书通知 ── -->
      <el-tab-pane label="飞书通知" name="feishu">
        <div style="max-width:520px; padding:12px 0">
          <el-form :model="config" label-width="130px" label-position="left">
            <el-form-item label="启用飞书通知">
              <el-switch v-model="config.feishu_enabled" />
            </el-form-item>
            <el-form-item label="Webhook URL">
              <el-input
                v-model="config.feishu_webhook_url"
                placeholder="飞书群机器人 Webhook 地址"
              />
            </el-form-item>
            <el-form-item label="Secret（可选）">
              <el-input
                v-model="config.feishu_secret"
                placeholder="留空则不签名"
                show-password
              />
            </el-form-item>
          </el-form>
          <div style="text-align:right; margin-top:16px">
            <el-button type="primary" :loading="saving" @click="handleSave">
              保存配置
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ── 邮箱通知 ── -->
      <el-tab-pane label="邮箱通知" name="email">
        <div style="max-width:560px; padding:12px 0">
          <el-form :model="config" label-width="130px" label-position="left">
            <el-form-item label="启用邮箱通知">
              <el-switch v-model="config.email_enabled" />
            </el-form-item>
            <el-form-item label="SMTP 服务器">
              <el-input v-model="config.smtp_host" placeholder="如 smtp.qq.com" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="config.smtp_port" :min="1" :max="65535" style="width:150px" />
            </el-form-item>
            <el-form-item label="使用 TLS">
              <el-switch v-model="config.smtp_use_tls" />
            </el-form-item>
            <el-form-item label="账号">
              <el-input v-model="config.smtp_user" placeholder="SMTP 登录账号" />
            </el-form-item>
            <el-form-item label="密码 / 授权码">
              <el-input
                v-model="config.smtp_password"
                placeholder="留空则不修改"
                show-password
              />
            </el-form-item>
            <el-form-item label="发件人">
              <el-input v-model="config.from_addr" placeholder="发件人邮箱地址" />
            </el-form-item>
            <el-form-item label="收件人">
              <el-input
                v-model="toAddrsStr"
                placeholder="多个收件人用英文逗号分隔"
              />
              <div style="font-size:11px; color:var(--text-muted); margin-top:4px">
                多个邮箱用 , 分隔，如 a@qq.com,b@163.com
              </div>
            </el-form-item>
          </el-form>
          <div style="text-align:right; margin-top:16px">
            <el-button type="primary" :loading="saving" @click="handleSave">
              保存配置
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getConfig, updateConfig } from '../api/config'
import { ElMessage } from 'element-plus'

const activeTab = ref('polling')
const saving = ref(false)

const config = ref({
  poll_interval_seconds: 600,
  scheduler_enabled: true,
  github_token: '',
  gitee_token: '',
  feishu_enabled: false,
  feishu_webhook_url: '',
  feishu_secret: '',
  email_enabled: false,
  smtp_host: '',
  smtp_port: 465,
  smtp_user: '',
  smtp_password: '',
  smtp_use_tls: true,
  from_addr: '',
  to_addrs: [],
})

const toAddrsStr = computed({
  get: () => (config.value.to_addrs || []).join(','),
  set: (val) => {
    config.value.to_addrs = val.split(',').map(s => s.trim()).filter(Boolean)
  },
})

async function loadConfig() {
  try {
    const data = await getConfig()
    config.value = { ...config.value, ...data }
  } catch (e) {
    ElMessage.error('加载配置失败: ' + e.message)
  }
}

async function handleSave() {
  saving.value = true
  try {
    const data = await updateConfig(config.value)
    config.value = { ...config.value, ...data }
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>
